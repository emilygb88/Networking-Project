import socket
import threading
import collections as col
from datetime import datetime

# SERVER VARIABLES
HEADER = 64
PORT = 5053
SERVER = 'localhost'  # server uses localhost address to run serer
ADDR = (SERVER, PORT)  # server connection
FORMAT = 'utf-8'
MSG_LEN = 2048
DISCONNECT_MESSAGE = '!exit'  # exit all groups and server
DISCONNECT_ACK_MESSAGE = '!exit_ack'  # exit acknowledgement
POST_MESSAGE = '!post'  # post message to group
RETRIEVE_MESSAGE = '!retrieve'  # retrieve message from group
invalidUser = "!INVALID!"  # invalid ack for User validation
validUser = "!VALID!"  # valid ack for User validation
invalidRoom = "!INVALIDROOM!"  # invalid ack for User validation
validRoom = "!VALIDROOM!"  # valid ack for User validation
LIST_GROUPS = '!groups'  # list all groups
LIST_GROUPMEMBERS = '!groupmembers'  # list current group members
JOIN_GROUP_COMMAND = '!groupjoin'  # allow user to join new group
LEAVE_GROUP_MESSAGE = '!leavegroup'  # allow user to leave group
msgInt = 0  # global variable that holds post ID

# SET UP CONNECTION
# set up and bind socket to localhost and specified port
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

# ARRAYS
# rooms is a variable which will hold sub-arrays for each message board. The
# subarray for each message board will hold the connection for each member
# which joins that message board.
# msgBoardArray holds all post information of each respective group, including the message itself
# msgPostArray holds all formatted post information, as posted to the groups, does not contain message
# userArray holds users if the groups in their respective arrays, users may be in multiple groups at once
# allUsers holds the usernames of all the users. Used for duplicate user handling
rooms = [[], [], [], [], []]
msgBoardArray = [[], [], [], [], []]
msgPostArray = [[], [], [], [], []]
userArray = [[], [], [], [], []]
allUsers = []

# messageBoard is a named tuple that holds all message information
# the tuple holds the message ID, name of the sender, post date, message text, and message subject
messageBoard = col.namedtuple('messageBoard', ['msgID', 'senderName', 'postDate', 'post_txt', 'post_subj'])


# NAME: send_message_to_chat
# ARGS: usr_room_id - the ID of the room the user is talking in
#       conn - the connection the user sending the message is using
#       msg - the message to be sent
# FUNCTIONALITY: This function sends a message to all other members in the chat
# room.
def send_message_to_chat(usr_room_id, conn, msg):
    # iterate through the users in the message board corresponding to the
    # user_room_id
    for i in range(len(rooms[usr_room_id])):
        # we check to make sure that we don't send the message to the client
        # who originally sent it.
        if rooms[usr_room_id][i] != conn:
            rooms[usr_room_id][i].send(f"---{msg}".encode(FORMAT))


# NAME: send_message_to_client
# ARGS: usr_room_id - the ID of the room the user is talking in
#       conn - the connection the user sending the message is using
#       msg - the message to be sent
# FUNCTIONALITY: This function sends a message to all specified through
# # the connection
def send_message_to_client(usr_room_id, conn, msg):
    # iterate through the users in the message board corresponding to the
    # user_room_id
    usr_room_id = int(usr_room_id)
    for i in range(len(rooms[usr_room_id])):
        # we check to make sure that we don't send the message to the client
        # who originally sent it.
        if rooms[usr_room_id][i] == conn:
            rooms[usr_room_id][i].send(f"{msg}".encode(FORMAT))


# NAME: broadcast_server_announcement
# ARGS: usr_room_id - the id of room to broadcast the server announcement to
#       msg - the test of the announcement to send the message to
# FUNCTIONALITY: This function sends an announcement from the server to all
# members of an individual message board.
def broadcast_server_announcement(usr_room_id, msg):
    # Iterate through each user in the message board and send the message to
    # each of them.
    for i in range(len(rooms[usr_room_id])):
        rooms[usr_room_id][i].send(msg.encode(FORMAT))


# NAME: disconnect
# ARGS: conn - the connection of the user disconnecting
#       server_name - the name of the user disconnecting
# FUNCTIONALITY: This function sends the special message takes care of all
# the necessary cleanup of removing a user from a group.
def disconnect(conn, server_name):
    # send the special disconnect_ack message to client so that the listening
    # thread can clean up on its end.
    conn.send(DISCONNECT_ACK_MESSAGE.encode(FORMAT))

    # iterate through the rooms, removing the user from any rooms they are in.
    for room_id in range(len(rooms)):
        if conn in rooms[room_id]:
            leave_room(conn, room_id, server_name)

    # remove the user from the all user array
    allUsers.remove(server_name)


