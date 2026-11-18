from localization import tr
import localization
from help_windows import show_help, show_about
from updater import check_for_updates
import json
import sys
from pathlib import Path
import os
import re
import shutil
import subprocess
import tempfile
import threading
import tkinter as tk
from dataclasses import dataclass, field
from queue import Empty, Queue
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText
from typing import Dict, List, Optional, Set, Tuple
from assembly_editor_menu_v5_4 import install_menus
from rop_jop_bridge import analyze_for_editor, filter_rop_lines, explain_gadget_line

@dataclass
class ExampleProgram:
    name: str
    category: str
    content: str
    guide: str
    expected_output: str
    error_lines: Set[int]
    focus_lines: Dict[int, str]
    input_hint: str = ''
    demo_inputs: List[str] = field(default_factory=list)
VERSION = '5.5.9'

class AssemblyEditorV555(tk.Tk):
    version = VERSION
    show_help = show_help
    show_about = show_about
    check_for_updates = check_for_updates

    def change_language(self, value):
        if self.task_busy or self.runtime_active:
            self.language_var.set(self.language)
            messagebox.showinfo(tr('Taal'), tr('Taal wijzigen kan zodra de huidige taak en het programma gestopt zijn.'), parent=self)
            return
        self.language = value
        localization.set_language(value)
        self.language_var.set(value)

        def refresh(widget):
            if isinstance(widget, tk.Menu):
                return
            try:
                if 'text' in widget.keys():
                    widget.configure(text=tr(str(widget.cget('text'))))
                if isinstance(widget, (ttk.Label, tk.Label)) and widget.cget('textvariable'):
                    var = widget.cget('textvariable')
                    widget.setvar(var, tr(str(widget.getvar(var))))
            except tk.TclError:
                pass
            if isinstance(widget, tk.Toplevel):
                widget.title(tr(widget.title()))
            for child in widget.winfo_children():
                refresh(child)
        refresh(self)
        old_menu = self.nametowidget(self.cget('menu'))
        install_menus(self)
        old_menu.destroy()
        for box in (self.help_box, self.lesson_box):
            current = box.get('1.0', 'end-1c')
            box.configure(state='normal')
            box.delete('1.0', tk.END)
            box.insert('1.0', tr(current))
            box.configure(state='disabled')
        self.register_help = {key: tr(value) for key, value in self.register_help.items()}
        for name, example in self.examples.items():
            for field in ('category', 'guide', 'expected_output', 'input_hint'):
                setattr(example, field, tr(getattr(example, field)))
        self.check_dependencies(startup=True)
        self.on_text_changed()
        for child in self.winfo_children():
            if hasattr(child, 'refresh_language'):
                child.refresh_language()
        try:
            self._save_settings()
        except OSError as exc:
            messagebox.showerror(tr('Taal'), tr('Taalvoorkeur kon niet worden opgeslagen:') + str(exc), parent=self)

    def __init__(self) -> None:
        super().__init__()
        self.title('Assembly GUI Editor ' + VERSION)
        icon_path = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent)) / 'assets' / 'assembly-editor.ico'
        if icon_path.is_file():
            self.iconbitmap(default=str(icon_path))
        self.geometry('1780x1100')
        self.minsize(1380, 880)
        self.protocol('WM_DELETE_WINDOW', self._on_close)
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        config = Path(os.environ.get('APPDATA', str(Path.home() / '.config'))) / 'AssemblyEditor'
        self.settings_file = str(config / 'settings.json')
        self.language = 'nl'
        self.language_var = tk.StringVar(value='nl')
        self.clean_text = ''
        self.task_busy = False
        self.closing = False
        self.built_source = None
        self.built_target = None
        self.current_file: Optional[str] = None
        self.current_example_name: Optional[str] = None
        self.last_binary: Optional[str] = None
        self.last_obj: Optional[str] = None
        self.temp_dir: Optional[str] = None
        self.last_build_mode: str = 'auto'
        self.compiler_path = 'nasm.exe' if os.name == 'nt' else 'nasm'
        self.linker_path = 'gcc.exe' if os.name == 'nt' else 'gcc'
        self.objdump_path = 'objdump.exe' if os.name == 'nt' else 'objdump'
        self.target_mode = tk.StringVar(value='windows_x64' if os.name == 'nt' else 'linux_x64')
        self.student_mode = tk.BooleanVar(value=True)
        self.ui_font_family = 'Consolas'
        self.ui_font_size = 12
        self.console_input_var = tk.StringVar()
        self.runtime_process: Optional[subprocess.Popen] = None
        self.runtime_queue: Queue[Tuple[str, str]] = Queue()
        self.runtime_active = False
        self.instructions = {'mov', 'lea', 'cmp', 'jmp', 'je', 'jne', 'jg', 'jl', 'jge', 'jle', 'call', 'ret', 'push', 'pop', 'xor', 'add', 'sub', 'and', 'or', 'test', 'inc', 'dec', 'shl', 'shr', 'syscall', 'nop', 'imul', 'mul'}
        self.two_operand_instructions = {'mov', 'lea', 'cmp', 'add', 'sub', 'xor', 'and', 'or', 'test', 'imul'}
        self.registers = {'rax', 'rbx', 'rcx', 'rdx', 'rsi', 'rdi', 'rsp', 'rbp', 'r8', 'r9', 'eax', 'ebx', 'ecx', 'edx'}
        self.directives = {'section', 'global', 'extern', 'db', 'dw', 'dd', 'dq', 'equ', 'bits', 'default', 'resb', 'resd'}
        self.register_help = {'rax': tr('RAX: accumulator, return value, vaak ook tijdelijke werkruimte.'), 'rbx': tr('RBX: algemeen register, vaak gebruikt voor tussenresultaten.'), 'rcx': tr('RCX: op Windows x64 meestal het eerste argumentregister.'), 'rdx': tr('RDX: op Windows x64 meestal het tweede argumentregister.'), 'rsp': 'RSP: stack pointer.', 'rbp': 'RBP: frame/base pointer.'}
        self.snippets = {'mov': 'mov rax, 1', 'call': 'call printf', 'section': 'section .text', 'global': 'global main'}
        self.examples = self._make_examples()
        self.example_names = list(self.examples.keys())
        self.compiler_path = self._discover_tool('nasm')
        self.linker_path = self._discover_tool('gcc')
        self.objdump_path = self._discover_tool('objdump')
        self._load_settings()
        localization.set_language(self.language)
        self.language_var.set(self.language)
        self.examples = self._make_examples()
        self.register_help = {key: tr(value) for key, value in self.register_help.items()}
        self._build_ui()
        install_menus(self)
        self.bind('<F1>', lambda event: self.show_help())
        self.bind('<Control-n>', lambda event: self.new_file())
        self.bind('<Control-o>', lambda event: self.open_file())
        self.bind('<Control-s>', lambda event: self.save_file())
        self.bind('<Control-Shift-S>', lambda event: self.save_file_as())
        self._load_default_example()
        self.on_text_changed()
        self.check_dependencies(startup=True)
        self.after(120, self._sync_line_numbers_periodic)
        self.after(120, self._poll_runtime_queue)

    def _make_examples(self) -> Dict[str, ExampleProgram]:
        examples = [ExampleProgram(name='01_windows_hello.asm', category='Windows Native Basics', content='default rel\nglobal main\nextern printf\n\nsection .data\nmsg db "Hallo vanuit Windows assembly!", 10, 0\n\nsection .text\nmain:\n    sub rsp, 40\n    lea rcx, [rel msg]\n    call printf\n    xor eax, eax\n    add rsp, 40\n    ret\n', guide=tr('Leerdoel: native Windows x64 met main en printf.'), expected_output='Hallo vanuit Windows assembly!', error_lines=set(), focus_lines={9: tr('Stackruimte voor externe call.'), 10: tr('Adres van msg gaat RIP-relatief naar RCX.')}, input_hint=tr('Geen invoer nodig. Klik op Run en bekijk alleen de output.')), ExampleProgram(name='02_gui_messagebox_hello.asm', category='Windows GUI Basics', content='default rel\nglobal WinMain\nextern MessageBoxA\nextern ExitProcess\n\nsection .data\ntitle db "GUI voorbeeld", 0\nmsg db "Hallo vanuit een grafisch assemblyprogramma!", 0\n\nsection .text\nWinMain:\n    sub rsp, 40\n    xor rcx, rcx\n    lea rdx, [rel msg]\n    lea r8, [rel title]\n    xor r9d, r9d\n    call MessageBoxA\n    xor ecx, ecx\n    call ExitProcess\n', guide=tr('Leerdoel: eerste Windows GUI voorbeeld met MessageBoxA.'), expected_output=tr('Een grafisch berichtvenster.'), error_lines=set(), focus_lines={10: tr('RDX wijst naar de boodschap.'), 11: tr('R8 wijst naar de venstertitel.')}, input_hint=tr('Geen console-invoer nodig. Run opent direct een grafisch venster.'))]
        return {e.name: e for e in examples}

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        toolbar = ttk.Frame(self, padding=8)
        toolbar.grid(row=0, column=0, sticky='ew')
        toolbar.columnconfigure(14, weight=1)
        quick = [(tr('Analyse + fix'), self.analyze_and_offer_fix), (tr('Build'), self.build_program), (tr('Run'), self.run_program), ('ROP/JOP', self.open_rop_jop_analysis), ('Disassembly', self.show_disassembly), (tr('Settings'), self.open_settings_window)]
        for idx, (label, cmd) in enumerate(quick):
            ttk.Button(toolbar, text=label, command=cmd).grid(row=0, column=idx, padx=3, pady=2)
        ttk.Label(toolbar, text=tr('Target:')).grid(row=0, column=7, padx=(12, 4))
        mode_box = ttk.Combobox(toolbar, textvariable=self.target_mode, state='readonly', width=16, values=['windows_x64', 'linux_x64'])
        mode_box.grid(row=0, column=8, padx=3)
        mode_box.bind('<<ComboboxSelected>>', self._on_target_changed)
        self.dep_var = tk.StringVar(value=tr('Dependencies: onbekend'))
        ttk.Label(toolbar, textvariable=self.dep_var).grid(row=0, column=14, sticky='e', padx=8)
        main = ttk.Panedwindow(self, orient=tk.HORIZONTAL)
        main.grid(row=1, column=0, sticky='nsew')
        left = ttk.Frame(main, padding=6)
        left.columnconfigure(0, weight=1)
        left.rowconfigure(1, weight=1)
        ttk.Label(left, text=tr('Voorbeeldbestanden')).grid(row=0, column=0, sticky='w')
        self.example_list = tk.Listbox(left, height=14)
        self.example_list.grid(row=1, column=0, sticky='nsew', pady=(4, 8))
        for name in self.example_names:
            self.example_list.insert(tk.END, name)
        self.example_list.bind('<<ListboxSelect>>', self._on_example_select)
        ttk.Button(left, text=tr('Laad geselecteerd voorbeeld'), command=self._load_selected_example_from_list).grid(row=2, column=0, sticky='ew')
        ttk.Button(left, text=tr('Importeer oefenbestanden...'), command=self.import_example_files).grid(row=3, column=0, sticky='ew', pady=(6, 0))
        center = ttk.Frame(main, padding=6)
        center.columnconfigure(1, weight=1)
        center.rowconfigure(0, weight=1)
        self.line_numbers = tk.Text(center, width=5, padx=4, takefocus=0, border=0, background='#f0f0f0', state='disabled', wrap='none', font=(self.ui_font_family, self.ui_font_size))
        self.line_numbers.grid(row=0, column=0, sticky='ns')
        self.editor = ScrolledText(center, undo=True, wrap='none', font=(self.ui_font_family, self.ui_font_size))
        self.editor.grid(row=0, column=1, sticky='nsew')
        self.editor.bind('<KeyRelease>', self.on_text_changed)
        self.editor.bind('<ButtonRelease-1>', self.on_text_changed)
        self.editor.bind('<ButtonRelease-1>', self._explain_current_line_event, add='+')
        self.editor.bind('<Return>', self._auto_indent)
        self.editor.bind('<Tab>', self._insert_spaces)
        right = ttk.Frame(main, padding=6)
        right.columnconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)
        right.rowconfigure(3, weight=1)
        right.rowconfigure(5, weight=2)
        ttk.Label(right, text=tr('Regel-uitleg / didactische hulp')).grid(row=0, column=0, sticky='w')
        self.help_box = ScrolledText(right, wrap='word', height=16, font=('Segoe UI', 10))
        self.help_box.grid(row=1, column=0, sticky='nsew', pady=(4, 8))
        self.help_box.configure(state='disabled')
        ttk.Label(right, text=tr('Leerdoel / verwacht resultaat')).grid(row=2, column=0, sticky='w')
        self.lesson_box = ScrolledText(right, wrap='word', height=10, font=('Segoe UI', 10))
        self.lesson_box.grid(row=3, column=0, sticky='nsew', pady=(4, 8))
        self.lesson_box.configure(state='disabled')
        runtime_container = ttk.LabelFrame(right, text=tr('Output / Console'))
        runtime_container.grid(row=5, column=0, sticky='nsew')
        runtime_container.columnconfigure(0, weight=1)
        runtime_container.rowconfigure(1, weight=1)
        self.runtime_hint_var = tk.StringVar(value=tr('Runtime-hint: laad een voorbeeld of bouw je eigen programma.'))
        ttk.Label(runtime_container, textvariable=self.runtime_hint_var).grid(row=0, column=0, columnspan=4, sticky='ew', padx=4, pady=(4, 0))
        self.console = ScrolledText(runtime_container, wrap='word', height=16, font=(self.ui_font_family, 10))
        self.console.grid(row=1, column=0, columnspan=4, sticky='nsew', padx=4, pady=(4, 2))
        self.console.configure(state='disabled')
        for tag, color in {'console_build': '#1b5e20', 'console_runtime_out': '#0d47a1', 'console_runtime_in': '#7b1fa2', 'console_runtime_err': '#b71c1c', 'console_hint': '#6d4c41', 'console_info': '#455a64'}.items():
            self.console.tag_configure(tag, foreground=color)
        self.console_input = ttk.Entry(runtime_container, textvariable=self.console_input_var)
        self.console_input.grid(row=2, column=0, sticky='ew', padx=(4, 2), pady=(2, 4))
        self.console_input.bind('<Return>', self.send_runtime_input_event)
        ttk.Button(runtime_container, text=tr('Verzend invoer'), command=self.send_runtime_input).grid(row=2, column=1, padx=2, pady=(2, 4))
        ttk.Button(runtime_container, text=tr('Demo invoer'), command=self.send_demo_input_to_running).grid(row=2, column=2, padx=2, pady=(2, 4))
        ttk.Button(runtime_container, text=tr('Wis console'), command=self.clear_console).grid(row=2, column=3, padx=(2, 4), pady=(2, 4))
        main.add(left, weight=1)
        main.add(center, weight=3)
        main.add(right, weight=2)
        footer = ttk.Frame(self, padding=(8, 4))
        footer.grid(row=2, column=0, sticky='ew')
        footer.columnconfigure(1, weight=1)
        self.status_var = tk.StringVar(value=tr('Klaar'))
        self.cursor_var = tk.StringVar(value=tr('Regel 1, kolom 1'))
        ttk.Label(footer, textvariable=self.status_var).grid(row=0, column=0, sticky='w')
        ttk.Label(footer, textvariable=self.cursor_var).grid(row=0, column=1, sticky='e')
        self.editor.tag_configure('comment', foreground='#2e8b57')
        self.editor.tag_configure('instruction', foreground='#1f4aa8')
        self.editor.tag_configure('register', foreground='#a02080')
        self.editor.tag_configure('label', foreground='#b35a00')
        self.editor.tag_configure('directive', foreground='#8b0000')
        self.editor.tag_configure('string', foreground='#aa5500')
        self.editor.tag_configure('errorline', background='#ffe7e7')
        self.editor.tag_configure('focusline', background='#dff2ff')

    @staticmethod
    def _discover_tool(name):
        found = shutil.which(name)
        if found:
            return found
        candidates = []
        if os.name == 'nt':
            if name == 'nasm':
                candidates = [Path(os.environ.get('LOCALAPPDATA', '')) / 'bin/NASM/nasm.exe', Path(os.environ.get('ProgramFiles', '')) / 'NASM/nasm.exe', Path.home() / 'AppData/Local/bin/NASM/nasm.exe']
            else:
                candidates = [Path('C:/msys64/ucrt64/bin') / (name + '.exe'), Path('C:/msys64/mingw64/bin') / (name + '.exe')]
        return str(next((path for path in candidates if path.is_file()), name))

    def _load_settings(self) -> None:
        try:
            if not os.path.exists(self.settings_file):
                return
            with open(self.settings_file, 'r', encoding='utf-8') as fh:
                data = json.load(fh)
            self.language = data.get('language', 'nl') if data.get('language', 'nl') in ('nl', 'en') else 'nl'
            self.compiler_path = data.get('compiler_path', self.compiler_path)
            self.linker_path = data.get('linker_path', self.linker_path)
            self.objdump_path = data.get('objdump_path', self.objdump_path)
            self.target_mode.set(data.get('target_mode', self.target_mode.get()))
            self.student_mode.set(bool(data.get('student_mode', True)))
            self.ui_font_family = data.get('ui_font_family', self.ui_font_family)
            self.ui_font_size = int(data.get('ui_font_size', self.ui_font_size))
        except Exception:
            pass

    def _save_settings(self) -> None:
        data = {'language': self.language, 'compiler_path': self.compiler_path, 'linker_path': self.linker_path, 'objdump_path': self.objdump_path, 'target_mode': self.target_mode.get(), 'student_mode': self.student_mode.get(), 'ui_font_family': self.ui_font_family, 'ui_font_size': self.ui_font_size}
        path = Path(self.settings_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix('.tmp')
        temporary.write_text(json.dumps(data, indent=2), encoding='utf-8')
        os.replace(temporary, path)

    def set_status(self, text: str) -> None:
        self.status_var.set(text)

    def _append_console(self, text: str, tag: str='console_info') -> None:
        self.console.configure(state='normal')
        self.console.insert(tk.END, text, tag)
        self.console.see(tk.END)
        self.console.configure(state='disabled')

    def log(self, text: str, tag: str='console_build') -> None:
        self._append_console(text + '\n', tag)

    def clear_console(self) -> None:
        self.console.configure(state='normal')
        self.console.delete('1.0', tk.END)
        self.console.configure(state='disabled')
        self._show_runtime_hint_in_console()

    def _show_runtime_hint_in_console(self) -> None:
        self._append_console('[Hint] ' + f'{self._get_current_input_hint()}' + '\n', 'console_hint')

    def _get_current_input_hint(self) -> str:
        if self.current_example_name and self.current_example_name in self.examples:
            return self.examples[self.current_example_name].input_hint or tr('Geen specifieke input-hint beschikbaar.')
        return tr("Typ invoer onderaan en klik op 'Verzend invoer'.")

    def _show_example_info(self, name: str) -> None:
        ex = self.examples[name]
        self.lesson_box.configure(state='normal')
        self.lesson_box.delete('1.0', tk.END)
        self.lesson_box.insert('1.0', f"{tr('Bestand: ')}" + f'{ex.name}' + f"{tr('\nCategorie: ')}" + f'{ex.category}' + '\n\n' + f'{ex.guide}' + f"{tr('\n\nVerwachte output:\n')}" + f'{ex.expected_output}' + '\n\nRuntime-hint:\n' + f'{ex.input_hint}')
        self.lesson_box.configure(state='disabled')
        self.runtime_hint_var.set('Runtime-hint: ' + ex.input_hint)

    def load_named_example(self, name: str) -> None:
        if not self.confirm_replace():
            return
        ex = self.examples[name]
        self.current_example_name = name
        self.editor.delete('1.0', tk.END)
        self.editor.insert('1.0', ex.content)
        self._show_example_info(name)
        self.help_box.configure(state='normal')
        self.help_box.delete('1.0', tk.END)
        self.help_box.insert('1.0', tr('Didactische modus actief.\nKlik op een regel voor uitleg.'))
        self.help_box.configure(state='disabled')
        self.clear_console()
        self.clean_text = self.editor.get('1.0', 'end-1c')
        self.last_binary = None
        self.set_status(f"{tr('Voorbeeld geladen: ')}" + f'{name}')
        self.on_text_changed()

    def _load_default_example(self) -> None:
        self.load_named_example(self.example_names[0])
        self.example_list.selection_clear(0, tk.END)
        self.example_list.selection_set(0)

    def _on_example_select(self, _event=None) -> None:
        sel = self.example_list.curselection()
        if sel:
            self._show_example_info(self.example_names[sel[0]])

    def _load_selected_example_from_list(self) -> None:
        sel = self.example_list.curselection()
        if sel:
            self.load_named_example(self.example_names[sel[0]])

    def open_examples_window(self) -> None:
        win = tk.Toplevel(self)
        win.title(tr('Voorbeelden'))
        box = tk.Listbox(win)
        box.pack(fill='both', expand=True, padx=8, pady=8)
        for name in self.example_names:
            box.insert(tk.END, name)
        ttk.Button(win, text=tr('Laad'), command=lambda: (self.load_named_example(self.example_names[box.curselection()[0]]), win.destroy()) if box.curselection() else None).pack(fill='x', padx=8, pady=8)

    def import_example_files(self) -> None:
        paths = filedialog.askopenfilenames(title=tr('Importeer oefenbestanden'), filetypes=[(tr('Assembly files'), '*.asm'), (tr('All files'), '*.*')])
        added = 0
        for path in paths:
            try:
                with open(path, 'r', encoding='utf-8') as fh:
                    content = fh.read()
                name = os.path.basename(path)
                if name in self.examples:
                    continue
                self.examples[name] = ExampleProgram(name=name, category=tr('Geimporteerde oefeningen'), content=content, guide=tr('Geimporteerd oefenbestand.'), expected_output=tr('Controleer comments in het bestand of voer het programma uit.'), error_lines=set(), focus_lines={}, input_hint=tr('Controleer comments in het bestand. Typ invoer handmatig indien nodig.'), demo_inputs=[])
                self.example_names.append(name)
                self.example_list.insert(tk.END, name)
                added += 1
            except Exception as exc:
                self.log(f"{tr('Importfout voor ')}" + f'{path}' + ': ' + f'{exc}', 'console_runtime_err')
        if added:
            messagebox.showinfo('Import', f'{added}' + f"{tr(' oefenbestand(en) geimporteerd.')}")

    def confirm_replace(self):
        if self.editor.get('1.0', 'end-1c') == self.clean_text:
            return True
        answer = messagebox.askyesnocancel(tr('Wijzigingen opslaan'), tr('Wil je de gewijzigde code eerst opslaan?'), parent=self)
        if answer is None:
            return False
        return self.save_file() if answer else True

    def new_file(self):
        if not self.confirm_replace():
            return
        self.editor.delete('1.0', tk.END)
        self.current_file = None
        self.current_example_name = None
        self.clean_text = ''
        self.last_binary = None
        self.clear_console()
        self.on_text_changed()

    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[(tr('Assembly files'), '*.asm *.s'), (tr('All files'), '*.*')])
        if not path or not self.confirm_replace():
            return
        try:
            text = Path(path).read_text(encoding='utf-8-sig')
        except (OSError, UnicodeError) as exc:
            messagebox.showerror(tr('Openen mislukt'), str(exc), parent=self)
            return
        self.editor.delete('1.0', tk.END)
        self.editor.insert('1.0', text)
        self.current_file = path
        self.current_example_name = None
        self.clean_text = text
        self.last_binary = None
        self.clear_console()
        self.on_text_changed()

    def save_file(self):
        if not self.current_file:
            return self.save_file_as()
        text = self.editor.get('1.0', 'end-1c')
        path = Path(self.current_file)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent, delete=False) as stream:
                stream.write(text)
                temporary = Path(stream.name)
            os.replace(temporary, path)
        except OSError as exc:
            messagebox.showerror(tr('Opslaan mislukt'), str(exc), parent=self)
            return False
        finally:
            if temporary:
                temporary.unlink(missing_ok=True)
        self.clean_text = text
        return True

    def save_file_as(self):
        path = filedialog.asksaveasfilename(defaultextension='.asm', filetypes=[(tr('Assembly files'), '*.asm')])
        if not path:
            return False
        previous = self.current_file
        self.current_file = path
        if self.save_file():
            return True
        self.current_file = previous
        return False

    def _sync_line_numbers_periodic(self) -> None:
        try:
            content = self.editor.get('1.0', 'end-1c')
            nums = '\n'.join((str(i) for i in range(1, max(1, content.count('\n') + 1) + 1)))
            self.line_numbers.configure(state='normal')
            self.line_numbers.delete('1.0', tk.END)
            self.line_numbers.insert('1.0', nums)
            self.line_numbers.configure(state='disabled')
        finally:
            self.after(150, self._sync_line_numbers_periodic)

    def on_text_changed(self, _event=None) -> None:
        idx = self.editor.index(tk.INSERT)
        line, col = idx.split('.')
        self.cursor_var.set(f"{tr('Regel ')}" + f'{int(line)}' + f"{tr(', kolom ')}" + f'{int(col) + 1}')
        self._apply_syntax_highlighting()

    def _apply_syntax_highlighting(self) -> None:
        for tag in ('comment', 'instruction', 'register', 'label', 'directive', 'string'):
            self.editor.tag_remove(tag, '1.0', tk.END)
        lines = self.editor.get('1.0', 'end-1c').splitlines()
        for i, line in enumerate(lines, start=1):
            if ';' in line:
                start = line.index(';')
                self.editor.tag_add('comment', f'{i}' + '.' + f'{start}', f'{i}' + '.end')
            for m in re.finditer('"[^"\\n]*"', line):
                self.editor.tag_add('string', f'{i}' + '.' + f'{m.start()}', f'{i}' + '.' + f'{m.end()}')
            stripped = line.strip()
            if stripped.endswith(':'):
                pos = line.find(stripped)
                self.editor.tag_add('label', f'{i}' + '.' + f'{pos}', f'{i}' + '.' + f'{pos + len(stripped)}')
            for token in re.findall('[A-Za-z_\\.][A-Za-z0-9_\\.]*', line):
                pos = line.lower().find(token.lower())
                if pos < 0:
                    continue
                end = pos + len(token)
                lower = token.lower()
                if lower in self.instructions:
                    self.editor.tag_add('instruction', f'{i}' + '.' + f'{pos}', f'{i}' + '.' + f'{end}')
                elif lower in self.registers:
                    self.editor.tag_add('register', f'{i}' + '.' + f'{pos}', f'{i}' + '.' + f'{end}')
                elif lower in self.directives:
                    self.editor.tag_add('directive', f'{i}' + '.' + f'{pos}', f'{i}' + '.' + f'{end}')

    def _explain_current_line_event(self, _event=None) -> None:
        line_no = int(self.editor.index(tk.INSERT).split('.')[0])
        line = self.editor.get(f'{line_no}' + '.0', f'{line_no}' + '.end').rstrip()
        msg = f"{tr('Regel ')}" + f'{line_no}' + ':\n' + f'{line}'
        self.help_box.configure(state='normal')
        self.help_box.delete('1.0', tk.END)
        self.help_box.insert('1.0', msg)
        self.help_box.configure(state='disabled')

    def _auto_indent(self, _event=None):
        line_no = int(self.editor.index(tk.INSERT).split('.')[0])
        prev = self.editor.get(f'{line_no}' + '.0', f'{line_no}' + '.end')
        indent = re.match('\\s*', prev).group(0)
        self.editor.insert(tk.INSERT, '\n' + indent)
        return 'break'

    def _insert_spaces(self, _event=None):
        self.editor.insert(tk.INSERT, '    ')
        return 'break'

    def analyze_and_offer_fix(self) -> None:
        issues = []
        for idx, raw in enumerate(self.editor.get('1.0', 'end-1c').splitlines(), start=1):
            stripped = raw.split(';', 1)[0].strip()
            if not stripped or stripped.endswith(':'):
                continue
            parts = stripped.split(None, 1)
            head = parts[0].lower()
            if head in self.two_operand_instructions:
                op = parts[1].strip() if len(parts) > 1 else ''
                if ',' not in op:
                    issues.append((idx, f"""{tr("Instructie '")}""" + f'{head}' + f"""{tr("' verwacht meestal 2 operanden.")}"""))
        self.help_box.configure(state='normal')
        self.help_box.delete('1.0', tk.END)
        if not issues:
            self.help_box.insert('1.0', tr('Geen duidelijke syntaxproblemen gevonden.'))
        else:
            self.help_box.insert('1.0', '\n'.join((f"{tr('Regel ')}" + f'{ln}' + ': ' + f'{msg}' for ln, msg in issues)))
        self.help_box.configure(state='disabled')

    def apply_last_fix_suggestion(self) -> None:
        self.log(tr('Automatische fix is in deze merge beperkt gehouden.'), 'console_hint')

    def check_syntax(self) -> None:
        self.analyze_and_offer_fix()

    def show_syntax_helper(self) -> None:
        self.help_box.configure(state='normal')
        self.help_box.delete('1.0', tk.END)
        self.help_box.insert('1.0', tr('Snelle syntaxhulp\n\nmov rax, 1\ncall printf\nsection .text\nglobal main\n\nGUI voorbeeld:\nglobal WinMain\nextern MessageBoxA'))
        self.help_box.configure(state='disabled')

    def show_register_explanation(self) -> None:
        self.help_box.configure(state='normal')
        self.help_box.delete('1.0', tk.END)
        self.help_box.insert('1.0', '\n\n'.join((f'{k.upper()}' + ': ' + f'{v}' for k, v in self.register_help.items())))
        self.help_box.configure(state='disabled')

    def _tool_exists(self, value: str) -> bool:
        return bool(value) and (os.path.exists(value) or shutil.which(value) is not None)

    def check_dependencies(self, startup: bool=False) -> None:
        nasm_ok = self._tool_exists(self.compiler_path)
        gcc_ok = self._tool_exists(self.linker_path)
        objdump_ok = self._tool_exists(self.objdump_path)
        self.dep_var.set('Dependencies: nasm=' + f"{('OK' if nasm_ok else 'X')}" + ' | gcc=' + f"{('OK' if gcc_ok else 'X')}" + ' | objdump=' + f"{('OK' if objdump_ok else 'X')}")
        if not startup:
            self.log('Dependency check: NASM=' + f"{('OK' if nasm_ok else 'X')}" + ', GCC=' + f"{('OK' if gcc_ok else 'X')}" + ', objdump=' + f"{('OK' if objdump_ok else 'X')}")

    def detect_gui_mode(self) -> bool:
        text = self.editor.get('1.0', 'end-1c').lower()
        return 'global winmain' in text or 'messageboxa' in text

    def _ensure_temp_dir(self) -> str:
        if self.temp_dir and os.path.isdir(self.temp_dir):
            return self.temp_dir
        self.temp_dir = tempfile.mkdtemp(prefix='assembly_editor_v553_')
        return self.temp_dir

    def _get_source_path(self) -> str:
        path = os.path.join(self._ensure_temp_dir(), 'buffer.asm')
        with open(path, 'w', encoding='utf-8') as fh:
            fh.write(self.editor.get('1.0', 'end-1c'))
        return path

    def start_task(self, work, complete):
        if self.task_busy:
            self.log(tr('Wacht tot de huidige taak klaar is.'), 'console_hint')
            return
        self.task_busy = True
        queue = Queue()

        def worker():
            try:
                queue.put((work(), None))
            except Exception as exc:
                queue.put((None, exc))

        def poll():
            if self.closing:
                return
            try:
                result, error = queue.get_nowait()
            except Empty:
                self.after(80, poll)
                return
            self.task_busy = False
            if error:
                self.log(f"{tr('Taak mislukt: ')}" + f'{error}', 'console_runtime_err')
                return
            complete(result)
        threading.Thread(target=worker, daemon=True).start()
        self.after(80, poll)

    def build_program(self, force_gui=None, on_success=None):
        if self.task_busy or self.runtime_active:
            self.log(tr('Stop het programma of wacht tot de huidige taak klaar is.'), 'console_hint')
            return
        self.last_binary = None
        self.last_obj = None
        self.built_source = None
        self.clear_console()
        for name, path in (('NASM', self.compiler_path), ('GCC', self.linker_path)):
            if not self._tool_exists(path):
                self.log(f'{name}' + f"{tr(' ontbreekt. Kies het uitvoerbestand via Tools > Dependency settings.')}", 'console_runtime_err')
                return
        text = self.editor.get('1.0', 'end-1c')
        target = self.target_mode.get()
        source = self._get_source_path()
        temp = self._ensure_temp_dir()
        obj = os.path.join(temp, 'buffer.obj' if target == 'windows_x64' else 'buffer.o')
        exe = os.path.join(temp, 'buffer.exe' if target == 'windows_x64' else 'buffer')
        fmt = 'win64' if target == 'windows_x64' else 'elf64'
        is_gui = self.detect_gui_mode() if force_gui is None else bool(force_gui)
        assembler = [self.compiler_path, '-f', fmt, source, '-o', obj]
        linker = [self.linker_path, obj, '-o', exe]
        if target == 'linux_x64':
            linker.append('-no-pie')
        if os.name == 'nt' and is_gui:
            linker.extend(['-mwindows', '-luser32', '-lkernel32'])

        def work():
            output = []
            for command in (assembler, linker):
                output.append(' '.join(command))
                result = subprocess.run(command, capture_output=True, text=True, timeout=30, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
                output.extend(filter(None, (result.stdout, result.stderr)))
                if result.returncode:
                    return (False, output)
            return (True, output)

        def complete(result):
            success, output = result
            for line in output:
                self.log(line)
            if not success:
                return
            if text != self.editor.get('1.0', 'end-1c') or target != self.target_mode.get():
                self.log(tr('Bron gewijzigd tijdens bouwen. Bouw opnieuw voor de actuele code.'), 'console_hint')
                return
            self.last_binary, self.last_obj = (exe, obj)
            self.built_source, self.built_target = (text, target)
            self.last_build_mode = 'gui' if is_gui else 'console'
            self.log(f"{tr('Build gereed: ')}" + f'{exe}')
            self._show_runtime_hint_in_console()
            if on_success:
                on_success()
        self.start_task(work, complete)

    def run_program(self) -> None:
        if self.runtime_active:
            self.log(tr('Er draait al een programma. Kies eerst Stop.'), 'console_hint')
            return
        if not self.last_binary or not os.path.exists(self.last_binary) or self.built_source != self.editor.get('1.0', 'end-1c') or (self.built_target != self.target_mode.get()):
            self.build_program(on_success=self.run_program)
            return
        if self.last_build_mode == 'gui':
            try:
                subprocess.Popen([self.last_binary], creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                self._append_console(tr('[GUI-programma gestart]\n'), 'console_info')
                self._append_console(tr("GUI-programma's tonen meestal een apart venster en gebruiken geen console-invoer.\n"), 'console_hint')
            except Exception as exc:
                self.log(f"{tr('GUI runtime start fout: ')}" + f'{exc}', 'console_runtime_err')
            return
        flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        try:
            self.runtime_process = subprocess.Popen([self.last_binary], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1, universal_newlines=True, creationflags=flags)
        except Exception as exc:
            self.log(f"{tr('Runtime start fout: ')}" + f'{exc}', 'console_runtime_err')
            return
        self.runtime_active = True
        self._append_console(tr('\n[Runtime gestart]\n'), 'console_info')
        self._append_console('[Runtime-hint] ' + f'{self._get_current_input_hint()}' + '\n', 'console_hint')
        threading.Thread(target=self._runtime_reader_worker, daemon=True).start()

    def run_demo_inputs(self) -> None:
        if self.last_build_mode == 'gui':
            self.log(tr("GUI-programma's gebruiken hier meestal geen demo-invoer."), 'console_hint')
            return
        if not self.current_example_name or self.current_example_name not in self.examples:
            return
        demo = self.examples[self.current_example_name].demo_inputs
        if not demo:
            self.log(tr('Dit voorbeeld heeft geen demo-invoer nodig.'), 'console_hint')
            return
        for i, value in enumerate(demo, start=1):
            self.after(150 * i, lambda v=value: self._send_input_line(v))

    def send_demo_input_to_running(self) -> None:
        if self.last_build_mode == 'gui':
            self.log(tr("GUI-programma's gebruiken hier meestal geen demo-invoer."), 'console_hint')
            return
        if not self.current_example_name or self.current_example_name not in self.examples:
            self.log(tr('Geen actief voorbeeld geladen.'), 'console_hint')
            return
        demo = self.examples[self.current_example_name].demo_inputs
        if not demo:
            self.log(tr('Dit voorbeeld heeft geen demo-invoer nodig.'), 'console_hint')
            return
        for i, value in enumerate(demo, start=1):
            self.after(150 * i, lambda v=value: self._send_input_line(v))

    def _runtime_reader_worker(self) -> None:
        proc = self.runtime_process
        if proc is None:
            return

        def reader(stream, kind):
            while True:
                data = stream.readline()
                if not data:
                    break
                self.runtime_queue.put((kind, data))
        threading.Thread(target=reader, args=(proc.stdout, 'stdout'), daemon=True).start()
        threading.Thread(target=reader, args=(proc.stderr, 'stderr'), daemon=True).start()
        code = proc.wait()
        self.runtime_queue.put(('info', f"{tr('\n[Runtime beeindigd met code ')}" + f'{code}' + ']\n'))
        self.runtime_queue.put(('finished', ''))

    def _poll_runtime_queue(self) -> None:
        try:
            while True:
                kind, data = self.runtime_queue.get_nowait()
                if kind == 'stdout':
                    self._append_console(data, 'console_runtime_out')
                elif kind == 'stderr':
                    self._append_console(data, 'console_runtime_err')
                elif kind == 'stdin_echo':
                    self._append_console(data, 'console_runtime_in')
                elif kind == 'info':
                    self._append_console(data, 'console_info')
                elif kind == 'finished':
                    self.runtime_active = False
                    self.runtime_process = None
        except Empty:
            pass
        finally:
            self.after(100, self._poll_runtime_queue)

    def _send_input_line(self, text: str) -> None:
        if not self.runtime_active or not self.runtime_process or (not self.runtime_process.stdin):
            self.log(tr('Er draait geen consoleprogramma.'), 'console_runtime_err')
            return
        self.runtime_process.stdin.write(text + '\n')
        self.runtime_process.stdin.flush()
        self.runtime_queue.put(('stdin_echo', '> ' + f'{text}' + '\n'))

    def send_runtime_input_event(self, _event=None):
        self.send_runtime_input()
        return 'break'

    def send_runtime_input(self) -> None:
        text = self.console_input_var.get()
        self.console_input_var.set('')
        self._send_input_line(text)

    def stop_program(self) -> None:
        if self.runtime_process:
            try:
                self.runtime_process.terminate()
            except Exception:
                pass
        self.runtime_active = False
        self.runtime_process = None
        self._append_console(tr('\n[Stop aangevraagd]\n'), 'console_info')

    def show_disassembly(self) -> None:
        if not self.last_binary or not os.path.exists(self.last_binary):
            return
        if not self._tool_exists(self.objdump_path):
            self.log(f"{tr('objdump niet gevonden: ')}" + f'{self.objdump_path}', 'console_runtime_err')
            return
        try:
            proc = subprocess.run([self.objdump_path, '-d', self.last_binary], capture_output=True, text=True, timeout=15)
        except Exception as exc:
            self.log(f"{tr('Disassembly fout: ')}" + f'{exc}', 'console_runtime_err')
            return
        win = tk.Toplevel(self)
        win.title('Disassembly')
        box = ScrolledText(win, wrap='none', font=(self.ui_font_family, 10))
        box.pack(fill='both', expand=True)
        box.insert('1.0', proc.stdout or '')
        box.configure(state='disabled')

    def _colorize_rop_output(self, widget):
        widget.tag_configure('rop_header', foreground='#0d47a1', font=('Segoe UI', 10, 'bold'))
        widget.tag_configure('addr', foreground='#6a1b9a')
        widget.tag_configure('gadget', foreground='#1b5e20')
        widget.tag_configure('cf', foreground='#b71c1c')
        for header in (tr('=== CHECKSEC / MITIGATIES ==='), tr('=== ROP-SAMENVATTING ==='), tr('=== DIDACTISCHE SCORE ==='), '=== RUWE ROPPER-OUTPUT ==='):
            start = '1.0'
            while True:
                idx = widget.search(header, start, tk.END)
                if not idx:
                    break
                line_end = idx.split('.')[0] + '.end'
                widget.tag_add('rop_header', idx, line_end)
                start = line_end
        start = '1.0'
        while True:
            idx = widget.search('0x', start, tk.END)
            if not idx:
                break
            end = f'{idx}' + ' lineend'
            widget.tag_add('addr', idx, end)
            start = end
        for needle, tag in {'pop': 'gadget', 'mov': 'gadget', 'xor': 'gadget', 'add': 'gadget', 'sub': 'gadget', 'lea': 'gadget', 'push': 'gadget', 'ret': 'cf', 'jmp': 'cf', 'call': 'cf', 'syscall': 'cf'}.items():
            start = '1.0'
            while True:
                idx = widget.search(needle, start, tk.END, nocase=True)
                if not idx:
                    break
                end = f'{idx}' + '+' + f'{len(needle)}' + 'c'
                widget.tag_add(tag, idx, end)
                start = end

    def _extract_gadget_lines(self, rop_blob: str):
        return [ln.rstrip() for ln in rop_blob.splitlines() if ln.strip().startswith('0x')]

    def _classify_gadget_line(self, line: str) -> str:
        low = line.lower()
        if ' pop' in low and ' ret' in low:
            return 'POP->RET'
        if ' ret' in low or low.endswith('ret'):
            return 'RET gadget'
        if ' jmp' in low:
            return 'JOP / JMP'
        if ' call' in low:
            return 'JOP / CALL'
        if ' syscall' in low:
            return 'SYSCALL'
        return tr('Overig')

    def _gadget_stats(self, gadget_lines):
        stats = {'totaal': len(gadget_lines), 'ret': 0, 'jmp': 0, 'call': 0, 'popret': 0, 'syscall': 0}
        for line in gadget_lines:
            low = line.lower()
            if ' ret' in low or low.endswith('ret'):
                stats['ret'] += 1
            if ' jmp' in low:
                stats['jmp'] += 1
            if ' call' in low:
                stats['call'] += 1
            if 'pop' in low and 'ret' in low:
                stats['popret'] += 1
            if 'syscall' in low:
                stats['syscall'] += 1
        return stats

    def _make_simple_hexdump(self, file_path: str, limit: int=512) -> str:
        try:
            with open(file_path, 'rb') as fh:
                data = fh.read(limit)
        except Exception as exc:
            return tr('Kon binary niet lezen voor hex-preview: ') + f'{exc}'
        lines = []
        for offset in range(0, len(data), 16):
            chunk = data[offset:offset + 16]
            hex_part = ' '.join((f'{b:02X}' for b in chunk))
            ascii_part = ''.join((chr(b) if 32 <= b <= 126 else '.' for b in chunk))
            lines.append(f'{offset:08X}' + '  ' + f'{hex_part:<47}' + '  ' + f'{ascii_part}')
        return '\n'.join(lines) if lines else tr('(geen data)')

    def open_rop_jop_analysis(self) -> None:
        if not self.last_binary or not os.path.exists(self.last_binary):
            self.log(tr('Bouw eerst een binary voordat je ROP/JOP analyse doet.'), 'console_runtime_err')
            return
        if self.built_source != self.editor.get('1.0', 'end-1c') or self.built_target != self.target_mode.get():
            self.log(tr('Bouw eerst de actuele code voor analyse.'), 'console_hint')
            return
        binary = self.last_binary
        self.start_task(lambda: analyze_for_editor(binary), self._show_rop_jop_results)

    def _show_rop_jop_results(self, results):
        raw_rop = str(results['rop_raw'])
        gadget_lines_all = self._extract_gadget_lines(raw_rop)
        win = tk.Toplevel(self)
        win.title(tr('ROP/JOP analyse - didactische modus'))
        win.geometry('1450x900')
        win.columnconfigure(0, weight=1)
        win.rowconfigure(1, weight=1)
        top = ttk.Frame(win, padding=8)
        top.grid(row=0, column=0, sticky='ew')
        ttk.Label(top, text=tr('Binary hardening / gadgetscan')).pack(side='left')
        ttk.Label(top, text='Filter:').pack(side='left', padx=(16, 4))
        filter_var = tk.StringVar()
        ttk.Entry(top, textvariable=filter_var, width=28).pack(side='left', padx=4)
        body = ttk.Frame(win, padding=8)
        body.grid(row=1, column=0, sticky='nsew')
        body.columnconfigure(0, weight=1)
        body.rowconfigure(0, weight=3)
        body.rowconfigure(1, weight=2)
        body.rowconfigure(2, weight=1)
        results_frame = ttk.LabelFrame(body, text=tr('Results & explanation'))
        results_frame.grid(row=0, column=0, sticky='nsew')
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        results_box = ScrolledText(results_frame, wrap='word', height=16, font=('Segoe UI', 10))
        results_box.grid(row=0, column=0, sticky='nsew', padx=6, pady=6)
        gadgets_frame = ttk.LabelFrame(body, text=tr('ROP gadgets (didactisch)'))
        gadgets_frame.grid(row=1, column=0, sticky='nsew', pady=(10, 0))
        gadgets_frame.columnconfigure(0, weight=1)
        gadgets_frame.rowconfigure(1, weight=1)
        controls = ttk.Frame(gadgets_frame)
        controls.grid(row=0, column=0, sticky='ew', padx=6, pady=(6, 2))
        gadget_list = tk.Listbox(gadgets_frame, font=(self.ui_font_family, 10))
        gadget_list.grid(row=1, column=0, sticky='nsew', padx=6, pady=(0, 6))
        explain_frame = ttk.LabelFrame(body, text=tr('Uitleg bij geselecteerde gadget'))
        explain_frame.grid(row=2, column=0, sticky='nsew', pady=(10, 0))
        explain_frame.columnconfigure(0, weight=1)
        explain_frame.rowconfigure(1, weight=1)
        explain_controls = ttk.Frame(explain_frame)
        explain_controls.grid(row=0, column=0, sticky='ew', padx=6, pady=(6, 2))
        selected_addr_var = tk.StringVar(value=tr('Nog geen gadget/mapping geselecteerd.'))
        selected_info_var = tk.StringVar(value=tr('Nog geen gadget/mapping geselecteerd.'))
        explain_box = ScrolledText(explain_frame, wrap='word', height=8, font=('Segoe UI', 10))
        explain_box.grid(row=1, column=0, sticky='nsew', padx=6, pady=(0, 6))

        def selected_line():
            sel = gadget_list.curselection()
            if not sel:
                return None
            return gadget_list.get(sel[0])

        def open_hex_window(title: str, text_blob: str):
            hex_win = tk.Toplevel(win)
            hex_win.title(title)
            hex_win.geometry('900x500')
            box = ScrolledText(hex_win, wrap='none', font=(self.ui_font_family, 10))
            box.pack(fill='both', expand=True)
            box.insert('1.0', text_blob)

        def on_select(_event=None):
            line = selected_line()
            if not line:
                return
            category = self._classify_gadget_line(line)
            text = explain_gadget_line(line)
            explain_box.delete('1.0', tk.END)
            explain_box.insert('1.0', f"{tr('Categorie: ')}" + f'{category}' + '\n\n' + f'{text}')
            addr = line.split(':', 1)[0].strip() if ':' in line else line.strip().split()[0]
            selected_addr_var.set(addr)
            selected_info_var.set(category)

        def open_hex_for_selected():
            line = selected_line()
            if not line:
                explain_box.delete('1.0', tk.END)
                explain_box.insert('1.0', tr('Selecteer eerst een gadgetregel.'))
                return
            addr = line.split(':', 1)[0].strip() if ':' in line else tr('(onbekend)')
            blob = f"{tr('Geselecteerde gadget: ')}" + f'{line}' + f"{tr('\n\nAdres: ')}" + f'{addr}' + f"{tr('\n\nDidactische opmerking:\nDe exacte VA->file offset mapping is in deze versie vereenvoudigd.\nHieronder zie je een preview van de binarybeginbytes.\n\n')}" + self._make_simple_hexdump(self.last_binary, limit=1024)
            open_hex_window(tr('Hex viewer - geselecteerde gadget'), blob)

        def copy_selected_address():
            line = selected_line()
            if not line:
                return
            addr = line.split(':', 1)[0].strip() if ':' in line else line.strip().split()[0]
            try:
                win.clipboard_clear()
                win.clipboard_append(addr)
                selected_addr_var.set(addr)
                selected_info_var.set(tr('Adres gekopieerd'))
            except Exception:
                selected_info_var.set(tr('Kopieren mislukt'))

        def show_more_info():
            blob = tr('Didactische toelichting\n\n1. RET-gadgets zijn klassiek relevant voor ROP-ketens.\n2. JMP/CALL-gadgets zijn interessanter in een JOP-context.\n3. POP->RET-gadgets helpen vaak om registers op te bouwen.\n4. Hexweergave helpt studenten de link te leggen tussen binaire bytes en gedisassembleerde instructies.\n5. De huidige hexweergave toont een vereenvoudigde preview; voor volledige adresmapping is een uitgebreidere offset-resolutie nodig.\n')
            open_hex_window(tr('Meer info: gadgets & hex'), blob)
        ttk.Button(controls, text=tr('Scan ROP-gadgets'), command=lambda: apply_filter()).pack(side='left', padx=(0, 6))
        ttk.Label(controls, text='Filter:').pack(side='left')
        ttk.Entry(controls, textvariable=filter_var, width=24).pack(side='left', padx=4)
        ttk.Button(controls, text=tr('Toepassen'), command=lambda: apply_filter()).pack(side='left', padx=4)
        ttk.Button(controls, text='Reset', command=lambda: reset_filter()).pack(side='left', padx=4)
        ttk.Button(controls, text='pop rdi', command=lambda: preset_filter('pop rdi')).pack(side='left', padx=8)
        ttk.Button(controls, text='syscall', command=lambda: preset_filter('syscall')).pack(side='left', padx=4)
        ttk.Button(controls, text=tr('Open Hex bij gadget-regel'), command=lambda: open_hex_for_selected()).pack(side='left', padx=8)
        ttk.Button(controls, text=tr('Meer info: gadgets & hex'), command=lambda: show_more_info()).pack(side='left', padx=4)
        ttk.Button(explain_controls, text=tr('Open Hex (geselecteerde gadget)'), command=lambda: open_hex_for_selected()).pack(side='left', padx=(0, 6))
        ttk.Button(explain_controls, text=tr('Kopieer adres'), command=lambda: copy_selected_address()).pack(side='left', padx=(0, 12))
        ttk.Label(explain_controls, textvariable=selected_addr_var).pack(side='left', padx=6)
        ttk.Label(explain_controls, textvariable=selected_info_var).pack(side='left', padx=6)
        score = results['rop_score']
        gadget_stats = self._gadget_stats(gadget_lines_all)
        summary_blob = 'Binary: ' + f"{results['binary_path']}" + '\nBinary type: ' + f"{results['binary_type']}" + f"{tr('\n\n=== CHECKSEC / MITIGATIES ===\n')}" + f"{str(results['checksec_text']).strip()}" + f"{tr('\n\n=== ROP-SAMENVATTING ===\n')}" + f"{str(results['rop_summary']).strip()}" + f"{tr('\n\n=== DIDACTISCHE SCORE ===\nRET-gerelateerde telling: ')}" + f"{score['ret_count']}" + f"{tr('\nIndirecte JMP telling: ')}" + f"{score['jmp_count']}" + f"{tr('\nIndirecte CALL telling: ')}" + f"{score['call_count']}" + f"{tr('\nPOP->RET telling: ')}" + f"{score['popret_count']}" + f"{tr('\nDidactische totaalscore: ')}" + f"{score['score']}" + f"{tr('/100\n\nSnelle gadgetstatistiek\n- Totaal getelde gadgetregels: ')}" + f"{gadget_stats['totaal']}" + '\n- RET gadgets: ' + f"{gadget_stats['ret']}" + f"{tr('\n- JMP-gerelateerd: ')}" + f"{gadget_stats['jmp']}" + f"{tr('\n- CALL-gerelateerd: ')}" + f"{gadget_stats['call']}" + '\n- POP->RET: ' + f"{gadget_stats['popret']}" + '\n- SYSCALL: ' + f"{gadget_stats['syscall']}" + '\n'
        results_box.insert('1.0', summary_blob)
        self._colorize_rop_output(results_box)

        def populate_gadgets(lines):
            gadget_list.delete(0, tk.END)
            for line in lines:
                gadget_list.insert(tk.END, line)
            stats = self._gadget_stats(lines)
            selected_info_var.set(f"{tr('Getoond: ')}" + f'{len(lines)}' + ' | RET: ' + f"{stats['ret']}" + ' | JMP: ' + f"{stats['jmp']}" + ' | CALL: ' + f"{stats['call']}" + ' | POP->RET: ' + f"{stats['popret']}")

        def apply_filter():
            pattern = filter_var.get()
            filtered_blob = filter_rop_lines(raw_rop, pattern)
            filtered_lines = self._extract_gadget_lines(filtered_blob)
            populate_gadgets(filtered_lines)

        def reset_filter():
            filter_var.set('')
            populate_gadgets(gadget_lines_all)

        def preset_filter(value):
            filter_var.set(value)
            apply_filter()
        gadget_list.bind('<<ListboxSelect>>', on_select)
        gadget_list.bind('<Double-Button-1>', lambda e: (on_select(), open_hex_for_selected()))
        populate_gadgets(gadget_lines_all)
        explain_box.insert('1.0', tr('Klik op een gadgetregel hierboven om uitleg te zien.\nDubbelklik opent de hex-viewer direct.'))
        self.log(tr('ROP/JOP analyse geopend.'), 'console_info')

    def change_editor_font_size(self, delta: int) -> None:
        self.ui_font_size = max(8, self.ui_font_size + delta)
        self.editor.configure(font=(self.ui_font_family, self.ui_font_size))
        self.line_numbers.configure(font=(self.ui_font_family, self.ui_font_size))

    def open_settings_window(self) -> None:
        win = tk.Toplevel(self)
        win.title(tr('Dependency settings'))
        win.geometry('900x380')
        win.columnconfigure(1, weight=1)
        nasm_var = tk.StringVar(value=self.compiler_path)
        gcc_var = tk.StringVar(value=self.linker_path)
        obj_var = tk.StringVar(value=self.objdump_path)
        font_var = tk.StringVar(value=self.ui_font_family)
        size_var = tk.StringVar(value=str(self.ui_font_size))
        check_var = tk.StringVar(value=tr("Klik op 'Check nu', 'Browse...' of 'Auto detect'."))

        def browse_for(var: tk.StringVar, title: str):
            path = filedialog.askopenfilename(title=title, filetypes=[(tr('Executable files'), '*.exe'), (tr('All files'), '*.*')])
            if path:
                var.set(path)
        rows = [(tr('NASM path'), nasm_var, tr('Kies NASM')), (tr('GCC path'), gcc_var, tr('Kies GCC')), (tr('Objdump path'), obj_var, tr('Kies objdump'))]
        for r, (label, var, title) in enumerate(rows):
            ttk.Label(win, text=label).grid(row=r, column=0, sticky='w', padx=8, pady=8)
            ttk.Entry(win, textvariable=var).grid(row=r, column=1, sticky='ew', padx=8, pady=8)
            ttk.Button(win, text=tr('Browse...'), command=lambda v=var, t=title: browse_for(v, t)).grid(row=r, column=2, padx=4, pady=8)
        ttk.Label(win, text=tr('Font family')).grid(row=3, column=0, sticky='w', padx=8, pady=8)
        ttk.Entry(win, textvariable=font_var).grid(row=3, column=1, sticky='ew', padx=8, pady=8)
        ttk.Label(win, text=tr('Font size')).grid(row=4, column=0, sticky='w', padx=8, pady=8)
        ttk.Entry(win, textvariable=size_var).grid(row=4, column=1, sticky='ew', padx=8, pady=8)
        ttk.Label(win, textvariable=check_var).grid(row=5, column=0, columnspan=3, sticky='w', padx=8, pady=(8, 4))

        def auto_detect():
            candidate_dirs = [os.environ.get('ProgramFiles', ''), os.environ.get('ProgramFiles(x86)', ''), 'C:\\msys64\\ucrt64\\bin', 'C:\\msys64\\mingw64\\bin', 'C:\\Program Files\\NASM']

            def first_existing(names):
                for n in names:
                    found = shutil.which(n)
                    if found:
                        return found
                for base in candidate_dirs:
                    if not base or not os.path.exists(base):
                        continue
                    for n in names:
                        cand = os.path.join(base, n)
                        if os.path.exists(cand):
                            return cand
                return names[0]
            nasm_var.set(first_existing(['nasm.exe', 'nasm']))
            gcc_var.set(first_existing(['gcc.exe', 'gcc']))
            obj_var.set(first_existing(['objdump.exe', 'objdump']))
            check_var.set(tr('Auto detect uitgevoerd.'))

        def check_now():
            ok = [self._tool_exists(nasm_var.get()), self._tool_exists(gcc_var.get()), self._tool_exists(obj_var.get())]
            check_var.set(f"{tr('Controle: NASM=')}" + f"{('OK' if ok[0] else 'X')}" + ', GCC=' + f"{('OK' if ok[1] else 'X')}" + ', objdump=' + f"{('OK' if ok[2] else 'X')}")

        def save_settings():
            self.compiler_path = nasm_var.get().strip() or self.compiler_path
            self.linker_path = gcc_var.get().strip() or self.linker_path
            self.objdump_path = obj_var.get().strip() or self.objdump_path
            self.ui_font_family = font_var.get().strip() or self.ui_font_family
            try:
                self.ui_font_size = max(8, int(size_var.get().strip()))
            except Exception:
                pass
            self.editor.configure(font=(self.ui_font_family, self.ui_font_size))
            self.line_numbers.configure(font=(self.ui_font_family, self.ui_font_size))
            self.console.configure(font=(self.ui_font_family, 10))
            self._save_settings()
            self.check_dependencies(startup=False)
            win.destroy()
        buttons = ttk.Frame(win)
        buttons.grid(row=6, column=0, columnspan=3, sticky='ew', padx=8, pady=12)
        ttk.Button(buttons, text='Auto detect', command=auto_detect).grid(row=0, column=0, padx=4)
        ttk.Button(buttons, text=tr('Nu controleren'), command=check_now).grid(row=0, column=1, padx=4)
        ttk.Button(buttons, text=tr('Opslaan'), command=save_settings).grid(row=0, column=2, padx=4)

    def _on_target_changed(self, _event=None) -> None:
        self.check_dependencies(startup=False)

    def _on_close(self) -> None:
        if not self.confirm_replace():
            return
        try:
            self._save_settings()
        except OSError as exc:
            messagebox.showerror(tr('Instellingen opslaan mislukt'), str(exc), parent=self)
            return
        self.closing = True
        self.stop_program()
        self.destroy()
if __name__ == '__main__':
    app = AssemblyEditorV555()
    app.mainloop()
