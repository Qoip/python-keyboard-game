""" Server module """

from bin.graph import Graph

import tkinter as tk
from tkinter import messagebox
import random
from typing import Tuple, List, Dict, Any
import asyncio
import threading
import json


class Server:

    def __init__(self):
        self.bounds: Tuple[int, int] = None
        self.dense: int = None
        self.time: int = None
        self.graph: Graph = None
        self.players: List[str] = []
        self.color_scheme: Dict[str, Tuple[int, int, int]] = {}

        self.port = random.randrange(10000, 60000)
        self.address: str = f"127.0.0.1:{self.port}"
        self.server: asyncio.AbstractServer = None
        self.is_serving: bool = False

        self.players_address: Dict[str, str] = {}
        self.client_updates: asyncio.Queue[str] = asyncio.Queue()

    async def run(self):
        server_thread = threading.Thread(target=lambda: asyncio.run(self.start_server()))
        server_thread.start()

        await self.run_menu()
        self.graph = Graph()
        self.graph.generate(self.players, self.bounds, self.dense)
        self.legend: Dict[str, int] = self.get_legend()

        print(self.players, self.color_scheme, self.legend, self.players_address)
        print(self.dense, self.bounds, self.time)

        # await self.stop_server()
        self.is_serving = False
        server_thread.join()

    async def start_server(self):
        """ Start server listening"""
        self.server = await asyncio.start_server(self.handle_update, '127.0.0.1', self.port)
        print("port", self.port)
        self.is_serving = True
        async with self.server:
            while self.is_serving:
                await asyncio.sleep(0.1)

    async def handle_update(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        data = await reader.read(1024)
        message = data.decode()
        addr = writer.get_extra_info('peername')
        print(f"get {message} from {addr}")
        await self.client_updates.put((addr, message))
        writer.close()

    async def run_menu(self) -> None:
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

        start_clicked = False

        def update_players():
            while not self.client_updates.empty():
                addr, message = self.client_updates.get_nowait()
                data: Dict[str, Any] = json.loads(message)
                if data.get("command") == "connect":
                    self.players.append(data.get("nickname"))
                    self.color_scheme[data.get("nickname")] = tuple(data.get("color"))
                    self.players_address[data.get("nickname")] = addr
            players_label.config(text=f"{self.players}")
            if not start_clicked:
                root.after(1000, update_players)

        update_players()
        root.mainloop()

    def get_legend(self) -> Dict[str, int]:
        ''' Get legend '''
        legend = {
            "time": self.time,
        }
        for player in self.players:
            legend[player] = 0
        return legend
