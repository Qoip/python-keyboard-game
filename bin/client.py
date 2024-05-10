""" Client module """

from bin.graph import Graph
from bin.view import View

from typing import Tuple, Dict, List
import tkinter as tk
from tkinter import colorchooser, messagebox
import asyncio
import json
import threading
import ast


class Client:
    def __init__(self):
        self.graph: Graph = None
        self.color_scheme: Dict[str, Tuple[int, int, int]] = None
        self.legend: Dict[str, int] = None

        self.nickname: str = None
        self.color: Tuple[int, int, int] = None
        self.address: str = None

        self.reader: asyncio.StreamReader = None
        self.writer: asyncio.StreamWriter = None

    async def run(self):
        ''' Run client '''
        connected = False
        while not connected:
            self.run_menu()
            self.reader, self.writer = await asyncio.open_connection(*self.address.split(':'))
            connect_data = f'{{"command": "connect", "nickname": "{self.nickname}", "color": {list(self.color)}}}'
            response = await self.query(connect_data)
            if response == "connected":
                connected = True
            else:
                messagebox.showerror("Error", response)
        message = ""
        while message != "game started":
            message = await self.query('{"command": "get", "argument": "state"}')
            await asyncio.sleep(1)
        self.graph = Graph()
        self.graph.from_dict(json.loads(await self.query('{"command": "get", "argument": "graph"}')))
        self.color_scheme = json.loads(await self.query('{"command": "get", "argument": "color_scheme"}'))
        self.legend = json.loads(await self.query('{"command": "get", "argument": "legend"}'))

        self.view = None
        self.lock = threading.Lock()
        self.view: View = None
        view_thread = threading.Thread(target=self.create_view)
        view_thread.start()
        while self.view is None:
            await asyncio.sleep(0.2)
        new_words: List[str] = []
        while self.view.legend.get("time") > 0:
            while not self.view.events.empty():
                event = self.view.events.get()
                if event[0] == "attack":
                    await self.query('{"command": "attack", "argument": ' + str(event[1]) + '}')
                elif event[0] == "change":
                    await self.query('{"command": "change", "argument": ' + str(event[1]) + '}')
                    response = await self.query('{"command": "get", "argument": "words"}')
                    if response.startswith("["):
                        new_words = ast.literal_eval(response)

            await asyncio.sleep(0.5)
            new_graph = json.loads(await self.query('{"command": "get", "argument": "graph"}'))
            new_legend = json.loads(await self.query('{"command": "get", "argument": "legend"}'))
            with self.lock:
                self.view._graph.from_dict(new_graph)
                self.view._legend = new_legend
                if new_words:
                    self.view.words = new_words
                    new_words = []
        self.view.running = False
        view_thread.join()

    def create_view(self):
        self.view = View(self.color_scheme, self.graph, self.nickname, self.legend)
        self.view.lock = self.lock
        self.view.run()

    async def query(self, data: str) -> str:
        ''' Query server '''
        self.writer.write(data.encode())
        await self.writer.drain()
        response = await self.reader.read(4096)
        return response.decode()

    def run_menu(self) -> None:
        ''' Run menu '''
        root = tk.Tk()
        root.title("Client menu")
        root.geometry("200x200")
        root.resizable(False, False)

        nickname_label = tk.Label(root, text="Nickname:")
        nickname_label.pack()
        nickname_entry = tk.Entry(root, width=20)
        nickname_entry.insert(0, self.nickname if self.nickname else "")
        nickname_entry.pack()

        def choose_color():
            color = colorchooser.askcolor(title="Choose Color")
            self.color = tuple(map(int, color[0]))

        color_button = tk.Button(root, text="Choose Color", command=choose_color)
        color_button.pack()

        address_label = tk.Label(root, text="Address:")
        address_label.pack()
        address_entry = tk.Entry(root, width=20)
        address_entry.insert(0, self.address if self.address else "")
        address_entry.pack()

        def save():
            if not nickname_entry.get() or not address_entry.get() or not self.color:
                messagebox.showerror("Error", "Fill all fields")
                return
            if len(nickname_entry.get()) > 14:
                messagebox.showerror("Error", "Nickname is too long (max 14)")
                return
            self.nickname = nickname_entry.get()
            self.address = address_entry.get()
            root.destroy()

        connect_button = tk.Button(root, text="Save", command=save)
        connect_button.pack()
        root.protocol("WM_DELETE_WINDOW", lambda: exit())

        root.mainloop()
