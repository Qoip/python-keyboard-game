from bin.graph import Graph

from typing import Tuple
import tkinter as tk
from tkinter import colorchooser, messagebox


class Client:
    def __init__(self):
        self.graph: Graph = None
        self.nickname: str = None
        self.color: Tuple[int, int, int] = None
        self.address: str = None
        self.run_menu()
        # self.connect()

    def run_menu(self) -> None:
        ''' Run menu '''
        root = tk.Tk()
        root.title("Menu")
        root.geometry("200x200")

        nickname_label = tk.Label(root, text="Nickname:")
        nickname_label.pack()
        nickname_entry = tk.Entry(root, width=20)
        nickname_entry.pack()

        def choose_color():
            color = colorchooser.askcolor(title="Choose Color")
            self.color = tuple(map(int, color[0]))

        color_button = tk.Button(root, text="Choose Color", command=choose_color)
        color_button.pack()

        address_label = tk.Label(root, text="Address:")
        address_label.pack()
        address_entry = tk.Entry(root, width=20)
        address_entry.pack()

        def save():
            self.nickname = nickname_entry.get()
            self.address = address_entry.get()
            if not self.nickname or not self.color or not self.address:
                messagebox.showerror("Error", "Fill all fields")
                return
            if len(self.nickname) > 14:
                messagebox.showerror("Error", "Nickname is too long (max 14)")
                return
            root.destroy()

        connect_button = tk.Button(root, text="Save", command=save)
        connect_button.pack()

        root.mainloop()
