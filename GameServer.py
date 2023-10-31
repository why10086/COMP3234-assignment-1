import socket
import threading
import sys
import time
import random

class ServerMain:
    def __init__(self, serverPort, userinfo, roomNumber, roomMembers, guessResult):
        self.serverPort = serverPort
        self.userinfo = userinfo
        self.roomNumber = roomNumber
        self.roomMembers = roomMembers
        self.guessResult = guessResult
        
    def server_listen(self):
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverSocket.bind( ("", self.serverPort) )
        serverSocket.listen(5)
        print("The server is ready to receive")
        while True:
            client = serverSocket.accept()
            t = ServerThread(client, self.userinfo, self.roomNumber, self.roomMembers, self.guessResult)
            t.start()

class ServerThread(threading.Thread):
    lock = threading.Lock()
    def __init__(self, client, userinfo, roomNumber, roomMembers, guessResult):
        threading.Thread.__init__(self)
        self.flag = True
        self.client = client
        self.userinfo = userinfo
        self.roomNumber = roomNumber
        self.roomMembers = roomMembers
        self.guessResult = guessResult
        self.condition = threading.Condition()
        
    def run(self):
        connectionSocket, addr = self.client
        while self.flag:
            try:
                logininfo = connectionSocket.recv(1024).decode()
                authentication = self.login(logininfo)
                connectionSocket.send(authentication.encode())
                if authentication == "1001 Authentication successful":
                    break
            except socket.error:
                print("Connection error in authentication")
                self.flag = False
            
        room = -1
        while self.flag:
            try:
                command = connectionSocket.recv(1024)
                if (not command):
                    message = "4002 Unrecognized message"
                    connectionSocket.send(message.encode())
                    continue
                command = command.decode()
                message = self.inHall(command)
                connectionSocket.send(message.encode())
                if message.startswith("3001"):
                    continue
                if message.startswith("3013") or message.startswith("4002"):
                    continue
                if message.startswith("4001"):
                    break
                room = int(command.split(" ")[-1])
                if message.startswith("3011"):
                    while self.roomMembers[room] != 2:
                        time.sleep(1)
                        connectionSocket.send(message.encode())
                    message = "3012 Game started. Please guess true or false"
                    connectionSocket.send(message.encode())
                
            except socket.error:
                print("Connection error in the game hall")
                self.flag = False
                if room != -1:
                    with ServerThread.lock:
                        self.roomMembers[room] -= 1
                print(f"Number of clients in room #{room}: {self.roomMembers[room]}")
                continue
            
            try:
                guess = connectionSocket.recv(1024).decode()
                result = self.gameResult(room, guess)
                while result.startswith("4002"):
                    connectionSocket.send(result.encode())
                    guess = connectionSocket.recv(1024).decode()
                    result = self.gameResult(room, guess)
                    continue
                connectionSocket.send(result.encode())
                time.sleep(1)
                with ServerThread.lock:
                    guess = guess.split(" ")[-1]
                    self.guessResult[room].remove(guess)
                    self.roomMembers[room] -= 1
            except socket.error:
                print("Connection error in guess process")
                self.flag = False
                with ServerThread.lock:
                    self.guessResult[room].append("error")
                time.sleep(2)
                with ServerThread.lock:
                    self.guessResult[room].remove("error")
        connectionSocket.close()
            
    def login(self, logininfo):
        userinfo = self.userinfo
        logininfo = logininfo.split(' ')[1:]
        if len(logininfo) < 2:
            authentication = "1002 Authentication failed"
            return authentication
        logininfo = logininfo[0] + ":" + logininfo[-1]
        if logininfo in userinfo:
            authentication = "1001 Authentication successful"
        else:
            authentication = "1002 Authentication failed"
        return authentication

    def inHall(self, command):
        command = command.strip().split(' ')
        print(f"Command from client: {command}")
        if len(command) == 1:
            command = command[0]
            if command == "/list":
                message = "3001 " + str(self.roomNumber)
                for i in range(self.roomNumber):
                    message += " " + str(self.roomMembers[i])
            elif command == "/exit":
                message = "4001 Bye bye"
            else:
                message = "4002 Unrecognized message"
        elif len(command) == 2 and command[0] == "/enter":
            enterNumber = command[-1]
            if (not enterNumber.isdigit()) or (int(enterNumber) not in self.guessResult):
                message = "4002 Unrecognized message"
            else:
                enterNumber = int(enterNumber)
                if roomMembers[enterNumber] == 0:
                    message = "3011 Wait"
                    with ServerThread.lock:
                        self.roomMembers[enterNumber] += 1
                    print(f"Number of clients in room #{enterNumber}: {self.roomMembers[enterNumber]}")
                elif roomMembers[enterNumber] == 1:
                    message = "3012 Game started. Please guess true or false"
                    with ServerThread.lock:
                        self.roomMembers[enterNumber] += 1
                    print(f"Number of clients in room #{enterNumber}: {self.roomMembers[enterNumber]}")
                else:
                    message = "3013 The room is full" 
        else:
            message = "4002 Unrecognized message" 
        return message

    def checkRoom(self, roomNumber):
        while self.roomMembers[roomNumber] != 2:
            time.sleep(1)
        return
    
    def playGame(self, room, guess):
        if self.guessResult[room][0] == self.guessResult[room][1]:
            return "3023 The result is a tie"
        if "error" in self.guessResult[room]:
            return "3021 You are the winner"
        random.seed(room)
        random_number = random.choice(["true", "false"])
        if guess == random_number:
            return "3021 You are the winner"
        else:
            return "3022 You lost this game"
        
    def gameResult(self, room, guess):
        if guess != "/guess true" and guess != "/guess false":
            result = "4002 Unrecognized message"
            return result
        guess = guess.split(" ")[1]
        with ServerThread.lock:
            self.guessResult[room].append(guess)
        self.checkGuess(room)
        result = self.playGame(room, guess)
        
        return result
    
    def checkGuess(self, roomNumber):
        while len(self.guessResult[roomNumber]) != 2:
            time.sleep(1)
        print(f"The result client given in room #{roomNumber}: {self.guessResult[roomNumber]}")
        return
    
def readfile(filename):
    with open(filename, 'r') as f:
        content_list = f.readlines()
    userinfo = [line.strip() for line in content_list]
    # authentication = []
    # for user in userinfo:
    #     authentication.append(user.split(':'))
    return userinfo
    
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python GameServer.py <Server_port> <filename>")
        sys.exit(1)
    serverPort = int(sys.argv[1])
    filename = sys.argv[2]
    userinfo = readfile(filename)
    roomNumber = 20
    roomMembers = [0] * roomNumber
    guessResult = {}
    for i in range(roomNumber):
        guessResult[i] = []
    server = ServerMain(serverPort, userinfo, roomNumber, roomMembers, guessResult)
    server.server_listen()
    
