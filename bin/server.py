""" Server module """

from bin.graph import Graph

import tkinter as tk
from tkinter import messagebox
from typing import Tuple, List, Dict


class Server:

    def __init__(self):
        self.bounds: Tuple[int, int] = None
        self.dense: int = None
        self.time: int = None

        self.address: str = ""  # TODO: get address
        self.players: List[str] = []

        self.run_menu()
        self.graph = Graph()
        self.graph.generate(self.players, self.bounds, self.dense)
        self.color_scheme: Dict[str, Tuple[int, int, int]] = None
        self.legend: Dict[str, int] = None

    def run_menu(self) -> None:
        ''' Run menu '''
        root = tk.Tk()
        root.title("Server menu")
        root.geometry("500x300")
        root.resizable(False, False)

        bounds_label = tk.Label(root, text="Bounds:")
        bounds_label.pack()
        x_label = tk.Label(root, text="X:")
        x_label.pack()
        x_entry = tk.Entry(root, width=20)
        x_entry.pack()
        y_label = tk.Label(root, text="Y:")
        y_label.pack()
        y_entry = tk.Entry(root, width=20)
        y_entry.pack()

        dense_label = tk.Label(root, text="Density (there will dense*(players+1) vertices in graph):")
        dense_label.pack()
        dense_entry = tk.Entry(root, width=20)
        dense_entry.pack()

        time_label = tk.Label(root, text="Game time (seconds):")
        time_label.pack()
        time_entry = tk.Entry(root, width=20)
        time_entry.pack()

        def start():
            if not x_entry.get() or not y_entry.get() or not dense_entry.get() or not time_entry.get():
                messagebox.showerror("Error", "Fill all fields")
                return
            self.bounds = (int(x_entry.get()), int(y_entry.get()))
            self.dense = int(dense_entry.get())
            self.time = int(time_entry.get())
            global start_clicked
            start_clicked = True
            root.destroy()

        connect_button = tk.Button(root, text="Start game", command=start)
        connect_button.pack()

        divider = tk.Frame(root, height=2, bd=1, relief=tk.SUNKEN)
        divider.pack(fill=tk.X, padx=5, pady=5)

        address_label = tk.Label(root, text=f"Address: {self.address}")
        address_label.pack()

        players_label = tk.Label(root, text=f"{self.players}")
        players_label.pack()

        def update_players():
            # TODO: update players
            players_label.config(text=f"{self.players}")
            if not start_clicked:
                root.after(1000, update_players)
        start_clicked = False

        update_players()
        root.mainloop()

