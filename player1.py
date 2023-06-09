import socket
from gameboard import BoardClass

def connect_to_host() -> tuple[bool, socket.socket]:
    """Connects to server through ip/port specified by user

    The function will ask the user to enter the ip and port of the server
    they want to connect to. If server is found, the client will connect to
    the server and function will return True. If server is not found, user 
    will have option to connect through different ip/port or terminate the program.

    Args:
        None.

    Returns:
        True: client was able to sucessfully connect to server.
        False: client was unable to connect to server and user chose
        to terminate the program.
        connectionSocket: Socket object that can be used by other functions.
    
    """
    #Create connection socket object
    connectionSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    while True:
        try:
            ip = input("Enter host ip address: ")
            port = int(input("Enter host port number: "))
            connectionSocket.connect((ip,port))
            return True, connectionSocket
        except:
            choice = input("Connection could not be made. Would you like to try again (y/n): ").lower()
            while(choice != 'y' and choice != 'n'):
                print("Invalid input.")
                choice = input("Connection could not be made. Would you like to try again (y/n): ").lower()
            if choice == "n":
                return False, connectionSocket

def move(player1) -> tuple[int, int]:
    """Request input from user asking where they want to play their move.

    Args:
        player1 (BoardClass object): BoardClass object used to get information about the board.

    Returns:
        row: row of the board.
        col: column of the board.
    """
    possible_moves = "111213212223313233"
    while(True):
        choice = input("Please enter the row and column you want to choose (if you want top left, you would enter \"11\"): ")
        while(choice not in possible_moves or len(choice) != 2):
            print("Not a valid row/column.")
            choice = input("Please enter the row and column you want to choose (if you want top left, you would enter \"11\"): ")
        row = int(choice[0])-1
        col = int(choice[1])-1
        if(player1.isEmpty(row, col)):
            break
        else:
            print("Space is already taken. Please Try again.")
    return row, col

def requestNames(connectionSocket) -> tuple[str, str]:
    """Request input from user asking for username.

    This function asks the user to enter a username and then sends it
    to the server. Then, the function will wait for the server to send back
    their username. Finally, the function will return the user's username and
    the server's username.

    Args:
        connectionSocket (Socket object): socket object used to send and receive messages.

    Returns:
        p1_name: user's username.
        p2_name: server's username.
    """
    p1_name = input("Please enter your username (only alphanumeric): ")
    while(not p1_name.isalnum()):
        print("Please only enter alphanumeric usernames.")
        p1_name = input("Please enter your username: ")
    p1_name = (p1_name.encode())
    connectionSocket.send(p1_name)
    p1_name = p1_name.decode('ascii')
    p2_name = connectionSocket.recv(1024).decode('ascii')
    return p1_name, p2_name
    
def playAgain(connectionSocket) -> bool:
    """Request input from user asking if they want to play again.

    This function asks the user if they want to play the game again.
    If they respond with "y" the function will send "Play Again" to the 
    server and return True. If the user enters "n" the function will send
    "Fun Times" to the server and return False.

    Args:
        connectionSocket (Socket object): socket object used to send and receive messages.

    Returns:
        True: user want's to play again.
        False: user chose to end the game.
    
    """
    choice = input("Would you like to play another game (y/n): ").lower()
    while(choice != 'y' and choice != 'n'):
        print("Invalid input.")
        choice = input("Would you like to play another game (y/n): ").lower()
    if choice == 'y':
        connectionSocket.send(b'Play Again')
        return True
    else:
        connectionSocket.send(b'Fun Times')
        return False

def runGame(player1, p1_name, p2_name, connectionSocket) -> bool:
    """Runs the main game.

    Args:
        player1 (BoardClass object): BoardClass object used to get information about the board.
        p1_name (str): player1 username.
        p2_name (str): player2 username.
        connectionSocket (Socket object): socket object used to send and receive messages.

    Returns:
        playAgain(): The function will call playAgain() when a winning
        move is detected and playAgain() will return True or False depending
        on if the user wants to play again.
    """
    print(f'Current Board (Opponent: {p2_name}):')
    player1.printBoard()
    while(True):
        # Request input from user and send move to server
        row, col = move(player1)
        player1.updateGameBoard(row, col)
        connectionSocket.send((str(row) + str(col)).encode())
        print(f'Current Board (Opponent: {p2_name}):')
        player1.printBoard()

        player1.setLastMove(p1_name)

        # Check if move by player1 was a winning move or was the last possible move
        if(player1.isWinner()):
            return playAgain(connectionSocket)
        elif(player1.boardIsFull()):
            return playAgain(connectionSocket)
        
        # Receive move from server
        print("Waiting for oppoent to move...")
        player2Move = connectionSocket.recv(1024).decode('ascii')
        player1.updateGameBoard(int(player2Move[0]), int(player2Move[1]))
        print(f'Current Board (Opponent: {p2_name}):')
        player1.printBoard()

        player1.setLastMove(p2_name)

        # Check if move from server was a winning move or was the last possible move
        if(player1.isWinner()):
            return playAgain(connectionSocket)
        elif(player1.boardIsFull()):
            return playAgain(connectionSocket)

def runProgram() -> None:
    """Runs the entire program.

    Args:
        None.

    Returns:
        None.
    """
    startgame, connectionSocket = connect_to_host()
    if(startgame):
        p1_name, p2_name = requestNames(connectionSocket)
        player1 = BoardClass(p1_name, p2_name, 0, 0, 0, 0)
        cont = True
        while(cont):
            player1.resetGameBoard()
            player1.updateTotalGames()
            cont = runGame(player1, p1_name, p2_name, connectionSocket)
        player1.printStats()
    connectionSocket.close()

if __name__ == "__main__":
    runProgram()
