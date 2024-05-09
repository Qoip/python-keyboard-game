""" Server module """

from bin.graph import Graph

import tkinter as tk
from tkinter import messagebox
import random
from typing import Tuple, List, Dict, Any, Set
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
        self.game_start_time: float = None  # also game started flag

        self.port = random.randrange(10000, 60000)
        self.address: str = f"127.0.0.1:{self.port}"
        self.server: asyncio.AbstractServer = None
        self.is_serving: bool = False
        self.active_connections: Set[asyncio.StreamWriter] = set()

        self.players_address: Dict[Tuple[str, int], str] = {}
        self.client_updates: asyncio.Queue[Tuple[str, Dict[str, Any]]] = asyncio.Queue()

    async def run(self):
        server_thread = threading.Thread(target=lambda: asyncio.run(self.start_server()))
        server_thread.start()

        await self.run_menu()
        self.graph = Graph()
        self.graph.generate(self.players, self.bounds, self.dense)
        self.legend: Dict[str, int] = self.get_legend()

        print("[settings]", "dense:", self.dense, "bounds:", self.bounds, "time:", self.time)
        print("[settings]", "players:", self.players, "color_scheme:", self.color_scheme)
        print("[settings]", "legend:", self.legend, "players_address:", self.players_address)

        # self.game_start_time = asyncio.get_event_loop().time()
        # while asyncio.get_event_loop().time() - self.game_start_time < self.time:
        #     await self.game_loop()

        self.is_serving = False
        server_thread.join()

    async def game_loop(self):
        """ Game loop """

    async def start_server(self):
        """ Start server listening """
        self.server = await asyncio.start_server(self.handle_update, '127.0.0.1', self.port)
        print("started on port", self.port)
        self.is_serving = True
        while self.is_serving:
            await asyncio.sleep(0.1)
        self.server.close()
        for connection in self.active_connections:
            connection.close()
        await self.server.wait_closed()

    async def handle_update(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        self.active_connections.add(writer)
        raw_data = await reader.read(1024)
        addr: Tuple[str, int] = writer.get_extra_info('peername')
        print("[handler]", f"get {raw_data} from {addr}")
        data: Dict[str, Any]
        try:
            data = json.loads(raw_data.decode())
        except json.JSONDecodeError:
            print("[handler]", "invalid data recieved")
            writer.write("invalid".encode())
            await writer.drain()
            return

        if data.get("command") == "connect" and not self.game_start_time:
            if data.get("nickname") in self.players:
                print("[handler]", "nickname exists")
                writer.write("nickname exists".encode())
                await writer.drain()
                return
            print("[handler]", "new player", data.get("nickname"))
            self.players.append(data.get("nickname"))
            self.color_scheme[data.get("nickname")] = tuple(data.get("color"))
            self.players_address[addr] = data.get("nickname")
            writer.write("connected".encode())
            await writer.drain()
            return

        nickname = self.players_address.get(addr, None)
        if nickname is None:
            print("[handler]", "unknown player query")
            writer.write("unknown".encode())
            await writer.drain()
            return

        if data.get("command") == "get":
            print("[handler]", "get query from", nickname)
            response = ""
            writer.write(response.encode())
            await writer.drain()
            return
        print("[handler]", f"'{data.get("command")}' query from {nickname}")
        await self.client_updates.put((nickname, data))
        writer.write("recieved".encode())
        await writer.drain()

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
        x_entry.insert(0, "500")
        x_entry.pack()
        y_label = tk.Label(root, text="Y:")
        y_label.pack()
        y_entry = tk.Entry(root, width=20)
        y_entry.insert(0, "500")
        y_entry.pack()

        dense_label = tk.Label(root, text="Density (there will dense*(players+1) vertices in graph):")
        dense_label.pack()
        dense_entry = tk.Entry(root, width=20)
        dense_entry.pack()
        dense_entry.insert(0, "3")

        time_label = tk.Label(root, text="Game time (seconds):")
        time_label.pack()
        time_entry = tk.Entry(root, width=20)
        time_entry.insert(0, "300")
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
