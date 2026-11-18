from localization import tr
import os
import re
import subprocess
from typing import Dict
try:
    import pefile
except Exception:
    pefile = None
ANSI_RE = re.compile('\\x1b\\[[0-9;]*m')

def strip_ansi(s: str) -> str:
    return ANSI_RE.sub('', s or '')

def detect_binary_format(path: str) -> str:
    try:
        with open(path, 'rb') as f:
            hdr = f.read(4)
        if hdr == b'\x7fELF':
            return 'ELF'
        if hdr[:2] == b'MZ':
            return 'PE'
    except Exception:
        pass
    return 'OTHER'

def run_pe_mitigations(binary_path: str) -> str:
    if pefile is None:
        return tr("[pe-check]\nKon 'pefile' niet importeren. Installeer met: pip install pefile\n")
    try:
        pe = pefile.PE(binary_path, fast_load=False)
        dll_chars = int(getattr(pe.OPTIONAL_HEADER, 'DllCharacteristics', 0))
        machine = hex(int(getattr(pe.FILE_HEADER, 'Machine', 0)))
        subsystem = int(getattr(pe.OPTIONAL_HEADER, 'Subsystem', 0))
        image_base = hex(int(getattr(pe.OPTIONAL_HEADER, 'ImageBase', 0)))
        DYNAMIC_BASE = 64
        NX_COMPAT = 256
        NO_SEH = 1024
        TERMINAL_SRV_AWARE = 32768
        HIGH_ENTROPY_VA = 32
        GUARD_CF = 16384
        FORCE_INTEGRITY = 128

        def yn(flag: int) -> str:
            return 'Yes' if dll_chars & flag else 'No'
        safe_seh = 'N/A'
        try:
            if hasattr(pe, 'DIRECTORY_ENTRY_LOAD_CONFIG') and pe.DIRECTORY_ENTRY_LOAD_CONFIG:
                lc = pe.DIRECTORY_ENTRY_LOAD_CONFIG.struct
                safe_seh = 'Yes' if getattr(lc, 'SEHandlerCount', 0) and getattr(lc, 'SEHandlerTable', 0) else 'No'
        except Exception:
            pass
        cfg = yn(GUARD_CF)
        try:
            if hasattr(pe, 'DIRECTORY_ENTRY_LOAD_CONFIG') and pe.DIRECTORY_ENTRY_LOAD_CONFIG:
                lc = pe.DIRECTORY_ENTRY_LOAD_CONFIG.struct
                if getattr(lc, 'GuardFlags', 0):
                    cfg = 'Yes'
        except Exception:
            pass
        out = []
        out.append('[pe-check] Windows PE mitigation report (training)')
        out.append(f"{tr('File: ')}" + f'{binary_path}')
        out.append('Machine: ' + f'{machine}' + '  Subsystem: ' + f'{subsystem}' + '  ImageBase: ' + f'{image_base}')
        out.append('')
        out.append('Mitigation                      Enabled')
        out.append('-------------------------------- --------')
        out.append('ASLR (DYNAMIC_BASE)             ' + f'{yn(DYNAMIC_BASE)}')
        out.append('High Entropy VA                 ' + f'{yn(HIGH_ENTROPY_VA)}')
        out.append('DEP (NX_COMPAT)                 ' + f'{yn(NX_COMPAT)}')
        out.append('Control Flow Guard (CFG)        ' + f'{cfg}')
        out.append('Force Integrity                 ' + f'{yn(FORCE_INTEGRITY)}')
        out.append('SEH Disabled (NO_SEH)           ' + f'{yn(NO_SEH)}')
        out.append('SafeSEH                         ' + f'{safe_seh}')
        out.append('Terminal Server Aware           ' + f'{yn(TERMINAL_SRV_AWARE)}')
        return '\n'.join(out) + '\n'
    except Exception as e:
        return f"{tr('[pe-check fout]\nKon PE niet lezen: ')}" + f'{e}' + '\n'

def run_checksec(binary_path: str) -> str:
    try:
        if detect_binary_format(binary_path) == 'PE':
            return run_pe_mitigations(binary_path)
    except Exception:
        pass
    candidates = [['checksec', '--file=' + f'{binary_path}'], ['checksec', '--file', binary_path], ['checksec', binary_path]]
    last_error = ''
    for cmd in candidates:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=30, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            out = strip_ansi((result.stdout or '') + ('\n' + result.stderr if result.stderr else ''))
            if 'RELRO' in out and 'STACK' in out and ('NX' in out):
                return out
            if 'Error:' not in out and 'Unknown option' not in out and ('No option selected' not in out):
                return out
            last_error = out
        except FileNotFoundError:
            return tr("[checksec fout]\nHet commando 'checksec' is niet gevonden in PATH.\n")
        except subprocess.CalledProcessError as e:
            last_error = strip_ansi((e.stdout or '') + ('\n' + e.stderr if e.stderr else ''))
    return f"{tr('[checksec fout]\n')}" + f'{last_error}' + '\n'

def run_ropper(binary_path: str) -> str:
    try:
        result = subprocess.run(['ropper', '-f', binary_path, '--all', '--nocolor'], capture_output=True, text=True, check=False, timeout=60, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    except FileNotFoundError:
        return tr("[ropper fout]\nHet commando 'ropper' is niet gevonden.\n")
    out = strip_ansi(result.stdout or '')
    err = strip_ansi(result.stderr or '')
    if err.strip():
        out = (out.rstrip() + '\n\n[ropper stderr]\n' + err).strip()
    return out if out.strip() else tr('[ropper fout]\nGeen output ontvangen van ropper.\n')

def summarize_rop_output(rop_text: str) -> str:
    lines = rop_text.splitlines()
    gadget_lines = [ln for ln in lines if ln.strip().startswith('0x')]
    totaal = len(gadget_lines)
    if totaal == 0:
        return tr('Aantal gevonden gadgets: 0\nOpmerking: ropper gaf geen bruikbare gadgetregels terug.')
    voorbeelden = '\n    '.join(gadget_lines[:min(5, totaal)])
    return f"{tr('Aantal gevonden gadgets (ruwe telling): ')}" + f'{totaal}' + f"{tr('\nVoorbeeldgadgets:\n    ')}" + f'{voorbeelden}'

def score_rop_text(rop_text: str) -> Dict[str, int]:
    lines = [ln.strip().lower() for ln in rop_text.splitlines() if ln.strip().startswith('0x')]
    ret_count = sum((1 for ln in lines if ' ret' in ln or ln.endswith('ret')))
    jmp_count = sum((1 for ln in lines if ' jmp' in ln))
    call_count = sum((1 for ln in lines if ' call' in ln))
    popret_count = sum((1 for ln in lines if 'pop' in ln and 'ret' in ln))
    raw = min(len(lines), 50) + min(jmp_count * 5, 20) + min(call_count * 5, 20) + min(popret_count * 4, 20)
    return {'ret_count': ret_count, 'jmp_count': jmp_count, 'call_count': call_count, 'popret_count': popret_count, 'score': min(raw, 100)}
