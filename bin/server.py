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
        self.current_vertex: Dict[str, int] = {}  # nickname -> vertex_index

        self.port = random.randrange(10000, 60000)
        self.address: str = f"127.0.0.1:{self.port}"
        self.server: asyncio.AbstractServer = None
        self.is_serving: bool = False
        self.active_connections: Set[asyncio.StreamWriter] = set()
        self.players_address: Dict[Tuple[str, int], str] = {}  # address -> nickname

        self.game_start_time: float = None  # also game started flag
        self.client_updates: asyncio.Queue[Tuple[str, Dict[str, Any]]] = asyncio.Queue()  # nickname -> json query

    async def run(self):
        server_thread = threading.Thread(target=lambda: asyncio.run(self.start_server()))
        server_thread.start()

        await self.run_menu()
        print("[main]", "dense:", self.dense, "bounds:", self.bounds, "time:", self.time)
        print("[main]", "players:", self.players, "color_scheme:", self.color_scheme)
        print("[main]", "legend:", self.legend, "players_address:", self.players_address)

        self.graph = Graph()
        self.graph.generate(self.players, self.bounds, self.dense)
        self.legend: Dict[str, int] = self.get_legend()
        self.current_vertex = {player: self.graph.get_main(player) for player in self.players}

        print("[main]", "game started")
        self.game_start_time = asyncio.get_event_loop().time()
        while self.estimated_time() > 0:
            await self.game_loop()

        self.is_serving = False
        server_thread.join()

    async def game_loop(self):
        """ Game loop """
        if self.estimated_time() != self.legend["time"]:
            self.legend["time"] = self.estimated_time()
            print("[game]", "time left:", self.estimated_time())
            for player in self.players:
                self.legend[player] += self.graph.count(player)

        while self.client_updates.qsize() > 0:
            nickname, data = await self.client_updates.get()
            if data.get("command") == "change":
                try:
                    vertex_index = int(data.get("argument"))
                    assert vertex_index < len(self.graph.vertices)
                    assert vertex_index >= 0
                    assert self.graph.reachable(nickname, vertex_index)
                except (ValueError, AssertionError) as exc:
                    print("[game]", f"invalid change from player {nickname}: {data}\nerror: {exc}")
                    continue
                self.current_vertex[nickname] = vertex_index
                vertex_name = self.graph.vertices[vertex_index].name
                print("[game]", f"player {nickname} changed current to {vertex_name} ({vertex_index})")
            elif data.get("command") == "attack":
                try:
                    vertex_index = int(data.get("argument"))
                    assert vertex_index == self.current_vertex[nickname]
                    assert not self.graph.vertices[vertex_index].is_main
                except (ValueError, AssertionError) as exc:
                    print("[game]", f"invalid attack from player {nickname}: {data}\nerror: {exc}")
                    continue
                vertex_name = self.graph.vertices[vertex_index].name
                if self.graph.vertices[vertex_index].owner is nickname:
                    self.graph.vertices[vertex_index].hp += 1
                    print("[game]", f"player {nickname} healed vertex {vertex_name} ({vertex_index})")
                else:
                    self.graph.vertices[vertex_index].hp -= 1
                    print("[game]", f"player {nickname} attacked vertex {vertex_name} ({vertex_index})")
                    if self.graph.vertices[vertex_index].hp == 0:
                        self.graph.vertices[vertex_index].hp = 3
                        old_owner = self.graph.vertices[vertex_index].owner
                        self.graph.vertices[vertex_index].owner = nickname
                        print("[game]", f"player {nickname} captured vertex {vertex_name} ({vertex_index})")

                        if old_owner is not None:  # check if old owner needs to force change vertex
                            if not self.graph.reachable(old_owner, self.current_vertex[old_owner]):
                                self.current_vertex[old_owner] = vertex_index  # move to captured vertex
                                print("[game]", f"player {old_owner} forced to change vertex")

    def estimated_time(self) -> int:
        """ Estimated time to end game """
        return self.time - int(asyncio.get_event_loop().time() - self.game_start_time)

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
            argument = data.get("argument")
            if argument == "graph":
                response = json.dumps(self.graph.to_dict())
            elif argument == "legend":
                response = json.dumps(self.get_legend())
            elif argument == "color_scheme":
                response = json.dumps(self.color_scheme())
            else:
                print("[handler]", "invalid get query from", nickname)
                return
            print("[handler]", "get query from", nickname)
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
