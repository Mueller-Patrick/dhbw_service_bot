**DHBW Service Bot - WIP**

This is a telegram bot for students at DHBW Karlsruhe.
In the future, it will be capable of things like automatically sending you the daily menu in the 
canteen in the morning or informing you when your first lecture will begin the next day.

To use it, go to `t.me/dhbw_service_bot` and follow the given instructions.

This bot is programmed and run by <br>
`https://github.com/Mueller-Patrick` <br>
and <br>
`https://github.com/qt1337`.
<br><br>
If you have any ideas on how to extend the functionality, feel free to create
a PR. Please make sure to document it appropriate and tell us wich commands you added
so we can add the to the bot properly.

Used libraries are
`requests`<br>
`requests_html`<br>
`json`<br>
`asyncio`.<br>
These are not specifically important for development, just for us to run the bot.
To install them, run `pip install [LIBRARY_NAME]`on your machine, given that you have already installed pip.
<br><br>
Supported commands of the bot are:<br>
`/start`- Starts the bot <br>
`/help` - Prints the most important commands <br>
`/subscribeMenu` - Subscribes you to the daily canteen menu newsletter <br>
`/unsubscribeMenu` - You might have an idea what this does.
