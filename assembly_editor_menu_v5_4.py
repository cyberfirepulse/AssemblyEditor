from localization import tr
import tkinter as tk
from tkinter import messagebox, simpledialog

def install_menus(app) -> None:
    menubar = tk.Menu(app)
    file_menu = tk.Menu(menubar, tearoff=0)
    file_menu.add_command(label=tr('Nieuw'), command=app.new_file)
    file_menu.add_command(label=tr('Openen...'), command=app.open_file)
    file_menu.add_separator()
    file_menu.add_command(label=tr('Opslaan'), command=app.save_file)
    file_menu.add_command(label=tr('Opslaan als...'), command=app.save_file_as)
    file_menu.add_separator()
    file_menu.add_command(label=tr('Importeer oefenbestanden...'), command=app.import_example_files)
    file_menu.add_separator()
    file_menu.add_command(label=tr('Afsluiten'), command=app._on_close)
    menubar.add_cascade(label=tr('File'), menu=file_menu)
    edit_menu = tk.Menu(menubar, tearoff=0)
    edit_menu.add_command(label=tr('Undo'), command=lambda: _safe_text_action(app, '<<Undo>>'))
    edit_menu.add_command(label=tr('Redo'), command=lambda: _safe_text_action(app, '<<Redo>>'))
    edit_menu.add_separator()
    edit_menu.add_command(label=tr('Knippen'), command=lambda: _safe_text_action(app, '<<Cut>>'))
    edit_menu.add_command(label=tr('Kopieren'), command=lambda: _safe_text_action(app, '<<Copy>>'))
    edit_menu.add_command(label=tr('Plakken'), command=lambda: _safe_text_action(app, '<<Paste>>'))
    edit_menu.add_separator()
    edit_menu.add_command(label=tr('Alles selecteren'), command=lambda: _select_all(app))
    edit_menu.add_command(label=tr('Zoeken...'), command=lambda: find_text(app))
    menubar.add_cascade(label=tr('Edit'), menu=edit_menu)
    project_menu = tk.Menu(menubar, tearoff=0)
    project_menu.add_command(label=tr('Voorbeeldenvenster'), command=app.open_examples_window)
    examples_sub = tk.Menu(project_menu, tearoff=0)
    for name in app.example_names:
        examples_sub.add_command(label=name, command=lambda n=name: app.load_named_example(n))
    project_menu.add_cascade(label=tr('Laad ingebouwd voorbeeld'), menu=examples_sub)
    project_menu.add_separator()
    project_menu.add_command(label=tr('Importeer oefenbestanden...'), command=app.import_example_files)
    menubar.add_cascade(label='Project', menu=project_menu)
    make_menu = tk.Menu(menubar, tearoff=0)
    make_menu.add_command(label=tr('Check syntax'), command=app.check_syntax)
    make_menu.add_command(label=tr('Build (auto)'), command=app.build_program)
    make_menu.add_command(label=tr('Build console'), command=lambda: app.build_program(force_gui=False))
    make_menu.add_command(label=tr('Build GUI'), command=lambda: app.build_program(force_gui=True))
    make_menu.add_separator()
    make_menu.add_command(label=tr('Run'), command=app.run_program)
    make_menu.add_command(label=tr('Run demo'), command=app.run_demo_inputs)
    make_menu.add_command(label='Stop', command=app.stop_program)
    make_menu.add_separator()
    make_menu.add_command(label='Disassembly', command=app.show_disassembly)
    menubar.add_cascade(label=tr('Make'), menu=make_menu)
    tools_menu = tk.Menu(menubar, tearoff=0)
    tools_menu.add_command(label=tr('Analyse + fix'), command=app.analyze_and_offer_fix)
    tools_menu.add_command(label=tr('Fix regel'), command=app.apply_last_fix_suggestion)
    tools_menu.add_command(label=tr('Syntax helper'), command=app.show_syntax_helper)
    tools_menu.add_command(label=tr('Register-uitleg'), command=app.show_register_explanation)
    tools_menu.add_separator()
    tools_menu.add_command(label=tr('ROP/JOP analyse'), command=app.open_rop_jop_analysis)
    tools_menu.add_separator()
    tools_menu.add_command(label=tr('Dependency settings'), command=app.open_settings_window)
    menubar.add_cascade(label=tr('Tools'), menu=tools_menu)
    view_menu = tk.Menu(menubar, tearoff=0)
    view_menu.add_command(label=tr('Wis console'), command=app.clear_console)
    view_menu.add_command(label=tr('Toon runtime-hint'), command=app._show_runtime_hint_in_console)
    view_menu.add_separator()
    view_menu.add_command(label='Zoom in', command=lambda: app.change_editor_font_size(1))
    view_menu.add_command(label=tr('Zoom uit'), command=lambda: app.change_editor_font_size(-1))
    view_menu.add_separator()
    view_menu.add_command(label=tr('Focus editor'), command=lambda: app.editor.focus_set())
    view_menu.add_command(label=tr('Focus console'), command=lambda: app.console_input.focus_set())
    menubar.add_cascade(label=tr('View'), menu=view_menu)
    language_menu = tk.Menu(menubar, tearoff=0)
    for code, label in (('nl', 'Nederlands'), ('en', 'English')):
        language_menu.add_radiobutton(label=label, value=code, variable=app.language_var, command=lambda c=code: app.change_language(c))
    menubar.add_cascade(label=tr('Taal'), menu=language_menu)
    help_menu = tk.Menu(menubar, tearoff=0)
    help_menu.add_command(label=tr('Gebruikershandleiding'), accelerator='F1', command=app.show_help)
    help_menu.add_command(label=tr('Controleren op updates'), command=app.check_for_updates)
    help_menu.add_separator()
    help_menu.add_command(label=tr('Over Assembly Editor'), command=app.show_about)
    menubar.add_cascade(label='Help', menu=help_menu)
    app.config(menu=menubar)

def _safe_text_action(app, sequence: str) -> None:
    try:
        app.editor.event_generate(sequence)
    except Exception:
        pass

def _select_all(app) -> None:
    app.editor.tag_add('sel', '1.0', 'end-1c')
    app.editor.mark_set('insert', '1.0')
    app.editor.see('insert')

def find_text(app) -> None:
    term = simpledialog.askstring(tr('Zoeken'), tr('Zoekterm:'))
    if not term:
        return
    app.editor.tag_remove('search_hit', '1.0', 'end')
    app.editor.tag_configure('search_hit', background='#fff59d')
    start = '1.0'
    hit_count = 0
    while True:
        pos = app.editor.search(term, start, stopindex='end', nocase=True)
        if not pos:
            break
        end = f'{pos}' + '+' + f'{len(term)}' + 'c'
        app.editor.tag_add('search_hit', pos, end)
        start = end
        hit_count += 1
    if hit_count:
        app.set_status(f"{tr('Zoeken: ')}" + f'{hit_count}' + f"""{tr(" resultaat/resultaten voor '")}""" + f'{term}' + "'")
    else:
        messagebox.showinfo(tr('Zoeken'), f"{tr('Geen resultaten voor: ')}" + f'{term}')

def _show_help(app, title, text):
    win = tk.Toplevel(app)
    win.title(title)
    win.geometry('760x560')
    txt = tk.Text(win, wrap='word', padx=10, pady=10)
    txt.pack(fill='both', expand=True)
    txt.insert('1.0', text)
    txt.configure(state='disabled')
