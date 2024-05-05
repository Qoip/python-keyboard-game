# python-keyboard-game

## Description

My project is a multiplayer client-server game where players compete in typing words. Each player will see a pygame window divided in sections:
- The top section will display a field represented in a graph where vertices have different colors matching who owns them (at start players have 1 vertex each).
- The bootom section will display a words that the player has to type.
- On side theres a legend with players points and estimated time left.


Players choose which vertex to attack by clicking TAB and then typing name attached to the vertex (after clicking TAB the names will be displayed next to all the vertices can be attacked). Of course player can attack vertex only if it has an edge to his owned vertex.
Players attack vertices by typing the given words. Each typed word brings player closer to owning the vertex. To gain noones vertex you need to type as many words as it shows under it (its hp). However, other players can also attack the same vertex, so the player who types last needed word will own the vertex. Also you can attack other players vertices, but to steal one you have to type at least its hp, which shown above it, and its owner can defend it by typing words as well, each word typed on owned vertex will heal it by 1 hp.
Players main vertices are marked with a circle, and players name. Main vertices cannot be attacked by players.

Vertices differs by their size, which shows how hard (long) words you have to type to attack them.

Each owned vertex gives player points based on its size (every second), and the player with most points at the end of the game wins. Game limited by time setted by server.

Also theres a menu at start where you can change nickname, color and connect to server for client, set game config and start game when all players you want connected for server. Graph (field) is generated randomly on how many players are in the game. Max players is 4 currently.

## Features

Server and client are actually in the same program, but server has separeted code and client on same device will connect to it like other players.

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
  - see other players nicknames and points

## Classes

- `Vertex` - container that represents a vertex in the graph
- `Graph` - class that represents the field logic
- `View` - class that displays the pygame window for client
- `Server` - class that runs the server and controls connections to clients, sends and receives updates, validates data
- `Client` - class that runs the client, sends and receives data from server
