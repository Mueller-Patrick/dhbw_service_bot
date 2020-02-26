`__init__`: Constructor of the Command. Takes the send message to handle it and the bot so
it can send messages to the user via the bot instance.
<br><br>
`findCommand`: Looks if the entered command is known and if so, runs `performCommand`.
<br><br>
`performCommand`: Looks which of the known commands was called and then calls the command-
specific function.
<br><br>
`interpretMessage`: Tries to find out what exactly the users message is via context.
This works by finding out what the user was expected to send now (which is specified by
the command.) E.g. if the user sends `/start`, the bot asks for the name of the user and 
saves in the user instance that the next message from the user is expected to be his name. 
If he then sends a normal message (so no command), the `interpretMessage` function knows that
the user was asked to enter his name and therefore treats the received message as his name.
<br><br>
The other funtions of this class are the command/message handlers.