`__init__`: Fetches the Telegram token and the users list and starts the asynchronous working loop.
<br><br>
`async` `mainLoop`: The asynchronous loop that handles new messages from users.
<br><br>
`async` `pushLoop`: The asynchronous loop that sends push notifications to all users that want them
at a specified time.
<br><br>
`async` `saveLoop`: The asynchronous loop that saves all current users with theit preferences every
full our to minimize data loss.
<br><br>
`sendMenu`: The method that fetches the menu and sends it to users that want it.
<br><br>
`getToken`: Reads the Telegram token from specified file.
<br><br>
`getUsers`: Reads the users from the specified file, creates a new instance of type `User`for
every user and puts them in a list to be given to the bot at startup.
<br><br>
`close`: Takes every instance of type `User` known to the bot, transforms its parameters to a
dict and then converts them to a json file to be saved.