import tkinter as tk
import asyncio

from src.client import Client
from src.server import Server


def start_server(root: tk.Tk):
    root.destroy()
    server = Server()
    asyncio.run(server.run())


def start_client(root: tk.Tk):
    root.destroy()
    client = Client()
    asyncio.run(client.run())


def main():
    root = tk.Tk()

    server_button = tk.Button(root, text="Server", command=lambda: start_server(root))
    server_button.pack()
    client_button = tk.Button(root, text="Client", command=lambda: start_client(root))
    client_button.pack()

    root.mainloop()


if __name__ == "__main__":
    asyncio.run(main())
