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

	# Used to find the requested command
	def find_command(self, message):
		text = message.text
		print(text)
		if text in self.bot.commands:
			self.performCommand(text, message)
		else:
			self.sendMessage(message.user.chatID, "Unknown command. Say what?")

	def performCommand(self, command, message):
		if command == '/help':
			# TODO
			self.bot.log("User wants help")
		elif command == '/start':
			self.bot.sendMessage(message.user.chatID, "Please send me your name so we get to know each other")
			message.user.setExpectedMessageType('name')
		elif command == '/stopBot':
			if str(message.user.chatID) == str(patrickID.chatID):
				self.bot.log("Stopping the bot now.")
				self.bot.tellMainToClose = True
			else:
				self.bot.log("Wrong user " + str(message.user.chatID) + ", entered name " + str(
					message.user.name) + " tried to stop the bot.")

	def interpretMessage(self, message):
		type = message.user.getExpectedMessageType()

		if type == '':
			self.bot.sendMessage(message.user.chatID, 'I don\'t know what to do with your input :(')
		elif type == 'name':
			message.user.setName(message.text)
			welcomeMsg = 'Hello, ' + message.text + '! Pleased to meet you!'
			self.bot.sendMessage(message.user.chatID, welcomeMsg)

		message.user.setExpectedMessageType('')
