"""
 User class. Used to save every registered user with their personal preferences.
"""


class User:
	def __init__(self, chatID):
		self.chatID = chatID
		self.name = ''
		self.expectedMessageType = ''


	def setName(self, name):
		self.name = name

	# In a conversation, this allows the bot to set the expected message type of the next message from the user.
	# e.g. if the bot asks for the name, then the next expected message from the user is his name.
	def setExpectedMessageType(self, messageType):
		self.expectedMessageType = messageType

	def getExpectedMessageType(self):
		return self.expectedMessageType