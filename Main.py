"""
 Main file. Handles the bot activity.
"""
import json
import asyncio
from bot import Bot as bt
from bot import User as usr
import telegram_secrets
from datetime import datetime
from menu import MenuSaver as menu


class Main:
	def __init__(self):
		self.token = self.getToken()
		self.users = self.getUsers()
		self.bot = bt.Bot(telegram_token=self.token, users=self.users)
		self.sentMenuToday = False

		# Runs both loops independent from each other
		loop = asyncio.get_event_loop()
		cors = asyncio.wait([self.mainLoop(), self.pushLoop(), self.saveLoop()])
		loop.run_until_complete(cors)

	async def mainLoop(self):
		while True:
			# Wait for commands by users
			await self.bot.getUpdates()
			self.bot.handleMessages()

			# Check if it should stop
			if self.bot.tellMainToClose:
				break

		self.close()

	async def pushLoop(self):
		while True:
			await asyncio.sleep(30)
			now = datetime.now()
			timeString = now.strftime("%H:%M")
			weekday = now.weekday()
			if weekday < 5: # Because monday is 0...
				canteenOpen = True
			else:
				canteenOpen = False

			# run daily at 06:00 for all users that want the menu
			if str(timeString) == '06:00' and not self.sentMenuToday and canteenOpen:
				self.sentMenuToday = True
				self.sendMenu()
			# Reset the boolean to send the menu for today again
			elif timeString == '00:01':
				self.bot.log(("About to reset the sentMenuToday variable at " + now.strftime("%H:%M:%S")))
				self.sentMenuToday = False
				self.bot.log(("Reset complete at " + now.strftime("%H:%M:%S")))

			# Check if it should stop
			if self.bot.tellMainToClose:
				break
		self.close()

	# Used to save the current users all hour to minimize data loss in case of a server failure.
	async def saveLoop(self):
		while True:
			await asyncio.sleep(59)
			now = datetime.now()
			timeString = now.strftime("%H:%M")
			# run every full our (so at xx:00)
			if ':00' in str(timeString):
				usersList = []
				for user in self.bot.users:
					toAppend = {
						"chatID": user.chatID,
						"name": user.name,
						"expectedMsgType": user.expectedMessageType,
						"wantsMenu": user.wantsMenu
					}
					usersList.append(toAppend)
				usersJson = json.dumps(usersList)

				with open('bot/userDict.json', 'w') as userFile:
					userFile.write(usersJson)
				userFile.close()
				self.bot.log(("Saved all users at " + now.strftime("%H:%M:%S")))

			# Check if it should stop
			if self.bot.tellMainToClose:
				break
		self.close()

	def sendMenu(self):
		for user in self.users:
			if user.wantsMenu:
				fetchedMenu = menu.Reader(1).get_menu_as_arr()
				self.bot.sendMessage(user.chatID, "Good morning "+user.name+", here is the menu for today:")
				for oneMenu in fetchedMenu:
					self.bot.sendMessage(user.chatID, oneMenu)

	def getToken(self):
		return telegram_secrets.token

	def getUsers(self):
		with open('bot/userDict.json', 'r') as userFile:
			usersJson = userFile.read()
		userFile.close()

		usersList = json.loads(usersJson)

		users = []
		for user in usersList:
			chatID = user.get('chatID')
			name = user.get('name')
			expectedMsgType = user.get('expectedMsgType')
			wantsMenu = user.get('wantsMenu')
			currentUser = usr.User(chatID)
			currentUser.setName(name)
			currentUser.setExpectedMessageType(expectedMsgType)
			currentUser.wantsMenu = wantsMenu
			users.append(currentUser)

		return users

	# Used to save all users to a dict before closing.
	def close(self):
		usersList = []
		for user in self.bot.users:
			toAppend = {
				"chatID": user.chatID,
				"name": user.name,
				"expectedMsgType": user.expectedMessageType,
				"wantsMenu": user.wantsMenu
			}
			usersList.append(toAppend)
		usersJson = json.dumps(usersList)

		with open('bot/userDict.json', 'w') as userFile:
			userFile.write(usersJson)
		userFile.close()

		self.bot.close()
		if len(self.bot.messages) > 0:
			self.bot.log("Bot has to handle some more commands, please wait.")


# Starting method
if __name__ == "__main__":
	Main()
