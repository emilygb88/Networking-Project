# Networking-Project-2
Emily Bever\
Mary Meineke\
Molly Vongsakhamphouy
## Compile Instructions
**How to run the code:**
1. The first thing that you should do is run the server.py as a normal file.
	- Ensure that you have an available port and server address: We use 'localhost' and port 5053 but feel free to change it in the server.py file.\
*NOTE: After running the server it should say :*
"Server is starting...
Server is listening on localhost"

2. Next run the client.py as a normal file. The first command you will need to run is the '!connect' command to connect to the server. It will prompt you for the server address and the port number. *NOTE: Unless you have changed the default values of the code, enter 'localhost' and 5053 here.*

3. Enter a username for your user\
*NOTE: If the username you entered is invalid (already exists) then you will be prompted to enter a different username.*

4. Now you will be prompted to select a group to join.  
	- You will be given 5 group numbers.  
	- Enter the number of the group you want to join.

5. Now you should be in your group that you selected.  You can use the list of commands below to navigate to perform different functionalities such as:
	- connect to the server
	- leaving the group
	- joining multiple groups
	- posting messages to groups
	- retrieving other messages from other users in your group(s)
	- listing the users in your group(s)
	- etc... \
*To use these commands simply type the command you want and if prompted type in any further information that is needed. The available commands are listed below.*


## User Instructions
Once you've connected to the server, you can enter the following commands to navigate the message board:
- !connect — This command will allow you to connect to the server. It is the first command you must use when you start the client. It will prompt you to enter the server address and port.  The address you should enter is either "localhost" or "127.0.0.1".  Then the port you should enter when prompted is "5053"
- !post — This command will allow you to post a message to the group. It will prompt you for the message text and subject and group to post to
- !retrieve — This command will allow you to view a message that has been posted to the message board. It will prompt you for the message ID
- !groups — This command will display a list of available groups
- !mygroups — This command will display a list of groups the user is in
- !groupjoin — This command will allow the user to join a group. It will prompt you for the ID of the group you would like to join.
- !leavegroup — This command will allow the user to leave a group. It will prompt you for the ID of the group you would like to leave
- !groupmembers — This command will list all the members of a group the user is is. It will prompt you for the ID of the group whose members you would like to know.
- !exit — This command will allow the user to leave the message board. It will leave all groups the user is a member and close the connection with the server.

## Issues we faced
### Source Control
One of the main issues we faced in creating this project was coordinating our work on the code. With three people working on the same project it was tricky to divide the work into portions we could work on simultaneously without running into issues where we wrote overtop of eachother and in the same sections. We used Github to keep track up the code we were working on which did help us to keep track of just what changes each other had made. Ultimately though, we could've come up with a more effective way of coordinating the work that would've been more effective.

### Handling Users in Multiple Groups 
Another big issue that we faced with this project was determining how to implement part 2.  When we first started working on part two we did not think it would be that difficult as we already had all or almost all of the functionality, but it was only for users with one group. However, we realized that it was not as easy as we thought it would be because of the complexities with handling how we would store all of the information we needed for each different group and also ensure that in order to see messages and user information, you must be in that group. To control all of these factors, we decided to use nested arrays for each group and each array in the big array would hold information about a specific group. So there were five group arrays, five message arrays, five users arrays.  Then when we needed to ensure that a user was able to do something based on its group, we would iterate through the arrays where everything was stored.  While there may have been other datastructures that we could have used, we throught the consistency and versatility of using nested arrays would be a good option, and ultimately it worked.
