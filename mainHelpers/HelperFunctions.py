import json
from datetime import datetime, timedelta
from menu import MenuSaver as menu
from maps import Directions
from bot import User as usr
import logging


class HelperFunctions:
	def __init__(self, main):
		self.main = main

	# Writes statistics to bot/usageStats.json in the format "DATE": ["AMOUNT_RECEIVED","AMOUNT_SENT"]
	def writeUsageStats(self, addLog):
		try:
			with open('bot/usageStats.json', 'r') as usageFile:
				usageJson = usageFile.read()
			usageFile.close()

			usageList = json.loads(usageJson)

			if (datetime.now().strftime('%Y-%m-%d')) in usageList:
				usageList[datetime.now().strftime('%Y-%m-%d')][0] += self.main.bot.messagesReceivedToday
				usageList[datetime.now().strftime('%Y-%m-%d')][1] += self.main.bot.messagesSentToday
			else:
				usageList[datetime.now().strftime('%Y-%m-%d')] = [0, 0]
				usageList[datetime.now().strftime('%Y-%m-%d')][0] = self.main.bot.messagesReceivedToday
				usageList[datetime.now().strftime('%Y-%m-%d')][1] = self.main.bot.messagesSentToday

			if addLog:
				self.main.bot.log(("We have " + str(len(self.main.bot.users)) + " users. Yesterday, I received "
								   + str(usageList[datetime.now().strftime('%Y-%m-%d')][0]) + " messages and sent "
								   + str(usageList[datetime.now().strftime('%Y-%m-%d')][1]) + " messages."))

			with open('bot/usageStats.json', 'w') as usageFile:
				usageFile.write(json.dumps(usageList, indent=4))
			usageFile.close()
		except:  # If file doesnt exist
			with open('bot/usageStats.json', 'w') as usageFile:
				usageList = {
					datetime.now().strftime('%Y-%m-%d'): [self.main.bot.messagesReceivedToday,
														  self.main.bot.messagesSentToday]
				}
				usageFile.write(json.dumps(usageList, indent=4))
			usageFile.close()

		self.main.bot.messagesReceivedToday = 0
		self.main.bot.messagesSentToday = 0

	def sendMenu(self):
		for user in self.main.bot.users:
			if user.wantsMenu:
				fetchedMenu = menu.Reader(1).get_menu_as_arr()
				self.main.bot.sendMessage(user.chatID, "Good morning " + user.name + ", here is the menu for today:")
				for oneMenu in fetchedMenu:
					self.main.bot.sendMessage(user.chatID, oneMenu)

	def sendLectures(self):
		tomorrow = datetime.now() + timedelta(days=1)
		dateString = tomorrow.strftime("%Y-%m-%d")  # to get the YYYY-MM-DD format that is required

		# Fetch the lecture times for all courses
		courses = self.main.lfetcher.getAllKnownCourses()
		# Dict is gonna hold course as key and list[plan, firstLectureTime, meme] as value
		courseDict = {}

		for course in courses:
			courseDict[course] = [self.main.lfetcher.getFormattedLectures(course, dateString),
								  self.main.lfetcher.getFirstLectureTime(course, dateString),
								  None]
			if course == 'TINF19B4':
				# Send memes for TINF19B4
				meme = None
				if 'Mathematik 1' in courseDict[course][0]:
					meme = self.main.memes.getMeme(course, 'Felder-Memes', '-1')
				elif 'Programmieren 1' in courseDict[course][0]:
					meme = self.main.memes.getMeme(course, 'Geiger-Memes', '-1')
				elif 'Theoretische Informatik I' in courseDict[course][0]:
					meme = self.main.memes.getMeme(course, 'Rotzinger-Memes', '-1')
				elif 'Projekt-Management 1' in courseDict[course][0]:
					meme = self.main.memes.getMeme(course, 'Vetter-Memes', '-1')
				elif 'Webengineering 1' in courseDict[course][0]:
					meme = self.main.memes.getMeme(course, 'Eisenbiegler-Memes', '-1')

				courseDict[course][2] = meme

		for user in self.main.bot.users:
			if user.wantsLecturePlan and user.course != None:
				plan = courseDict[user.course][0]
				firstLectureTime = courseDict[user.course][1]

				self.main.bot.sendMessage(user.chatID,
										  ('Good evening ' + user.name + '. Tomorrow your first lecture begins '
										   + 'at ' + firstLectureTime + '. Here is the plan for tomorrow:'))
				self.main.bot.sendMessage(user.chatID, plan)

				if courseDict[user.course][2] is not None:
					self.sendMeme(user, courseDict[user.course][2])

				if user.address is not None and user.wantsTransportInfo and user.address != '':
					time = datetime(int(tomorrow.year), int(tomorrow.month), int(tomorrow.day),
									int(firstLectureTime[:2]), int(firstLectureTime[3:]))

					try:
						direc = Directions.Direction(time, user.address)
						trainPlan = direc.create_message()

						self.main.bot.sendMessage(user.chatID, 'Here are the public transport directions:')
						self.main.bot.sendMessage(user.chatID, trainPlan)
					except:
						self.bot.sendMessage(self.message.user.chatID, (
								'Could not fetch public transport directions for your address '
								+ self.message.user.address))
						logging.warning('In HelperFunctions(): Fetching directions for address %s not successful.',
									  self.message.user.address)

	# Send the given meme
	def sendMeme(self, user, meme):
		if meme[1]:
			meme_id = self.main.bot.sendPhoto(user.chatID, meme[0], False)
			self.main.bot.memes.addMemeId(user.course, meme[2], meme[3], meme_id)
		else:
			meme_id = self.main.bot.sendPhoto(user.chatID, meme[0], True)

			# If telegram returned an error whilst sending the photo via id, the id is invalid and has to be refreshed
			if meme_id == '-1':
				# Resets the id
				self.main.memes.addMemeId(user.course, meme[2], meme[3], '')

				# Fetches the meme again to get the file itself and send it to the user. Also note the new file_id.
				meme = self.main.memes.getMeme(user.course, list(self.main.memes.memeTypes)[meme[2]],
											   list(list(self.main.memes.memeTypes)[meme[2]])[meme[3]])
				meme_id = self.main.bot.sendPhoto(user.chatID, meme[0], False)
				self.main.memes.addMemeId(user.course, meme[2], meme[3], meme_id)

	def sendMenuRating(self):
		mealArr = menu.Reader(1).get_food_with_ratings_as_string_array()

		mealString = ("Meal 1:\n" + mealArr[0] + "\nMeal 2:\n" + mealArr[1] + "\nMeal 3:\n" + mealArr[2])
		for user in self.main.bot.users:
			if user.wantsMenu and user.wantsToRateMeals:
				self.main.bot.sendMessageWithOptions(user.chatID, (
						"Please rate your meal today. The available meals were:\n\n" + mealString),
													 self.bot.generateReplyMarkup(
														 [['Meal 1', 'Meal 2', 'Meal 3'], ['Don\'t rate']]))
				user.tempParams['ratingMealset'] = mealArr
				user.expectedMessageType = 'mealtoberated'

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

			currentUser.name = user.get('name')
			currentUser.expectedMessageType = user.get('expectedMsgType')
			if user.get('tempParams') is not None:
				currentUser.tempParams = user.get('tempParams')
			if user.get('wantsMenu') is not None:
				currentUser.wantsMenu = user.get('wantsMenu')
			currentUser.course = user.get('course')
			if user.get('wantsLecturePlan') is not None:
				currentUser.wantsLecturePlan = user.get('wantsLecturePlan')
			currentUser.address = user.get('address')
			if user.get('wantsTransportInfo') is not None:
				currentUser.wantsTransportInfo = user.get('wantsTransportInfo')
			if user.get('wantsToRateMeals') is not None:
				currentUser.wantsToRateMeals = user.get('wantsToRateMeals')

			users.append(currentUser)

		return users
