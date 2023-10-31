# COMP3234-Programming-Assignment-1
# Game Server and Client

This repository contains a Game Server and Client implementation in Python.

## Usage

### Game Server

To run the Game Server, use the following command format: `python GameServer.py <ServerPort> <filename>`

- `<ServerPort>`: Specify the port number on which the server will listen for incoming connections.
- `<filename>`: Specify the name of the file containing the user information.

### Game Client

To run the Game Client, use the following command format: `python GameClient.py <Hostname/IP address> <ServerPort>`

- `<Hostname/IP address>`: Specify the hostname or IP address of the server to connect to.
- `<ServerPort>`: Specify the port number on which the server is listening.

To terminate the Game Client program, use the `Ctrl+C` command in the terminal.

## Customization

The Game Server script (`GameServer.py`) provides the following customizable variables:

- `roomNumber`: Stores the number of rooms. You can modify this variable in the `main()` function.
- `roomMembers`: Stores the number of members in each room.
- `guessResult`: Stores the guess made by each member in each room.

Feel free to modify these variables according to your needs.

## Error Handling

If the system encounters a connection exception, the error message or location will be displayed in the terminal. If the server crashes, the client will display the error message after completing the input.
