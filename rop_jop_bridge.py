
from typing import Dict, List
from rop_jop_core import detect_binary_format, run_checksec, run_ropper, summarize_rop_output, score_rop_text

def filter_rop_lines(rop_text: str, pattern: str) -> str:
    if not pattern.strip():
        return rop_text
    lines = rop_text.splitlines()
    filtered: List[str] = []
    filter_lc = pattern.lower().strip()
    saw_gadget = False
    kept = 0
    for ln in lines:
        if ln.strip().startswith("0x"):
            saw_gadget = True
            if filter_lc in ln.lower():
                filtered.append(ln)
                kept += 1
        else:
            if not saw_gadget:
                filtered.append(ln)
    if kept == 0:
        filtered.append(f"[No gadgets found that '{pattern}' contain]")
    return "\n".join(filtered)

def explain_gadget_line(line: str) -> str:
    if not line or not line.strip().startswith("0x"):
        return "Selecteer een gadgetregel die met 0x begint."
    try:
        addr_part, instr_part = line.split(":", 1)
    except ValueError:
        addr_part, instr_part = line, ""
    raw_instructions = [i.strip() for i in instr_part.split(";") if i.strip()]
    if not raw_instructions:
        return f"Adres: {addr_part.strip()}\nGeen instructies gevonden."
    out = [f"Adres: {addr_part.strip()}", "", "Didactische uitleg per stap:"]
    for idx, instr in enumerate(raw_instructions, start=1):
        low = instr.lower()
        if low.startswith("pop"):
            msg = "Laadt een waarde van de stack in een register."
        elif low.startswith("mov"):
            msg = "Verplaatst data van bron naar doel."
        elif low.startswith("xor"):
            msg = "Bitwise XOR; vaak gebruikt om een register op nul te zetten."
        elif low.startswith("add"):
            msg = "Telt waarden op."
        elif low.startswith("sub"):
            msg = "Trekt waarden af."
        elif low.startswith("lea"):
            msg = "Berekent een adres zonder geheugeninhoud direct te lezen."
        elif low.startswith("push"):
            msg = "Zet een waarde op de stack."
        elif low.startswith("ret"):
            msg = "Keert terug via de stack; klassiek relevant voor ROP."
        elif low.startswith("jmp"):
            msg = "Maakt een sprong; indirecte varianten zijn interessant voor JOP."
        elif low.startswith("call"):
            msg = "Roept een functie of doel aan; indirecte call-patronen zijn interessant."
        else:
            msg = "Algemene instructie."
        out.append(f"{idx}. {instr}\n   -> {msg}")
    return "\n".join(out)

def analyze_for_editor(binary_path: str) -> Dict[str, object]:
    binary_type = detect_binary_format(binary_path)
    checksec_text = run_checksec(binary_path)
    rop_raw = run_ropper(binary_path)
    rop_summary = summarize_rop_output(rop_raw)
    rop_score = score_rop_text(rop_raw)
    return {
        "binary_path": binary_path,
        "binary_type": binary_type,
        "checksec_text": checksec_text,
        "rop_raw": rop_raw,
        "rop_summary": rop_summary,
        "rop_score": rop_score,
    }
