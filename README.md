**DHBW Service Bot - WIP**

This is a telegram bot for students at DHBW Karlsruhe. It is made by students of the DHBW Karlsruhe 
and not affiliated with the DHBW.
In the future, it will be capable of things like automatically sending you the daily menu in the 
canteen in the morning or informing you when your first lecture will begin the next day.

To use it, go to `t.me/dhbw_service_bot` and follow the given instructions.

This bot is programmed and run by

`https://github.com/Mueller-Patrick`

and

`https://github.com/qt1337`.

To contribute, follow the steps in `CONTRIBUTING.md`

<br><br>
Used libraries are <br>
`requests`<br>
`requests_html`<br>
`datetime`<br>
`json`<br>
`asyncio`<br>
`icalendar`<br>
`icalevents`<br>
`logging`.<br>

These are not specifically important for development, just for us to run the bot.
To install them, run `pip install [LIBRARY_NAME]`on your machine, given that you have already installed pip.

We also used the `os` library, but this should come with vanilla python.


For a list of supported commands, see 
`docs/telegram_command_description.md`

**KNOWN ISSUES**<br>
Due to the port to AWS Lambda and the simultaneous switch to the official python telegram library, some commands
are currently not working, including, but not limited to:<br>
<ul>
    <li>/help</li>
    <li>/settings</li>
    <li>/getmenu</li>
</ul>
This is because for these commands, we generate a reply markup, which is done differently with the new library, so we
need to switch that to the new behavior first. This is going to be done ASAP by Patrick.
