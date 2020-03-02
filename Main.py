"""
 Main file. Handles the bot activity.
"""
import json
import asyncio
from bot import Bot as bt
from bot import User as usr
import telegram_secrets
from datetime import datetime
from datetime import timedelta
from menu import MenuSaver as menu
from lecturePlan import LectureFetcher as lf


class Main:
	def __init__(self):
		self.token = self.getToken()
		self.lfetcher = lf.LectureFetcher()
		self.bot = bt.Bot(telegram_token=self.token, users=self.getUsers(), lectureFetcher=self.lfetcher)
		self.sentMenuToday = False
		self.sentLecturesToday = False

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

			# For menu push
			if weekday < 5:  # Because monday is 0...
				canteenOpen = True
			else:
				canteenOpen = False

			# For lecture Plan push
			if weekday < 4 or weekday == 6:  # Monday to Thursday and also Sunday
				sendPlanToday = True
			else:
				sendPlanToday = False

			# run daily at 06:00 for all users that want the menu
			if str(timeString) == '06:00' and not self.sentMenuToday and canteenOpen:
				self.sentMenuToday = True
				self.sendMenu()
			elif str(timeString) == '18:00' and not self.sentLecturesToday and sendPlanToday:
				self.sentLecturesToday = True
				self.sendLectures()
			# Reset the boolean to send the menu for today again
			elif timeString == '00:01':
				self.bot.log(("About to reset the sentMenuToday variable at " + now.strftime("%H:%M:%S")))
				self.sentMenuToday = False
				self.sentLecturesToday = False
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
				# Save user data
				usersList = []
				for user in self.bot.users:
					toAppend = {
						"chatID": user.chatID,
						"name": user.name,
						"expectedMsgType": user.expectedMessageType,
						"wantsMenu": user.wantsMenu,
						"course": user.course,
						"wantsLecturePlan": user.wantsLecturePlan
					}
					usersList.append(toAppend)
				usersJson = json.dumps(usersList)

				with open('bot/userDict.json', 'w') as userFile:
					userFile.write(usersJson)
				userFile.close()

				# save rapla links
				self.lfetcher.writeLinksToJson()

				self.bot.log(("Saved all preferences at " + now.strftime("%H:%M:%S")))

			# Check if it should stop
			if self.bot.tellMainToClose:
				break
		self.close()

	def sendMenu(self):
		for user in self.bot.users:
			if user.wantsMenu:
				fetchedMenu = menu.Reader(1).get_menu_as_arr()
				self.bot.sendMessage(user.chatID, "Good morning " + user.name + ", here is the menu for today:")
				for oneMenu in fetchedMenu:
					self.bot.sendMessage(user.chatID, oneMenu)

	def sendLectures(self):
		now = datetime.now()
		tomorrow = now + timedelta(days=1)
		dateString = tomorrow.strftime("%Y-%m-%d")  # to get the YYYY-MM-DD format that is required

		for user in self.bot.users:
			if user.wantsLecturePlan:
				plan = self.lfetcher.getFormattedLectures(user.course, dateString)
				firstLectureTime = self.lfetcher.getFirstLectureTime(user.course, dateString)

				self.bot.sendMessage(user.chatID, ('Good evening ' + user.name + '. Tomorrow your first lecture begins '
												   + 'at ' + firstLectureTime + '. Here is the plan for tomorrow:'))
				self.bot.sendMessage(user.chatID, plan)

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
			currentUser = usr.User(chatID)

			currentUser.name = name = user.get('name')
			currentUser.expectedMessageType = user.get('expectedMsgType')
			currentUser.wantsMenu = user.get('wantsMenu')
			currentUser.course = user.get('course')
			currentUser.wantsLecturePlan = user.get('wantsLecturePlan')

			users.append(currentUser)

		return users

	# Used to save all users to a dict before closing.
	def close(self):
		# save user data
		usersList = []
		for user in self.bot.users:
			toAppend = {
				"chatID": user.chatID,
				"name": user.name,
				"expectedMsgType": user.expectedMessageType,
				"wantsMenu": user.wantsMenu,
				"course": user.course,
				"wantsLecturePlan": user.wantsLecturePlan
			}
			usersList.append(toAppend)
		usersJson = json.dumps(usersList)

		with open('bot/userDict.json', 'w') as userFile:
			userFile.write(usersJson)
		userFile.close()

		# Save rapla links
		self.lfetcher.writeLinksToJson()

		# tell the bot to terminate
		self.bot.close()
		if len(self.bot.messages) > 0:
			self.bot.log("Bot has to handle some more commands, please wait.")


# Starting method
if __name__ == "__main__":
	Main()
