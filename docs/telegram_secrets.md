We used the file `telegram_secrets.py` to hold the telegram api token and our telegram ids
so these stay out of the source code and obviously out of git.

If you want to host this as your own bot, you have to give these credentials to the bot yourself
for it to work, so here is the file structure of `telegram_secrets.py`:


`token = [TELEGRAM TOKEN]`<br>
`patrick_telegram_id = [PATRICK TELEGRAM ID]`<br>
`david_telegram_id = [DAVID TELEGRAM ID]`

The telegram id of a user is the chat_id fetched by the bot.