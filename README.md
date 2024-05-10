# python-keyboard-game

## Description

My project is a multiplayer client-server game where players compete in typing words. Each player will see a pygame window divided in sections:
- The top section will display a field represented in a graph where vertices have different colors matching who owns them (at start players have 1 vertex each).
- The bootom section will display a words that the player has to type.
- On side theres a legend with players points and estimated time left.


Players choose which vertex to attack by clicking TAB and then typing name attached to the vertex (after clicking TAB the names will be displayed next to all the vertices can be attacked). Of course player can attack vertex only if it has an edge to his owned vertex.
Players attack vertices by typing the given words. Each typed word brings player closer to owning the vertex. To gain noones vertex you need to type as many words as it shows under it (its hp). However, other players can also attack the same vertex, so the player who types last needed word will own the vertex. Also you can attack other players vertices, but to steal one you have to type at least its hp, which shown above it, and its owner can defend it by typing words as well, each word typed on owned vertex will heal it by 1 hp.
Players main vertices are marked with a circle and players name under it. Main vertices cannot be attacked by players.

Vertices differs by their size, which shows how hard (long) words you have to type to attack them.

Each owned vertex gives player 1 point every second, and the player with most points at the end of the game wins. Game limited by time setted by server.

Also theres a menu at start where you can change nickname, color and connect to server for client, set game config and start game when all players you want connected for server. Graph (field) is generated randomly on how many players are in the game. Max players is 4 currently.

## Features

server:
- create game and change its settings
- start game

client:
- connect to server
- change nickname and color
- ingame:
  - type words to attack vertices
  - choose which vertex to attack
  - see field and other players vertices and their hp
  - see other players nicknames and points + time left

## Classes

Key methods and fields of classes:

- `Vertex` - container that represents a vertex in the graph
  - `to_dict` and `from_dict`
  - fields:
    - `x`, `y` - position on the field
    - `hp`
    - `name`
    - `owner` - player that owns the vertex
    - `is_main` - if the vertex is main for any player
    - `size` - size of the vertex displayed and its hardness
- `Graph` - class that represents the field logic
  - fields:
    - `vertices` - list of vertices
    - `edges` - list of edges
    - `bounds` - size of the field
    - `dense` - how many edges are between vertices
  - `to_dict` and `from_dict`
  - `generate` - generates a random graph based on number of players
  - `distance` - calculates distance between two vertices
  - `reachable` - checks if vertex is reachable from player
  - `get_main` - returns main vertex for player
  - `count` - counts vertices owned by player
- `View` - class that displays the pygame window for client
  - fields:
    - `color_scheme` - list of colors for players
    - `legend_` - legend with players points and estimated time
    - `graph_` - Graph object
    - `words` - list of current words to type
    - `my_name` - players nickname
    - `current_vertex` - vertex that player is attacking
  - `update` - updates the window
  - `run` - main loop of the window
- `Server` - class that runs the server and controls connections to clients, sends and receives updates, validates data
  - `run` - main of the server
  - `start_server` - starts the listener to connections from clients
  - `game_loop` - main loop of the game
  - `run_menu` - runs the menu for server
- `Client` - class that runs the client, sends and receives data from server
  - fields:
    - `nickname` - players nickname
    - `color` - players color
    - `graph` - Graph object
    - `color_scheme` - list of colors for players
    - `legend` - legend with players points and estimated time
  - `query` - sends request to server
  - `run_menu` - runs the menu for client
- `start.py` - main module - chooses if to run server or client
  - `start_server` - starts the server
  - `start_client` - starts the client
