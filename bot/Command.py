"""
 This class is used by the bot to run the commands.
"""
import telegram_secrets
from menu import MenuSaver as menu
from datetime import datetime


class Command:
	def __init__(self, message, bot):
		self.message = message
		self.bot = bot

		# Defined commands
		self.commands = ['/start', '/help', '/stopbot', '/privacy', '/whatdoyouknowaboutme', '/subscribemenu',
						 '/unsubscribemenu', '/getmenu', '/subscribelectureplan', '/unsubscribelectureplan',
						 '/sendmessagetoeveryone']

	# Used to find the requested command
	def findCommand(self):
		text = self.message.text.lower()
		if text in self.commands:
			self.performCommand(text)
		else:
			self.bot.sendMessage(self.message.user.chatID, "Unknown command. Say what?")

	def performCommand(self, command):
		callCommandFunctions = {
			'/help': self.command_help,
			'/start': self.command_start,
			'/stopbot': self.command_stopbot,
			'/privacy': self.command_privacy,
			'/subscribemenu': self.command_subscribemenu,
			'/unsubscribemenu': self.command_unsubscribemenu,
			'/whatdoyouknowaboutme': self.command_whatdoyouknowaboutme,
			'/getmenu': self.command_getmenu,
			'/subscribelectureplan': self.command_subscribelectureplan,
			'/unsubscribelectureplan': self.command_unsubscribelectureplan,
			'/sendmessagetoeveryone': self.command_sendmessagetoeveryone
		}

		commandFunc = callCommandFunctions.get(command)
		commandFunc()

	def interpretMessage(self):
		type = self.message.user.expectedMessageType

		callMessageFunctions = {
			'': self.message_unknown,
			'name': self.message_name,
			'coursename': self.message_coursename,
			'raplalink': self.message_raplalink,
			'broadcastmessage': self.message_broadcastmessage
		}

		messageFunc = callMessageFunctions.get(type)
		messageFunc()

	# Commands
	def command_help(self):
		# Provide help list for patrick with full command list and for other users with commands they can use.
		if str(self.message.user.chatID) == str(telegram_secrets.patrick_telegram_id):
			self.bot.sendMessage(self.message.user.chatID,
								 "/start\n/help\n/stopbot\n/sendmessagetoeveryone\n\n/subscribemenu\n/unsubscribemenu\n/getmenu\n\n/subscribelectureplan\n/unsubscribelectureplan\n\n/privacy\n/whatdoyouknowaboutme")
		else:
			self.bot.sendMessage(self.message.user.chatID,
								 (
										 "Basic commands:\n/start\n/help\n\nMenu commands:\n/subscribemenu\n/unsubscribemenu\n/getmenu\n\n"
										 + "Lecture plan commands:\n/subscribelectureplan\n/unsubscribelectureplan"
										 + "\n\nFor privacy information, type\n/privacy\n"
										 + "To get all information we have about you, type\n/whatdoyouknowaboutme"))

	def command_start(self):
		self.bot.sendMessage(self.message.user.chatID, "Please send me your name so we get to know each other")
		self.message.user.expectedMessageType = 'name'

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

	def command_subscribemenu(self):
		self.message.user.wantsMenu = True
		self.bot.sendMessage(self.message.user.chatID,
							 "You successfully subscribed to the daily menu push-service. Welcome aboard!")

	def command_unsubscribemenu(self):
		self.message.user.wantsMenu = False
		self.bot.sendMessage(self.message.user.chatID,
							 "We are sorry to loose you as a subscriber and hope to see you here again.")

	def command_whatdoyouknowaboutme(self):
		self.bot.sendMessage(self.message.user.chatID, "I know the following things about you:")
		self.bot.sendMessage(self.message.user.chatID, ("Your Telegram chat id is " + str(self.message.user.chatID)))
		self.bot.sendMessage(self.message.user.chatID, ("Your name is " + str(self.message.user.name)))

		if self.message.user.wantsMenu:
			self.bot.sendMessage(self.message.user.chatID, "You want to receive the daily menu push")
		else:
			self.bot.sendMessage(self.message.user.chatID, "You don't want to receive the daily menu push")

		if self.message.user.wantsLecturePlan:
			self.bot.sendMessage(self.message.user.chatID, "You want to receive the daily lecture plan push")
		else:
			self.bot.sendMessage(self.message.user.chatID, "You don't want to receive the daily lecture plan push")

		if self.message.user.course:
			self.bot.sendMessage(self.message.user.chatID, ("You are in the " + self.message.user.course + " course"))
		else:
			self.bot.sendMessage(self.message.user.chatID,
								 "But I don't know which course you are in, so I can't send you"
								 + "your lecture plan :(")

	def command_getmenu(self):
		now = datetime.now()
		weekday = now.weekday()
		if weekday < 5:  # Because monday is 0...
			fetchedMenu = menu.Reader(1).get_menu_as_arr()
			self.bot.sendMessage(self.message.user.chatID, "Here you go: ")
			for oneMenu in fetchedMenu:
				self.bot.sendMessage(self.message.user.chatID, oneMenu)
		else:
			self.bot.sendMessage(self.message.user.chatID, "The canteen is closed today. Hence no menu for you.")

	def command_subscribelectureplan(self):
		if self.message.user.course == '' or self.message.user.course == None:
			self.bot.sendMessage(self.message.user.chatID, "Please send me your course name in this format: TINF19B4")
			self.message.user.expectedMessageType = 'coursename'
		else:
			self.message.user.wantsLecturePlan = True
			self.bot.sendMessage(self.message.user.chatID, "You successfully subscribed to the daily lecture plan push."
								 + " May the RaPla be with you!")

	def command_unsubscribelectureplan(self):
		self.bot.sendMessage(self.message.user.chatID, "What did I do wrong? :(((( I'm so sad now :(((( But since "
							 + "I'm just a computer, of course I did what you wanted and unsubscribed you. :((((")

	def command_sendmessagetoeveryone(self):
		if str(self.message.user.chatID) == str(telegram_secrets.patrick_telegram_id):
			self.bot.sendMessage(self.message.user.chatID, "What do you want to broadcast?")
			self.message.user.expectedMessageType = "broadcastmessage"
		else:
			self.bot.log(("Wrong user " + str(self.message.user.chatID) + ", entered name " + str(
				self.message.user.name) + " tried to broadcast a message"))
			self.bot.sendMessage(self.message.user.chatID, "You are not allowed to do this.")

	# Message types
	def message_unknown(self):
		self.bot.sendMessageWithOptions(self.message.user.chatID,
										'I don\'t know what to do with your input :( Use this to get help:',
										self.bot.generateReplyMarkup(['/help']))

	def message_name(self):
		self.message.user.name = self.message.text
		welcomeMsg = ('Hello, ' + self.message.text + '! Pleased to meet you! To get you started, I\'ll now explain to '
					+ 'you the stuff I\'m able to do and what commands may use. You already figured out the first command, /start. '
					+ 'Great work there! To continue, you might want to subscribe to the daily menu push service via /subscribemenu '
					+ 'and the daily lecture plan push via /subscribelectureplan. Pretty easy to remember, right? If you want to '
					+ 'unsubscribe from these services, you just need to type /unsubscribemenu or /unsubscribelectureplan (You '
					+ 'probably already guessed these). To get the daily menu at any time, send /getmenu. And because I '
					+ 'respect your privacy, type /privacy and /whatdoyouknowaboutme to get Info about what we save '
					+ 'about you. Last but not least, type /help to get a short description of every command.')
		self.bot.sendMessage(self.message.user.chatID, welcomeMsg)
		self.message.user.expectedMessageType = ''

	def message_coursename(self):
		self.message.user.course = self.message.text

		if self.bot.lectureFetcher.checkForCourse(self.message.user.course):
			self.message.user.wantsLecturePlan = True
			self.bot.sendMessage(self.message.user.chatID, "You successfully subscribed to the daily lecture plan push."
								 + " May the RaPla be with you!")
			self.message.user.expectedMessageType = ''
		else:
			self.bot.sendMessage(self.message.user.chatID, "Unknown course. Please send me the link to your courses"
								 + " iCal calendar:")
			self.message.user.expectedMessageType = "raplalink"

	def message_raplalink(self):
		if self.message.text == 'stop':
			self.message.user.expectedMessageType = ''
			self.bot.sendMessage(self.message.user.chatID, 'Mission aborted, repeating: MISSION ABORTED.')
		else:
			if self.bot.lectureFetcher.validateLink(self.message.text):
				self.bot.lectureFetcher.addRaplaLink(self.message.user.course, self.message.text)
				self.message.user.wantsLecturePlan = True
				self.bot.sendMessage(self.message.user.chatID,
									 "You successfully subscribed to the daily lecture plan push."
									 + " May the RaPla be with you!")
				self.message.user.expectedMessageType = ''
			else:
				self.bot.sendMessage(self.message.user.chatID,
									 "Invalid link. Please try again. Write stop to cancel setup.")
				self.message.user.expectedMessageType = 'raplalink'

	def message_broadcastmessage(self):
		for user in self.bot.users:
			self.bot.sendMessage(user.chatID, self.message.text)

		self.message.user.expectedMessageType = ''
