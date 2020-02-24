"""
 This class is used by the bot to run the commands.
"""
import Message as msg
import User as usr
import Bot as bt
import patrickID


class Command():
	def __init__(self, message, bot):
		self.message = message
		self.bot = bot

		# Defined commands
		self.commands = ['/start', '/help', '/stopbot', '/privacy', '/subscribemenu', '/unsubscribemenu']

	# Used to find the requested command
	def find_command(self, message):
		text = message.text.lower()
		if text in self.commands:
			self.performCommand(text, message)
		else:
			self.sendMessage(message.user.chatID, "Unknown command. Say what?")

	def performCommand(self, command, message):
		if command == '/help':
			# Provide help list for patrick with full command list and for other users with commands they can use.
			if str(message.user.chatID) == str(patrickID.chatID):
				self.bot.sendMessage(message.user.chatID, "/start\n/help\n/stopbot\n\n/subscribemenu\n/unsubscribemenu\n\n/privacy")
			else:
				self.bot.sendMessage(message.user.chatID,
									 "Basic commands:\n/start\n/help\n\nMenu commands:\n/subscribemenu\n/unsubscribemenu\n\nFor privacy information, type\n/privacy")
		elif command == '/start':
			self.bot.sendMessage(message.user.chatID, "Please send me your name so we get to know each other")
			message.user.setExpectedMessageType('name')
		elif command == '/stopbot':
			if str(message.user.chatID) == str(patrickID.chatID):
				self.bot.log("Stopping the bot now.")
				self.bot.tellMainToClose = True
			else:
				self.bot.log("Wrong user " + str(message.user.chatID) + ", entered name " + str(
					message.user.name) + " tried to stop the bot.")
		elif command == '/privacy':
			self.bot.sendMessage(message.user.chatID,
								 "We save everything you provide us for you to get the best experience.")
		elif command == '/subscribemenu':
			message.user.wantsMenu = True
			self.bot.sendMessage(message.user.chatID,
								 "You successfully subscribed to the daily menu push-service. Welcome aboard!")
		elif command == '/unsubscribemenu':
			message.user.wantsMenu = False
			self.bot.sendMessage(message.user.chatID,
								 "We are sorry to loose you as a subscriber and hope to see you here again.")

	def interpretMessage(self, message):
		type = message.user.getExpectedMessageType()

		if type == '':
			self.bot.sendMessage(message.user.chatID, 'I don\'t know what to do with your input :(')
		elif type == 'name':
			message.user.setName(message.text)
			welcomeMsg = 'Hello, ' + message.text + '! Pleased to meet you!'
			self.bot.sendMessage(message.user.chatID, welcomeMsg)

		message.user.setExpectedMessageType('')
