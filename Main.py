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
from maps import Directions
from memes import Memes
import logging


class Main:
	def __init__(self):
		self.token = self.getToken()
		self.lfetcher = lf.LectureFetcher()
		self.memes = Memes.Memes()
		self.bot = bt.Bot(telegram_token=self.token, users=self.getUsers(), lectureFetcher=self.lfetcher,
						  memes=self.memes)
		self.sentMenuToday = False
		self.sentLecturesToday = False
		self.askedForRatingToday = False

		# Configure logging
		logfile = 'logs/main_application_' + datetime.now().strftime('%Y-%m-%d') + '.log'
		logging.basicConfig(filename=logfile, level=logging.INFO,
							format='%(asctime)s---%(levelname)s:%(message)s',
							datefmt='%Y-%m-%d %H:%M:%S')

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
			await asyncio.sleep(29)
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
				logging.info('Sending menu')
				self.sendMenu()
			elif str(timeString) == '18:00' and not self.sentLecturesToday and sendPlanToday:
				self.sentLecturesToday = True
				logging.info('Sending lecture plans')
				self.sendLectures()
			elif str(timeString) == '14:30' and not self.askedForRatingToday and canteenOpen:
				self.askedForRatingToday = True
				logging.info('Sending menu rating requests')
				self.sendMenuRating()
			# Reset the boolean to send the menu for today again.
			# Do this only if seconds < 30 because otherwise it would happen twice.
			elif timeString == '23:59' and int(datetime.now().strftime('%S')) < 30:
				logging.info('Resetting variables and writing usage stats')
				self.writeUsageStats(True)
				self.sentMenuToday = False
				self.sentLecturesToday = False

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
			if ':05' in str(timeString):
				# Save user data
				usersList = []
				for user in self.bot.users:
					toAppend = {
						"chatID": user.chatID,
						"name": user.name,
						"expectedMsgType": user.expectedMessageType,
						"tempParams": user.tempParams,
						"wantsMenu": user.wantsMenu,
						"course": user.course,
						"wantsLecturePlan": user.wantsLecturePlan,
						"address": user.address,
						"wantsTransportInfo": user.wantsTransportInfo
					}
					usersList.append(toAppend)
				usersJson = json.dumps(usersList)

				with open('bot/userDict.json', 'w') as userFile:
					userFile.write(usersJson)
				userFile.close()

				# save rapla links
				self.lfetcher.writeLinksToJson()

				# save usage stats
				self.writeUsageStats(False)

				logging.info('Saved all preferences')

			# Check if it should stop
			if self.bot.tellMainToClose:
				break
		self.close()

	# Writes statistics to bot/usageStats.json in the format "DATE": ["AMOUNT_RECEIVED","AMOUNT_SENT"]
	def writeUsageStats(self, addLog):
		try:
			with open('bot/usageStats.json', 'r') as usageFile:
				usageJson = usageFile.read()
			usageFile.close()

			usageList = json.loads(usageJson)

			if (datetime.now().strftime('%Y-%m-%d')) in usageList:
				usageList[datetime.now().strftime('%Y-%m-%d')][0] += self.bot.messagesReceivedToday
				usageList[datetime.now().strftime('%Y-%m-%d')][1] += self.bot.messagesSentToday
			else:
				usageList[datetime.now().strftime('%Y-%m-%d')] = [0, 0]
				usageList[datetime.now().strftime('%Y-%m-%d')][0] = self.bot.messagesReceivedToday
				usageList[datetime.now().strftime('%Y-%m-%d')][1] = self.bot.messagesSentToday

			if addLog:
				self.bot.log(("We have " + str(len(self.bot.users)) + " users. Yesterday, I received "
							  + str(usageList[datetime.now().strftime('%Y-%m-%d')][0]) + " messages and sent "
							  + str(usageList[datetime.now().strftime('%Y-%m-%d')][1]) + " messages."))

			with open('bot/usageStats.json', 'w') as usageFile:
				usageFile.write(json.dumps(usageList))
			usageFile.close()
		except:  # If file doesnt exist
			with open('bot/usageStats.json', 'w') as usageFile:
				usageList = {
					datetime.now().strftime('%Y-%m-%d'): [self.bot.messagesReceivedToday, self.bot.messagesSentToday]
				}
				usageFile.write(json.dumps(usageList))
			usageFile.close()

		self.bot.messagesReceivedToday = 0
		self.bot.messagesSentToday = 0

	def sendMenu(self):
		for user in self.bot.users:
			if user.wantsMenu:
				fetchedMenu = menu.Reader(1).get_menu_as_arr()
				self.bot.sendMessage(user.chatID, "Good morning " + user.name + ", here is the menu for today:")
				for oneMenu in fetchedMenu:
					self.bot.sendMessage(user.chatID, oneMenu)

	def sendLectures(self):
		tomorrow = datetime.now() + timedelta(days=1)
		dateString = tomorrow.strftime("%Y-%m-%d")  # to get the YYYY-MM-DD format that is required

		for user in self.bot.users:
			if user.wantsLecturePlan and user.course != None:
				plan = self.lfetcher.getFormattedLectures(user.course, dateString)
				firstLectureTime = self.lfetcher.getFirstLectureTime(user.course, dateString)

				self.bot.sendMessage(user.chatID, ('Good evening ' + user.name + '. Tomorrow your first lecture begins '
												   + 'at ' + firstLectureTime + '. Here is the plan for tomorrow:'))
				self.bot.sendMessage(user.chatID, plan)

				# Send meme in Mathematik 1 is in the plan
				if 'Mathematik 1' in plan:
					meme = self.memes.getMeme(user.course, 'Felder-Memes', '-1')
					self.sendMeme(user, meme)
				elif 'Programmieren 1' in plan:
					meme = self.memes.getMeme(user.course, 'Geiger-Memes', '-1')
					self.sendMeme(user, meme)
				elif 'Theoretische Informatik I' in plan:
					meme = self.memes.getMeme(user.course, 'Rotzinger-Memes', '-1')
					self.sendMeme(user, meme)
				elif 'Projekt-Management 1' in plan:
					meme = self.memes.getMeme(user.course, 'Vetter-Memes', '-1')
					self.sendMeme(user, meme)

				if user.address != None and user.wantsTransportInfo and user.address != '':
					time = datetime(int(tomorrow.year), int(tomorrow.month), int(tomorrow.day),
									int(firstLectureTime[:2]), int(firstLectureTime[3:]))

					direc = Directions.Direction(time, user.address)
					trainPlan = direc.create_message()

					self.bot.sendMessage(user.chatID, 'Here are the public transport directions:')
					self.bot.sendMessage(user.chatID, trainPlan)

	# Send the given meme
	def sendMeme(self, user, meme):
		if meme[1]:
			meme_id = self.bot.sendPhoto(user.chatID, meme[0], False)
			self.bot.memes.addMemeId(user.course, meme[2], meme[3], meme_id)
		else:
			meme_id = self.bot.sendPhoto(user.chatID, meme[0], True)

			# If telegram returned an error whilst sending the photo via id, the id is invalid and has to be refreshed
			if meme_id == '-1':
				# Resets the id
				self.memes.addMemeId(user.course, meme[2], meme[3], '')

				# Fetches the meme again to get the file itself and send it to the user. Also note the new file_id.
				meme = self.memes.getMeme(user.course, list(self.memes.memeTypes)[meme[2]],
										  list(list(self.memes.memeTypes)[meme[2]])[meme[3]])
				meme_id = self.bot.sendPhoto(user.chatID, meme[0], False)
				self.memes.addMemeId(user.course, meme[2], meme[3], meme_id)

	def sendMenuRating(self):
		mealArr = menu.Reader(1).get_food_with_ratings_as_string_array()

		mealString = ("Meal 1:\n" + mealArr[0] + "\nMeal 2:\n" + mealArr[1] + "\nMeal 3:\n" + mealArr[2])
		for user in self.bot.users:
			if user.wantsMenu:
				self.bot.sendMessageWithOptions(user.chatID, (
							"Please rate your meal today. The available meals were:\n\n" + mealString),
												self.bot.generateReplyMarkup(
													[['Meal 1', 'Meal 2', 'Meal 3'], ['Don\'t rate']]))
				user.tempParams['ratingMealset'] = mealArr
				user.expectedMessageType = 'mealtoberated'

	def getToken(self):
		return telegram_secrets.token

	def getUsers(self):
		try:
			with open('bot/userDict.json', 'r') as userFile:
				usersJson = userFile.read()
			userFile.close()

			usersList = json.loads(usersJson)
		except:
			with open('bot/userDict.json', 'w') as userFile:
				userFile.close()
			usersList = []

		users = []
		for user in usersList:
			chatID = user.get('chatID')
			currentUser = usr.User(chatID)

			currentUser.name = name = user.get('name')
			currentUser.expectedMessageType = user.get('expectedMsgType')
			if user.get('tempParams') != None:
				currentUser.tempParams = user.get('tempParams')
			currentUser.wantsMenu = user.get('wantsMenu')
			currentUser.course = user.get('course')
			currentUser.wantsLecturePlan = user.get('wantsLecturePlan')
			currentUser.address = user.get('address')
			currentUser.wantsTransportInfo = user.get('wantsTransportInfo')

			users.append(currentUser)

		return users

	# Used to save all users to a dict before closing.
	def close(self):
		logging.info('Closing bot now')
		# save user data
		usersList = []
		for user in self.bot.users:
			toAppend = {
				"chatID": user.chatID,
				"name": user.name,
				"expectedMsgType": user.expectedMessageType,
				"tempParams": user.tempParams,
				"wantsMenu": user.wantsMenu,
				"course": user.course,
				"wantsLecturePlan": user.wantsLecturePlan,
				"address": user.address,
				"wantsTransportInfo": user.wantsTransportInfo
			}
			usersList.append(toAppend)
		usersJson = json.dumps(usersList)

		with open('bot/userDict.json', 'w') as userFile:
			userFile.write(usersJson)
		userFile.close()

		# Save rapla links
		self.lfetcher.writeLinksToJson()

		# Save usage stats
		self.writeUsageStats(False)

		# tell the bot to terminate
		self.bot.close()
		if len(self.bot.messages) > 0:
			logging.info('Bot has to handle more commands and will terminate once finished.')


# Starting method
if __name__ == "__main__":
	Main()
