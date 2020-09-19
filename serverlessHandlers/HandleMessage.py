"""
 Bot class, an object of type bot is created in main.init() at startup with the required parameters.
"""

import telegram
import logging

logger = logging.getLogger()

class HandleMessage:
	def __init__(self, bot, chat_id, text, message_id):
		ret_text = ("Hello fellow Nerd! I'm currently being ported to a new system and am therefore unavailable."
					+ " If you want to help or just check the progress, you can do that here:"
					+ " https://github.com/Mueller-Patrick/dhbw_service_bot. I'm going to be up and running again as soon"
					+ " as possible, so stay tuned!")

		bot.sendMessage(chat_id=chat_id, text=ret_text)
		logger.info('Message sent')
