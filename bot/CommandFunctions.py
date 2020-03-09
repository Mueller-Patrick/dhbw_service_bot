import telegram_secrets
from menu import MenuSaver as menu
from datetime import datetime


class CommandFunctions:
	def __init__(self, message, bot):
		self.message = message
		self.bot = bot

	def command_help(self):
		# Provide help list for patrick with full command list and for other users with commands they can use.
		if str(self.message.user.chatID) == str(telegram_secrets.patrick_telegram_id):
			self.bot.sendMessageWithOptions(self.message.user.chatID,
											"/help\n/stopbot\n/sendmessagetoeveryone\n\n/getmenu\n\n/getlectures\n\n/getmeme\n\n/reportbug\n\n/privacy\n/whatdoyouknowaboutme",
											self.bot.generateReplyMarkup(
												[['/stopbot'], ['/sendmessagetoeveryone'], ['/help'], ['/settings'],
												 ['/getmenu'], ['/getlectures'], ['/getmeme'],
												 ['/reportbug'], ['/privacy'], ['/whatdoyouknowaboutme']]))
		else:
			replyString = ('*Help*: /help\n\n'
				+ '*Settings*: /settings\n\n'
				+ '*Menu*: /getmenu\n\n'
				+ '*Lecture plan*: /getlectures\n\n'
				+ 'Get your favorite *memes*: /getmeme\n\n'
				+ 'To *report a bug*: /reportbug\n\n'
				+ '*Privacy information*: /privacy\n'
				+ 'To get *all information* we have about you: /whatdoyouknowaboutme\n\n'
				+ 'If you have any questions, contact @PaddyOfficial on Telegram.')
			self.bot.sendMessageWithOptions(self.message.user.chatID, replyString,
											self.bot.generateReplyMarkup(
												[['/help'], ['/settings'], ['/getmenu'], ['/getlectures'], ['/getmeme'],
												 ['/reportbug'], ['/privacy'], ['/whatdoyouknowaboutme']]))

	def command_start(self):
		self.bot.sendMessage(self.message.user.chatID, "Please send me your name so we get to know each other")
		self.message.user.expectedMessageType = 'startname'

	def command_stopbot(self):
		if str(self.message.user.chatID) == str(telegram_secrets.patrick_telegram_id):
			self.bot.log("Stopping the bot now.")
			self.bot.tellMainToClose = True
		else:
			self.bot.log(("Wrong user " + str(self.message.user.chatID) + ", entered name " + str(
				self.message.user.name) + " tried to stop the bot."))
			self.bot.sendMessage(self.message.user.chatID, "You are not allowed to do this.")

	def command_privacy(self):
		self.bot.sendMessage(self.message.user.chatID,
							 "We save everything you provide us for you to get the best experience.")

	def command_whatdoyouknowaboutme(self):
		self.bot.sendMessage(self.message.user.chatID, "🤔 I know the following things about you :")
		self.bot.sendMessage(self.message.user.chatID,
							 ("📥 Your Telegram chat id is " + str(self.message.user.chatID)))
		self.bot.sendMessage(self.message.user.chatID, ("🗣 Your name is " + str(self.message.user.name)))
		if self.message.user.address != '' and self.message.user.address is not None:
			self.bot.sendMessage(self.message.user.chatID,
								 ('🚅 The address you entered is ' + self.message.user.address))
		if self.message.user.wantsMenu:
			self.bot.sendMessage(self.message.user.chatID, "✅ You want to receive the daily menu push")
		else:
			self.bot.sendMessage(self.message.user.chatID, "❌ You don't want to receive the daily menu push")

		if self.message.user.wantsLecturePlan:
			self.bot.sendMessage(self.message.user.chatID, "✅ You want to receive the daily lecture plan push")
		else:
			self.bot.sendMessage(self.message.user.chatID,
								 "❌ You don't want to receive the daily lecture plan push")

		if self.message.user.wantsTransportInfo:
			self.bot.sendMessage(self.message.user.chatID, "✅ You want to receive public transport info")
		else:
			self.bot.sendMessage(self.message.user.chatID, "❌ You don't want to receive public transport info")

		if self.message.user.course:
			self.bot.sendMessage(self.message.user.chatID,
								 ("🏫 You are in the " + self.message.user.course + " course"))
		else:
			self.bot.sendMessage(self.message.user.chatID,
								 "❓ But I don't know which course you are in, so I can't send you"
								 + "your lecture plan :(")

	def command_getmenu(self):
		self.bot.sendMessageWithOptions(self.message.user.chatID, 'For which day do you want the plan?',
										self.bot.generateReplyMarkup([['Today', 'Tomorrow']]))

		self.message.user.expectedMessageType = 'menuday'

	def command_getlectures(self):
		if self.message.user.course == None or self.message.user.course == '':
			self.bot.sendMessage(self.message.user.chatID,
								 'I don\'t know which course you are in. Please provide me this information under /settings -> Personal Information')
		else:
			self.bot.sendMessageWithOptions(self.message.user.chatID, 'For which day do you want the plan?',
											self.bot.generateReplyMarkup([['Today', 'Tomorrow']]))

			self.message.user.expectedMessageType = 'lectureplanday'

	def command_sendmessagetoeveryone(self):
		if str(self.message.user.chatID) == str(telegram_secrets.patrick_telegram_id):
			self.bot.sendMessage(self.message.user.chatID, "What do you want to broadcast?")
			self.message.user.expectedMessageType = "broadcastmessage"
		else:
			self.bot.log(("Wrong user " + str(self.message.user.chatID) + ", entered name " + str(
				self.message.user.name) + " tried to broadcast a message"))
			self.bot.sendMessage(self.message.user.chatID, "You are not allowed to do this.")

	def command_getmeme(self):
		if self.message.user.course != '':
			# Convert the memeTypes to a list of lists so they appear as a vertical keyboard instead of horizontal
			memeTypes = self.bot.memes.getMemeTypes(self.message.user.course)
			memeTypesConverted = []
			for meme in memeTypes:
				memeTypesConverted.append([meme])
			memeTypesConverted.append(['Random'])

			self.bot.sendMessageWithOptions(self.message.user.chatID, "Please select the type of meme:",
											self.bot.generateReplyMarkup(memeTypesConverted))
			self.message.user.expectedMessageType = 'memetype'
		else:
			self.bot.sendMessage(self.message.user.chatID, "I can't send you memes because you are in no course. "
								 + "Enter your course under /settings -> Personal Information")

	def command_reportbug(self):
		self.bot.sendMessage(self.message.user.chatID, "Please describe the bug:")
		self.message.user.expectedMessageType = 'bugdescription'

	def command_settings(self):
		self.bot.sendMessageWithOptions(self.message.user.chatID, 'What do you want to change?',
										self.bot.generateReplyMarkup(
											[['️🧍 Personal Information'], ['📲 Subscription-Settings'],
											 ['🧨 Cancel']]))
		self.message.user.expectedMessageType = 'settingstype'
