"""
 This class is used by the bot to run the commands.
"""
import Message as msg
import User as usr
import Bot as bt
import patrickID


class Command:
	def __init__(self, message, bot):
		self.message = message
		self.bot = bot

		# Defined commands
		self.commands = ['/start', '/help', '/stopbot', '/privacy', '/whatdoyouknowaboutme', '/subscribemenu',
						 '/unsubscribemenu']

	# Used to find the requested command
	def findCommand(self):
		text = self.message.text.lower()
		if text in self.commands:
			self.performCommand(text)
		else:
			self.sendMessage(self.message.user.chatID, "Unknown command. Say what?")

	def performCommand(self, command):
		callCommandFunctions = {
			'/help': self.command_help,
			'/start': self.command_start,
			'/stopbot': self.command_stopbot,
			'/privacy': self.command_privacy,
			'/subscribemenu': self.command_subscribemenu,
			'/unsubscribemenu': self.command_unsubscribemenu,
			'/whatdoyouknowaboutme': self.command_whatdoyouknowaboutme
		}

		commandFunc = callCommandFunctions.get(command)
		commandFunc()

	def interpretMessage(self):
		type = self.message.user.getExpectedMessageType()

		callMessageFunctions = {
			'': self.message_unknown,
			'name': self.message_name
		}

		messageFunc = callMessageFunctions.get(type)
		messageFunc()

		self.message.user.setExpectedMessageType('')

	# Commands
	def command_help(self):
		# Provide help list for patrick with full command list and for other users with commands they can use.
		if str(self.message.user.chatID) == str(patrickID.chatID):
			self.bot.sendMessage(self.message.user.chatID,
								 "/start\n/help\n/stopbot\n\n/subscribemenu\n/unsubscribemenu\n\n/privacy\n/whatdoyouknowaboutme")
		else:
			self.bot.sendMessage(self.message.user.chatID,
								 "Basic commands:\n/start\n/help\n\nMenu commands:\n/subscribemenu\n/unsubscribemenu\n\nFor privacy information, type\n/privacy\n"
								 "To get all information we have about you, type\n/whatdoyouknowaboutme")

	def command_start(self):
		self.bot.sendMessage(self.message.user.chatID, "Please send me your name so we get to know each other")
		self.message.user.setExpectedMessageType('name')

	def command_stopbot(self):
		if str(self.message.user.chatID) == str(patrickID.chatID):
			self.bot.log("Stopping the bot now.")
			self.bot.tellMainToClose = True
		else:
			self.bot.log("Wrong user " + str(self.message.user.chatID) + ", entered name " + str(
				self.message.user.name) + " tried to stop the bot.")

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
			self.bot.sendMessage(self.message.user.chatID, "You want to receive the daily canteen newsletter")
		else:
			self.bot.sendMessage(self.message.user.chatID, "You don't want to receive the daily canteen newsletter")

		# Message types
	def message_unknown(self):
		self.bot.sendMessage(self.message.user.chatID, 'I don\'t know what to do with your input :(')

	def message_name(self):
		self.message.user.setName(self.message.text)
		welcomeMsg = 'Hello, ' + self.message.text + '! Pleased to meet you!'
		self.bot.sendMessage(self.message.user.chatID, welcomeMsg)
