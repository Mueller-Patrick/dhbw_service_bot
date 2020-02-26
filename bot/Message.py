"""
 Message class. Used to create a new Object "Message" every time a telegram message comes in.
 The message is then put in a list to be handeled. This way, its quite easy to handle multiple requests
 at the same time.
"""


class Message:
	def __init__(self, user, text):
		self.user = user
		self.text = text
		self.isCommand = False
		self.checkCommand()

	def checkCommand(self):
		# Look for commands
		if '/' in self.text:
			self.isCommand = True
		else:
			self.isCommand = False
