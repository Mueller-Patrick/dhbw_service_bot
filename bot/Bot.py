"""
 Bot class, an object of type bot is created in main.init() at startup with the required parameters.
"""
import requests
import telegram_secrets
from bot import Command as cmd, Message as msg, User as usr
import asyncio
import json
from datetime import datetime


class Bot:
	def __init__(self, telegram_token, users, lectureFetcher, memes):
		# Given parameters
		self.telegram_token = telegram_token

		# Fix parameters
		self.telegramUrl = 'https://api.telegram.org/bot'
		self.sendMessageParam = 'sendMessage'
		self.receiveUpdatesParam = 'getUpdates'
		self.sendPhotoParam = 'sendPhoto'
		self.deleteMessageParam = 'deleteMessage'

		# Param for the http request
		self.offsetParam = {'offset': 0}

		# Get update offset
		self.getOffset()

		# Messages sent to the bot that have to be handles
		self.messages = []

		# All known users
		self.users = users

		# If the bot should now close
		self.closeNow = False
		self.tellMainToClose = False

		# The LectureFetcher instance
		self.lectureFetcher = lectureFetcher

		# The Memes instance
		self.memes = memes

		# To create statistics on how much messages have been handled
		# If the bot restarted that day, this is the number of handled messages since the restart.
		self.messagesReceivedToday = 0
		self.messagesSentToday = 0

	# External File handlers
	def getOffset(self):
		try:
			with open('bot/offsetFile.txt', 'r') as offsetFile:
				self.offsetParam['offset'] = int(offsetFile.read())
			offsetFile.close()
		except:
			with open('bot/offsetFile.txt', 'w') as offsetFile:
				offsetFile.close()
			self.offsetParam['offset'] = 0

	def setOffset(self, newOffset):
		if newOffset != '':
			with open('bot/offsetFile.txt', 'w') as offsetFile:
				offsetFile.write(str(newOffset))
			offsetFile.close()

	# Sends a param to the user so that current custom keyboards get removed.
	def sendMessage(self, chat, text):
		sendParams = {'chat_id': chat,
					  'text': text,
					  'reply_markup': '{"remove_keyboard": true}',
					  'parse_mode': 'Markdown'}
		reqUrl = (self.telegramUrl + self.telegram_token + self.sendMessageParam)
		resp = requests.post(url=reqUrl, params=sendParams)
		self.messagesSentToday += 1

		if not resp.json().get('ok'):
			print('Error on sending text: ' + resp.json())

	# The options param has to be a [[String]], so an Array of rows with an array of buttons in JSON format.
	def sendMessageWithOptions(self, chat, text, options):
		sendParams = {
			'chat_id': chat,
			'text': text,
			'reply_markup': options,
			'parse_mode': 'Markdown'
		}
		reqUrl = (self.telegramUrl + self.telegram_token + self.sendMessageParam)
		resp = requests.post(url=reqUrl, params=sendParams)
		self.messagesSentToday += 1

		if not resp.json().get('ok'):
			print('Error on sending text with options: ' + resp.json())

	def sendPhoto(self, chat, photo, isFileId):
		if isFileId:
			sendParams = {
				'chat_id': chat,
				'reply_markup': '{"remove_keyboard": true}',
				'photo': photo
			}
			files = {}
		else:
			sendParams = {
				'chat_id': chat,
				'reply_markup': '{"remove_keyboard": true}'
			}
			files = {
				'photo': photo
			}
		reqUrl = (self.telegramUrl + self.telegram_token + self.sendPhotoParam)
		resp = requests.post(url=reqUrl, params=sendParams, files=files)
		print('Sent photo, got answer ' + str(resp.json().get('ok')))
		self.messagesSentToday += 1

		# If the photo was successful sent, return the file_id. Else, return -1
		if resp.json().get('ok'):
			# Returns the file id so we don't have to send this picture again in the future
			return resp.json().get('result').get('photo')[0].get('file_id')
		else:
			print('Error on sending picture: ' + resp.json())
			return '-1'

	def generateReplyMarkup(self, options):
		reply = ('{"keyboard": ' + json.dumps(options) + ','
				 + '"one_time_keyboard": true,'
				 + '"resize_keyboard": true}')
		return reply

	def deleteMessage(self, chatID, messageID):
		sendParams = {
			'chat_id': chatID,
			'message_id': messageID
		}
		reqUrl = (self.telegramUrl + self.telegram_token + self.deleteMessageParam)
		resp = requests.post(url=reqUrl, params=sendParams)

		if not resp.json().get('ok'):
			print('Error on deleting message: ' + resp.json())

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
					messageID = str(res.get('message').get('message_id'))

					# Print the first 10 characters of each message for debugging.
					if len(text) < 11:
						print("Received message at " + datetime.now().strftime('%H:%M:%S') + ', Text: ' + text)
					else:
						print("Received message at " + datetime.now().strftime('%H:%M:%S') + ', Text: ' + text[:10] + '...')

					if not text:
						self.sendMessage(chat, "Unknown input format. Don't mess with me, fella!")
					else:
						currentUser = usr.User('0')  # Creates an empty user object to be populated later
						for user in self.users:
							if user.chatID == chat:
								currentUser = user

						if not currentUser.chatID == '0':
							# If it is an existing user, get record for this user and create a new message entity
							# with the user as parameter.
							self.messages.append(msg.Message(currentUser, text, messageID))
						else:
							# If unknown user, create a new user and write it to users list. Also create a new message
							# entity with the user as parameter.
							newUser = usr.User(chat)
							self.users.append(newUser)
							self.messages.append(msg.Message(newUser, text, messageID))

			else:
				print('Error on update: ' + update.json())
				return update.json().get('error_code')

	# Used to handle all new commands and messages
	def handleMessages(self):
		for message in self.messages:
			# self.log(("Handling message by " + message.user.name))
			if message.isCommand:
				cmd.Command(message, self).findCommand()
			else:
				cmd.Command(message, self).interpretMessage()
			self.messagesReceivedToday += 1
		self.messages.clear()

	# self.log("Handled all current messages")

	def log(self, message):
		print(message)
		self.sendMessage(telegram_secrets.patrick_telegram_id, message)

	# self.sendMessage(patrickID.david_telegram_id, message)

	# Used to tell the bot to accept no more commands because it is about to be closed
	def close(self):
		self.closeNow = True
