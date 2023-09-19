from __future__ import annotations
from .listbox import ExListbox
from tkinter import Tk, ttk
from typing import Sequence
from .utils import StringVar
import tkinter as tk

def _on_listbox_item_selected(obj, entry: str | float, **kw):
    print(f"Entry selected: {entry}")

def _on_listbox_items_selected(obj, entries: Sequence[str | float], **kw):
    print(f"Entries selected: {entries}")

def _change_listbox_selectmode(lbx: ExListbox):
    var = StringVar(name="SELECTMODE")
    lbx.configure(selectmode=var.get())

def _on_listbox_values_set(obj, values: Sequence[str | float], **kw):
    print(f"Values set: {values}")

def _change_listbox_values(lbx: ExListbox, button: ttk.Button):
    lbx.set_values([6, 7, 8, 9, 10])
    button.state(('disabled',))

def run_test():
    root = Tk()

    frame = ttk.Frame()
    frame.pack(fill=tk.BOTH, expand=True)

    lbx = ExListbox(frame)
    lbx.pack()

    lbx.set_values([1, 2, 3, 4, 5])

    lbx.on_item_selected.connect(_on_listbox_item_selected)
    lbx.on_items_selected.connect(_on_listbox_items_selected)
    lbx.on_values_set.connect(_on_listbox_values_set)

    var = StringVar(name="SELECTMODE", value="browse")

    ttk.Radiobutton(frame, variable=var, command=lambda: _change_listbox_selectmode(lbx),
                    value="browse", text="Browse").pack()
    ttk.Radiobutton(frame, variable=var, command=lambda: _change_listbox_selectmode(lbx),
                    value="multiple", text="Multiple").pack()

    button = ttk.Button(frame, text="Change Values")
    button.configure(command=lambda: _change_listbox_values(lbx, button))
    button.pack()

    root.mainloop()
