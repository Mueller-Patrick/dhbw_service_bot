"""
 Bot class, an object of type bot is created in main.init() at startup with the required parameters.
"""
import requests
import telegram_secrets
from bot import Command as cmd, Message as msg, User as usr
import asyncio


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
		with open('bot/offsetFile.txt', 'r') as offsetFile:
			self.offsetParam['offset'] = int(offsetFile.read())
		offsetFile.close()

	def setOffset(self, newOffset):
		if newOffset != '':
			with open('bot/offsetFile.txt', 'w') as offsetFile:
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

	async def getUpdates(self):
		# If the bot is not about to be closed
		if not self.closeNow:
			# Wait for update
			self.getOffset()
			reqUrl = (self.telegramUrl + self.telegram_token + "getUpdates")
			update = requests.post(url=reqUrl, params=self.offsetParam)
			if update.json().get('ok'):
				# While no new messages have been received, fetch updates again. No offset needed because if you send an
				# offset one time, all 'older' messages get deleted.
				while len(update.json().get('result')) == 0:
					# Wait 1 second before fetching updates again to enable other asynchronous functions to work
					await asyncio.sleep(1)
					update = requests.post(url=reqUrl)

					# Check if bot should close now
					if self.closeNow:
						break

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
				self.log(update.json.get('error_code'))
				return update.json().get('error_code')

	# Used to handle all new commands and messages
	def handleMessages(self):
		for message in self.messages:
			if message.isCommand:
				cmd.Command(message, self).findCommand()
			else:
				cmd.Command(message, self).interpretMessage()
			self.messages.remove(message)

	def log(self, message):
		print(message)
		self.sendMessage(telegram_secrets.patrick_telegram_id, message)
		#self.sendMessage(patrickID.david_telegram_id, message)

	# Used to tell the bot to accept no more commands because it is about to be closed
	def close(self):
		self.closeNow = True
