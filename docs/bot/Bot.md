`__init__`: Constructor of the bot, sets all required parameters for the bot to work.
<br><br>
`getOffset`, `setOffset`: Gets and Sets the telegram update offset from / to the offset file.
<br><br>
`sendMessage`: Takes a chat-id and the message to be send and sends this to the specified user.
<br><br>
`getUpdates`: Fetches updates from the Telegram servers every second and creates new message
instances for every received message as specified in the data model.
<br><br>
`handleMessages`: Decides whether the message is a command and then calls the function to execute
this command. If it is no command, it tries to interpret the message based on what the conversation
history with this user is.
<br><br>
`log`: Prints the given message to the console and sends a Telegram message to Patrick (and David).
Used for important messages like crash logs etc.
<br><br>
`close`: At call, it sets the bot's close parameter to true and therefore tells the bot not to 
fetch any new updates and just handle the messages that are already fetched and have to be handled now.