import socket
import threading

# SERVER VARIABLES
# We're setting the values of all these connection variables so that we're able
# to connect to the server
HEADER = 64
FORMAT = 'utf-8'

# USER COMMANDS
DISCONNECT_MESSAGE = '!exit'            # exit server
DISCONNECT_ACK_MESSAGE = '!exit_ack'    # exit acknowledgement
RETRIEVE_MESSAGE = '!retrieve'          # retrieve message
POST_MESSAGE = '!post'                  # post message
LIST_GROUPS = '!groups'                 # lists all available groups
LIST_GROUPMEMBERS = '!groupmembers'     # lists all group members in specific group
LIST_MYGROUPS = '!mygroups'             # lists groups that member is in
JOIN_GROUP_COMMAND = '!groupjoin'       # allow user to join new group
LEAVE_GROUP_MESSAGE = '!leavegroup'     # allow user to leave group
groups = []  # array that locally holds all users

# SET UP CONNECTION
# sets up socket and prompts the user to use the !connect command to connect to the server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connectStr = input("Welcome to the message board. Type !connect to connect to the server:\n")
while connectStr != "!connect":  # loops until client types !connect command
    connectStr = input("Type !connect to connect to the server:\n")

# CONNECT TO SERVER
# loops until connection has been successfully created
# has error exception handling
connected = False
while not connected:
    try:
        serverAddr = input("Enter the server address: ")
        portNum = input("Enter the port number: ")
        ADDR = (serverAddr, int(portNum))
        client.connect(ADDR)
        connected = True  # exit loop
    except socket.error as exc:
        print(f"Caught exception socket.error : {exc}")
    except TypeError as msg:
        print(f"Type Error: {msg}")
    except ValueError as msg:
        print(f"Type Error: {msg}")

# INITIAL SERVER SET UP
# User is prompted to enter a username. Username must not already be in use.
# User is prompted to join an existing group. The group entered should be existing and valid.
# User is added to the corresponding group and username arrays
print("\nSUCCESSFULLY CONNECTED TO SERVER\n")
name = input('Enter your username: ')
client.send(name.encode())
msg = client.recv(2048).decode(FORMAT)
if msg == "!VALID!":
    print("You entered a valid username.\n")
while msg == "!INVALID!":
    print("That username is already in use, pick another username.\n")
    name = input('Enter your username: ')
    client.send(name.encode())
    msg = client.recv(2048).decode(FORMAT)
strRooms = client.recv(2048).decode(FORMAT)
print(strRooms)
userRoomInitial = input('Enter the Group number you want to join: ')
while((userRoomInitial in groups) or (not userRoomInitial.isdigit()) or ( 0 > int(userRoomInitial)) or (int(userRoomInitial) >= 5)):
    userRoomInitial = input('Enter a valid integer for the Group: ')
client.send(userRoomInitial.encode())
msg = client.recv(2048).decode(FORMAT)
if msg == "!VALIDROOM!":
    print("You entered a valid Group number.\n")
while msg == "!INVALIDROOM!":
    print("That Group number is invalid, pick another Group number.\n")
    userRoomInitial = input('Enter the Group you want to join: ')
    client.send(userRoomInitial.encode())
    msg = client.recv(2048).decode(FORMAT)
groups.append(userRoomInitial)


# NAME: listen
# ARGS: None
# FUNCTIONALITY: This function waits to recieve messages from the server and
# the prints the messages
def listen():
    # boolean used to control the listening loop
    listening = True
    while listening:
        msg = client.recv(2048).decode(FORMAT)
        # if the message received is the disconnect ack, set the looping
        # variable to false so the thread will stop listening. Otherwise
        # print the message as normal.
        if msg == DISCONNECT_ACK_MESSAGE:
            listening = False
        else:
            print(msg)


# NAME: send
# ARGS: None
# FUNCTIONALITY: This function takes in input and sends it as a message to the
# server
def send():
    while True:
        message = input()
        messageUser = ("[" + name + "] " + message)
        client.send(messageUser.encode(FORMAT))


