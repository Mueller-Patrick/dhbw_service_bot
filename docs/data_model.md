In this file, I'll give you an overview on how the data model looks like.
We start the bot simply by running `Main.py`. This will create a new instance of the
`Bot`. Then the Main.py constructor creates an asynchronous loop that alternatingly
uses the functions `getUpdates` and `handleMessages` of the bot instance to fetch
updates and process them. The `getUpdates` function creates a new instance of the type
`Message` for every received message. These instances are then saved into a list to
be handled afterwards. The `getUpdates` method also checks if the sending user is
already known. If so, it hands the instance of the type `User` to the message. If 
not, it creates a new instance of type `User`, hands it to the message and saves
it to a list. This list is used when stopping the bot to persist the user data.
The `handleMessages` function goes through each message in the list and checks if 
it is a command. It creates a new instance of `Command` and calls the `findCommand`
function if the message is a command. If not, it calls the `interpretMessage` function.
It then removes the now handled message from the list and continues with the next one.
<br><br>
The menu newsletter is currently handled inside `Main.py`'s function `pushLoop`. It checks
for a specified time and if it is that time, uses `Request.py` to fetch the daily menu 
from the website of the DHBW and afterwards sends this to every user that wants to have it.
