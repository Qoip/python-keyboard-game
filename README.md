# python-keyboard-game

## Description

My project is a multiplayer client-server game where players compete in typing words. Each player will see a pygame window divided in two sections:
- The top section will display a field represented in a graph where verticies have different colors matching who owns them (at start players have 1 vertex each).
- The bootom section will display a words that the player has to type.


Players choose which vertex to attack by clicking TAB and then typing name attached to the vertex (after clicking TAB the names will be displayed next to  all the vertices can be attacked). Of course player can attack vertex only if it has an edge to his owned vertex.
Players attack verticies by typing the given words. Each typed word brings player closer to owning the vertex. To gain noones vertex you need to type as many words as it shows under it. However, other players can also attack the same vertex, so the player who types last needed word will own the vertex. Also you can attack other players verticies, but to steal one you have to type many words (at least its hp, which shown under it), and its owner can defend it by typing words as well, each word typed on owned vertex will heal it by 1 hp.
The player 'dies' when he loses his main vertex, which was his start vertex.
Verticies differs by their size, which shows how hard words you have to type to own them.

Also theres a menu at start where you can change nickname, connect to server or create game and start it when all players connected. Graph (field) is generated randomly on how many players are in the game.

approximate scheme image:
![pic](https://github.com/Qoip/python-keyboard-game/assets/110194047/41e84037-210d-48cb-bbec-333abc1b8027)

## Features

Server and client are actually in the same program, but server has separeted code and client on same device will connect to it like other players.

server:
- create game
- start game

client:
- connect to server
- change nickname
- ingame:
  - type words to attack verticies
  - choose which vertex to attack
  - see field and other players verticies and their hp
  - see other players nicknames

## Classes

- `Game` - main class that controls the game and validates data from clients
- `Server` - class that runs the server and controls connections to clients, sends and receives updates
- `Client` - class that runs the client
- `View` - class that displays the game for client