# NAME: leave_room
# ARGS: conn - the connection value of the client
#       room_id - the id of the room the user is leaving
# FUNCTIONALITY: This function removes a user from a room.
def leave_room(conn, room_id, server_name):
    # notify all group members that the user has left
    leave_msg = "[" + server_name + "] has left group " + str(room_id) + "."
    broadcast_server_announcement(room_id, leave_msg)

    # Remove the user connection from the rooms array
    rooms[room_id].remove(conn)
    # Remove the username from the users array for the group
    userArray[room_id].remove(server_name)


# NAME: connect_to_the_room
# ARGS: room_id - the index value for which room to store the connection in
#       conn - the connection to store
# FUNCTIONALITY: This function adds the connection value of a new user to the
# subarray corresponding to it in rooms.
# when the user joins the room, if applicable, the last two posts made to
# the specified group are displayed
# The server sends an announcement to all users in the group that
# a new person joined
def connect_to_the_room(room_id, conn, server_name):
    rooms[room_id].append(conn)
    for user in rooms[room_id]:
        if user and user == conn:
            if len(msgPostArray[room_id]) == 1:
                user.send("--------------------------------------\n".encode(FORMAT))
                user.send("Last Post on Message Board Before You Joined:\n".encode(FORMAT))
                for x in range(len(msgPostArray[room_id]) - 1, len(msgPostArray[room_id])):
                    # print(msgArray[x])
                    msgTemp = (msgPostArray[room_id][x] + '\n')
                    user.send(msgTemp.encode(FORMAT))
                user.send("--------------------------------------\n".encode(FORMAT))
            elif len(msgPostArray[room_id]) >= 2:
                user.send("--------------------------------------\n".encode(FORMAT))
                user.send("Last 2 Posts on Message Board Before You Joined:\n".encode(FORMAT))
                for x in range(len(msgPostArray[room_id]) - 2, len(msgPostArray[room_id])):
                    # print(msgArray[x])
                    msgTemp = (msgPostArray[room_id][x] + '\n')
                    user.send(msgTemp.encode(FORMAT))
                user.send("--------------------------------------\n".encode(FORMAT))
    msg = "[" + server_name + "] has joined group " + str(room_id) + "!"
    broadcast_server_announcement(room_id, msg)
    msg = "\nList of users in the room: \n"
    send_message_to_client(room_id, conn, msg)
    listOfUsers = ','.join(userArray[room_id])
    broadcast_server_announcement(room_id, listOfUsers)


