import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import localization
from localization import tr
from user_guide import TOPICS

def show_help(app):
    existing = getattr(app, 'guide_window', None)
    if existing is not None and existing.winfo_exists():
        existing.lift()
        return existing
    win = app.guide_window = tk.Toplevel(app)
    win.geometry('1050x720')
    win.minsize(760, 480)
    pane = ttk.Panedwindow(win, orient=tk.HORIZONTAL)
    pane.pack(fill='both', expand=True, padx=12, pady=12)
    nav = tk.Listbox(pane, exportselection=False, font=('Segoe UI', 11), width=30)
    body = ScrolledText(pane, wrap='word', font=('Segoe UI', 11), padx=16, pady=12)
    body.tag_configure('heading', font=('Segoe UI', 17, 'bold'), foreground='#175d81', spacing3=16)
    pane.add(nav, weight=1)
    pane.add(body, weight=3)
    def render(event=None):
        index = nav.curselection()[0] if nav.curselection() else 0
        title, nl, en = TOPICS[index]
        body.configure(state='normal')
        body.delete('1.0', tk.END)
        body.insert('end', tr(title) + '\n\n', 'heading')
        body.insert('end', en if localization.language == 'en' else nl)
        body.configure(state='disabled')
        body.yview_moveto(0)
    def refresh():
        index = nav.curselection()[0] if nav.curselection() else 0
        win.title(tr('Gebruikershandleiding') + ' — Assembly Editor ' + app.version)
        nav.delete(0, tk.END)
        for title, _, _ in TOPICS:
            nav.insert(tk.END, tr(title))
        nav.selection_set(index)
        render()
    win.refresh_language = refresh
    nav.bind('<<ListboxSelect>>', render)
    ttk.Button(win, text=tr('Sluiten'), command=win.destroy).pack(anchor='e', padx=12, pady=(0,12))
    refresh()
    return win

def show_about(app):
    win = tk.Toplevel(app)
    win.geometry('580x330')
    win.minsize(500, 300)
    try:
        from pathlib import Path
        import sys
        image = tk.PhotoImage(file=str(Path(getattr(sys, '_MEIPASS', Path(__file__).parent))/'assets'/'assembly-editor.png'))
        win.brand_image = image.subsample(6, 6)
        ttk.Label(win, image=win.brand_image).pack(pady=(16,4))
    except (OSError, tk.TclError):
        pass
    title = ttk.Label(win, font=('Segoe UI', 17, 'bold'))
    title.pack(pady=8)
    body = ttk.Label(win, justify='center', wraplength=530)
    body.pack(fill='x', padx=18)
    def refresh():
        win.title(tr('Over Assembly Editor'))
        title.configure(text='Assembly Editor ' + app.version)
        body.configure(text='CyberFirePulse\n\n' + tr('Alle rechten voorbehouden.') + '\n' + tr('Eigen gebruiksvoorwaarden. Zie LICENSE.txt in de installatiemap.'))
    win.refresh_language = refresh
    ttk.Button(win, text=tr('Sluiten'), command=win.destroy).pack(pady=16)
    refresh()
    return win
