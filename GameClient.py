import socket
import sys

class ClientMain:
    def __init__(self, serverName, serverPort):
        self.serverName = serverName
        self.serverPort = serverPort
    
    def login(self):
        username = input("Please input your username:\n")
        password = input("Please input your password:\n")
        login = "/login " + username + " " + password
        return login
    
    def inHall(self):
        command = input("Please enter a command </list> </enter target_room_number>:")
        return command
    
    def guessInput(self):
        guess = input()
        return guess

    def run(self):
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect( (self.serverName, self.serverPort) )
        while True:
            logininfo = self.login()
            clientSocket.send(logininfo.encode())
            authentication = clientSocket.recv(1024).decode()
            print(authentication)
            if authentication == "1001 Authentication successful":
                break
        
        while True:
            # command = self.inHall()
            command = input("Please enter a command </list> </enter target_room_number>:")
            clientSocket.send(command.encode())
            message = clientSocket.recv(1024).decode()
            print(message)
            if message.startswith("3001"):
                continue
            while message.startswith("3011"):
                message = clientSocket.recv(1024).decode()
                if message.startswith("3012"):
                    print(message)
            if message.startswith("3013") or message.startswith("4002"):
                continue
            if message.startswith("4001"):
                break
            while True:
                guess = self.guessInput()
                clientSocket.send(guess.encode())
                result = clientSocket.recv(1024).decode()
                print(result)
                if not result.startswith("4002"):
                    break
        print("Client ends")
        
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python GameClient.py <Hostname/IP address> <ServerPort>")
        sys.exit(1)
    serverName = sys.argv[1]
    serverPort = int(sys.argv[2])
    client = ClientMain(serverName, serverPort)
    client.run()