# NAME: handle_client
# ARGUMENTS: conn - the connection value of the client
#            addr - the address value of the client
# FUNCTIONALITY: this function manages an individual connection from a user
# to the message board. It's the function used to spin off threads.
def handle_client(conn, addr):
    # print out the new connection added
    print(f'[NEW CONNECTION] {addr} connected.')
    connected = True

    # INITIAL SERVER SETUP
    # Initial user validity error checking
    # Initial group validity error checking
    # Adds user to corresponding user and group arrays
    server_name = conn.recv(1024)
    server_name = server_name.decode()
    while server_name in allUsers:
        conn.send(invalidUser.encode())
        server_name = conn.recv(2048).decode(FORMAT)
    conn.send(validUser.encode())
    xs = []
    for room_id in range(len(rooms)):
        xs.append(f'Group: {room_id}')
    mySeparator = ", "
    strRooms = mySeparator.join(xs)
    conn.send(strRooms.encode())
    userRoomInitial = conn.recv(2048).decode(FORMAT)
    userRoomInitial = int(userRoomInitial)
    while (int(userRoomInitial) > len(rooms) - 1) or (int(userRoomInitial) < 0):
        conn.send(invalidRoom.encode())
        userRoomInitial = conn.recv(2048).decode(FORMAT)
    conn.send(validRoom.encode())
    userArray[int(userRoomInitial)].append(server_name)
    allUsers.append(server_name)
    connect_to_the_room(int(userRoomInitial), conn, server_name)

    # MAIN WHILE LOOP
    # continuously receives and sends message to client
    # contains all functionality for commands sent from the client
    while connected:
        msg = conn.recv(MSG_LEN).decode(FORMAT)
        # POST MESSAGE
        # receives message text, message subject, group number, and name of the user
        # calculates time and gets msg ID
        # creates a message post with above information and stores it in array
        # post is broadcast to all users in that room
        if msg == POST_MESSAGE:
            global msgInt
            post_txt = conn.recv(MSG_LEN).decode(FORMAT)
            post_subj = conn.recv(MSG_LEN).decode(FORMAT)
            post_board = int(conn.recv(MSG_LEN).decode(FORMAT))
            senderName = conn.recv(MSG_LEN).decode(FORMAT)
            now = datetime.now()
            postDate = now.strftime("%m/%d/%Y %H:%M:%S")
            message = messageBoard(msgInt, senderName, postDate, post_txt, post_subj)
            msgPost = f"[{message.msgID} , {message.senderName} , {message.postDate} , {message.post_subj}]"
            msgPostArray[post_board].append(msgPost)
            msgBoardArray[post_board].append(message)
            broadcast_server_announcement(post_board, msgPost)
            msgInt = msgInt + 1
        # RETRIEVE MESSAGE
        # receives desired message ID, and list of groups the user is in
        # has user and post validity checking
        # user must be in the same group as the desired message to retrieve the message
        # ID must be a valid integer and index
        # sends message to client if user is in the same room as message
        elif msg == RETRIEVE_MESSAGE:
            userMsgID = conn.recv(MSG_LEN).decode(FORMAT)
            userGroupStr = conn.recv(MSG_LEN).decode(FORMAT)
            userGroupsList = list(userGroupStr.split(" "))
            userGroupsList = [eval(i) for i in userGroupsList]
            if all([not sublist for sublist in msgBoardArray]):
                send_message_to_client(userGroupsList[0], conn, "There are no posts on the message board. Use !post to "
                                                              "make a post")
            # If the user entered a valid ID, the server iterates through each room that
            # the user is in to check if their specified message is also in that room
            # handles value index exceptions
            elif 0 <= int(userMsgID) <= (int(msgInt) - 1):
                break_flag = True
                arrGroup = []
                while break_flag:
                    for userGroupCounter in userGroupsList:
                        tempArr = msgBoardArray[userGroupCounter]
                        arrGroup.append(userGroupCounter)
                        try:
                            checkTuple = [tup[0] for tup in tempArr].index(int(userMsgID))
                            msg = f"{msgBoardArray[userGroupCounter][checkTuple][3]}"
                            send_message_to_client(arrGroup[0], conn, f"Retrieved Message: {msg}")
                            break_flag = False
                            break
                        except ValueError:
                            if arrGroup == userGroupsList:
                                send_message_to_client(arrGroup[0], conn,
                                                       "You are not in that room, cannot retrieve message")
                                break_flag = False
            else:
                send_message_to_client(userGroupsList[0], conn, "Index out of range, enter a valid Message ID")
        # LIST GROUP MEMBERS
        # retrieves the group that the user wants to check
        # sends list back to client
        elif msg == LIST_GROUPMEMBERS:
            groupChosenView = conn.recv(MSG_LEN).decode(FORMAT)
            groupMembers = []
            for i in range(len(userArray[int(groupChosenView)])):
                groupMembers.append(f'{userArray[int(groupChosenView)][i]}')
            mySeparator = ", "
            strGroupMembers = mySeparator.join(groupMembers)
            send_message_to_client(groupChosenView, conn, strGroupMembers)
        # LIST GROUPS
        # gets int of number of groups in the rooms array
        # returns string of formatted available groups to user
        elif msg == LIST_GROUPS:
            userGroupStr = conn.recv(MSG_LEN).decode(FORMAT)
            userGroupsList = list(userGroupStr.split(" "))
            userGroupsList = [eval(i) for i in userGroupsList]
            roomsArrTemp = []
            for room_id in range(len(rooms)):
                roomsArrTemp.append(f'Group: {room_id}')
            mySeparator = ", "
            strGroups = mySeparator.join(roomsArrTemp)
            send_message_to_client(userGroupsList[0], conn, strGroups)
        # JOIN GROUP
        # gets room that user wants to join
        # connects user to that room by adding them to the appropriate arrays
        # value validation is in client
        elif msg == JOIN_GROUP_COMMAND:
            user_room_chosen = conn.recv(MSG_LEN).decode(FORMAT)
            int_user_room_chosen = int(user_room_chosen)
            userArray[int_user_room_chosen].append(server_name)
            connect_to_the_room(int_user_room_chosen, conn, server_name)
        # LEAVE GROUP MESSAGE
        # receives user group to leave and removes the user from the
        # necessary arrays
        elif msg == LEAVE_GROUP_MESSAGE:
            # receive the group to leave
            leave_room_id = int(conn.recv(MSG_LEN).decode(FORMAT))
            # leave the room
            leave_room(conn, leave_room_id, server_name)

        # DISCONNECT MESSAGE
        # if the message received is the disconnect message notify the other
        # users in the group that the user has left
        elif msg == DISCONNECT_MESSAGE:
            disconnect(conn, server_name)
            break
    conn.close()
    print(f'[END CONNECTION] {addr} disconnected.')
    print(f'[ACTIVE CONNECTIONS] {threading.active_count() - 2}')




# NAME: start
# ARGUMENTS: None
# FUNCTIONALITY: This function initializes the message board and starts spinning
# off threads for each client that joins.
def start():
    # Begin listening on local host
    server.listen()
    print(f"Server is listening on {SERVER}")

    while True:
        # wait for a client to try and connect to the message board
        conn, addr = server.accept()
        # spin off a thread that uses the handle_client function
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        # print the number of users connected to the message board
        print(f'[ACTIVE CONNECTIONS] {threading.active_count() - 1}')


print('Server is starting...')
start()