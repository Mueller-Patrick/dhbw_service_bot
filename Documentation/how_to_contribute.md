The following steps are required of you to contribute by adding a command to our bot:

1. Add the command to the known commands list in `Command.py`
2. Add the command to the commands list in `Command.performCommand`
3. Add the function that is called when the command is performed.
4. If needed, add any message types to the `Command.interpretMessage` list and add the required functions.
Make sure the message type specifier you add is not already in use.
5. In your pull request, provide a complete list of commands you added in the following format:
[command] - [description].
Please keep in mind that commands have to be all-lowercase.
<br><br>
Any modifications that go beyond adding commands can be discussed with us. You then get provided
the required information on how to do it if you need them.