# MAIN THREAD
# Here we spin off a thread to listen for messages and then have the main
# program wait for user input to send messages.
if __name__ == '__main__':
    thread = threading.Thread(target=listen, daemon=True)
    thread.start()

    connected = True  # Boolean variable used to control the loop

    # MAIN LOOP OF CLIENT PROGRAM
    while connected:
        # wait for user input
        message = input()

        # DISCONNECT MESSAGE
        # check if the user sent the disconnect message and removes from the server
        # sets main loop condition to false
        if message == DISCONNECT_MESSAGE:
            connected = False
            client.send(message.encode(FORMAT))
        # POST MESSAGE
        # prompts the user a message, subject, and group to send to the server
        # User must be in the group specified
        elif message == POST_MESSAGE:
            if not groups:
                print("You are not in any Groups. You cannot post to Group.")
            else:
                client.send(message.encode(FORMAT))
                post_txt = input('Enter your message text: ')
                client.send(post_txt.encode(FORMAT))
                post_subj = input('Enter your message subject: ')
                client.send(post_subj.encode(FORMAT))
                post_board = input('Which Group board to post to: ')
                while post_board not in groups:
                    post_board = input('You are not in that Group, enter a valid Group number to post to: ')
                client.send(post_board.encode(FORMAT))
                client.send(name.encode(FORMAT))
        # RETRIEVE MESSAGE
        # prompts the user to enter a post ID
        # the User must be in the group of the post ID
        # client sends list of groups joined to the server
        elif message == RETRIEVE_MESSAGE:
            if not groups:
                print("You are not in any Groups, you cannot retrieve any messages.")
            else:
                client.send(message.encode(FORMAT))
                msgID = input('Enter the post ID: ')
                while not msgID.isdigit():
                    msgID = input('Invalid post ID, enter a valid integer:  ')
                client.send(msgID.encode(FORMAT))
                groupList = []
                for i in range(len(groups)):
                    groupList.append(f'{groups[i]}')
                mySeparator = " "
                strGroupList = mySeparator.join(groupList)
                client.send(strGroupList.encode(FORMAT))
        # LIST_GROUPS
        # prints out a list of all available groups
        elif message == LIST_GROUPS:
            print("All available Groups:")
            if not groups:
                print("Group: 0, Group: 1, Group: 2, Group: 3, Group: 4")
            else:
                client.send(message.encode(FORMAT))
                groupList = []
                for i in range(len(groups)):
                    groupList.append(f'{groups[i]}')
                mySeparator = " "
                strGroupList = mySeparator.join(groupList)
                client.send(strGroupList.encode(FORMAT))
        # LIST_GROUPS
        # prints out a list of all available groups
        elif message == LIST_GROUPMEMBERS:
            if not groups:
                print("You are not in any Groups. You cannot view Group members.")
            else:
                client.send(message.encode(FORMAT))
                groupChooseView = input('Enter which Group number to list current members: ')
                while groupChooseView not in groups:
                    groupChooseView = input('You are not in that Group, enter a valid Group number: ')
                client.send(groupChooseView.encode(FORMAT))
        # LIST MY GROUPS
        # prints out a list of current groups the client is in
        elif message == LIST_MYGROUPS:
            if not groups:
                print("You are not in any Groups.")
            else:
                print("Groups currently in:")
                sortedList = sorted(groups)
                sortedStrList = ', '.join(sortedList)
                print(sortedStrList)
        # JOIN GROUP
        # prompts the user for which group they'd like to join
        # input must be a valid integer, it should be within range of groups
        # input should be a different group than the ones already joined
        elif message == JOIN_GROUP_COMMAND:
            if len(groups) == 5:
                print('There are no new groups for you to join.')
            else:
                client.send(message.encode(FORMAT))
                newRoom = input('Enter a valid Group to join: ')
                while((newRoom in groups) or (not newRoom.isdigit()) or ( 0 > int(newRoom)) or (int(newRoom) >= 5)):
                    newRoom = input("You cannot join that group. Enter a valid group number (0 -4) that you are not already in: ")
                if newRoom not in groups:
                    client.send(newRoom.encode(FORMAT))
                groups.append(newRoom)
        # OTHER / INVALID COMMAND
        # if the user inputs an invalid command, print to console.
        elif message == LEAVE_GROUP_MESSAGE:
            if not groups:
                print("You are not in any Groups.")
            else:
                client.send(message.encode(FORMAT))
                # prompt the user for the group they want to leave and ensure that it's valid
                room_to_leave = input('Enter the id of the group you want to leave: ')
                while room_to_leave not in groups:
                    print('Invalid room id. Please enter a valid id.')
                    room_to_leave = input('Enter the id of the group you want to leave: ')
                client.send(room_to_leave.encode(FORMAT))
                groups.remove(room_to_leave)
        else:
            print("Invalid command.")
    thread.join()

    # Having exited the loop upon the disconnect message, we now close the
    # connection.
    client.close()