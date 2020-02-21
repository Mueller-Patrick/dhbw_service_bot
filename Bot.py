"""
 Bot class, an object of type bot is created in main.init() at startup with the required parameters.
"""
import requests
import json
import asyncio
import Message as msg
import User as usr
import patrickID
import Command as cmd


class Bot:
	def __init__(self, telegram_token, users):
		# Given parameters
		self.telegram_token = telegram_token

		# Fix parameters
		self.telegramUrl = 'https://api.telegram.org/bot'
		self.sendMessageParam = 'sendMessage'
		self.receiveUpdatesParam = 'getUpdates'

		# Params for the http request
		self.offsetParam = {'offset': 0}
		self.sendParams = {'chat_id': '',
						   'text': ''}

		# Get update offset
		self.getOffset()

		# Messages sent to the bot that have to be handles
		self.messages = []

		# All known users
		self.users = users

		# If the bot should now close
		self.closeNow = False
		self.tellMainToClose = False

	# External File handlers
	def getOffset(self):
		with open('offsetFile.txt', 'r') as offsetFile:
			self.offsetParam['offset'] = int(offsetFile.read())
		offsetFile.close()

	def setOffset(self, newOffset):
		if newOffset != '':
			with open('offsetFile.txt', 'w') as offsetFile:
				offsetFile.write(str(newOffset))
			offsetFile.close()

	# Api Handlers
	def sendMessage(self, chat, text):
		self.sendParams['chat_id'] = chat
		self.sendParams['text'] = text
		reqUrl = (self.telegramUrl + self.telegram_token + self.sendMessageParam)
		resp = requests.post(url=reqUrl, params=self.sendParams)

		# Reset send params after request
		self.sendParams = {'chat_id': '',
						   'text': ''}

	def getUpdates(self):
		if not self.closeNow:
			# Wait for update
			self.getOffset()
			reqUrl = (self.telegramUrl + self.telegram_token + "getUpdates")
			update = requests.post(url=reqUrl, params=self.offsetParam)
			if update.json().get('ok'):
				while len(update.json().get('result')) == 0:
					update = requests.post(url=reqUrl)

				# Set offset to be one higher than the offset of the latest update
				self.setOffset(update.json().get('result')[len(update.json().get('result')) - 1].get('update_id') + 1)

				# Iterate over updates and retrieve chat ids and related messages/commands
				for res in update.json().get('result'):
					chat = res.get('message').get('chat').get('id')
					text = res.get('message').get('text')

				if not text:
					self.sendMessage(chat, "Unknown input format. Don't mess with me, fella!")
				else:
					currentUser = usr.User('0') # Creates an empty user object to be populated later
					for user in self.users:
						if user.chatID == chat:
							currentUser = user

					if not currentUser.chatID == '0':
						# If it is an existing user, get record for this user and create a new message entity
						# with the user as parameter.
						self.messages.append(msg.Message(currentUser, text))
					else:
						# If unknown user, create a new user and write it to users list. Also create a new message
						# entity with the user as parameter.
						newUser = usr.User(chat)
						self.users.append(newUser)
						self.messages.append(msg.Message(newUser, text))

			else:
				return update.json().get('error_code')

	# Used to handle all new commands and messages
	def handleMessages(self):
		for message in self.messages:
			if message.isCommand:
				cmd.Command(message, self).find_command(message)
			else:
				cmd.Command(message, self).interpretMessage(message)
			self.messages.remove(message)

	def log(self, message):
		print(message)
		self.sendMessage(patrickID.chatID, message)
		#self.sendMessage(patrickID.davidID, message)

	# Used to tell the bot to accept no more commands because it is about to be closed
	def close(self):
		self.closeNow = True
