Every instance of type `Message` holds the important information about this message to handle it.
Currently these are the chat-ID of the user that send the message and the text of the message.
Also, `checkCommand` is used to find out whether this message is a command or not by checking
for a `/` in the message.