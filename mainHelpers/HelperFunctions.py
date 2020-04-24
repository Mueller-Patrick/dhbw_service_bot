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
	def writeUsageStats(self, addLog: bool):
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

	def sendMenu(self, isCustomTime=False, customUser=None):
		"""
		Sends the menu to either all subscribers at normal time or a single subscriber at a special time
		:param isCustomTime: Optional. If this is a custom time user or the regular push at 06:00
		:param user: Optional. Just important if this is called for a specific user with a custom time
		:return: void
		"""

		try:
			if isCustomTime and not customUser.pauseAllNotifications:
				fetchedMenu = menu.Reader(1).get_menu_as_arr()
				self.main.bot.sendMessage(customUser.chatID,
										  "Good morning " + customUser.name + ", here is the menu for today:")
				for oneMenu in fetchedMenu:
					self.main.bot.sendMessage(customUser.chatID, oneMenu)
			else:
				# To save todays menu no matter if anyone gets the push, just so we have good statistics
				# TODO: Before deployment: Davids fix of false fetches required!!!
				# menu.Saver(1)

				# Iterate over users and push the menu
				for user in self.main.bot.users:
					if user.wantsMenu and not user.pauseAllNotifications and user.pushTimes['menu'] == '06:00':
						fetchedMenu = menu.Reader(1).get_menu_as_arr()
						self.main.bot.sendMessage(user.chatID,
												  "Good morning " + user.name + ", here is the menu for today:")
						for oneMenu in fetchedMenu:
							self.main.bot.sendMessage(user.chatID, oneMenu)
		except:
			logging.error('Error occured during menu fetching for daily menu push. No push has been sent.')

	def sendLectures(self, isCustomTime=False, customUser=None):
		if isCustomTime:
			tomorrow = datetime.now() + timedelta(days=1)
			dateString = tomorrow.strftime("%Y-%m-%d")

			if customUser.wantsLecturePlan and customUser.course != None:
				plan = self.main.lfetcher.getFormattedLectures(customUser.course, dateString)
				if not customUser.pauseAllNotifications:
					firstLectureTime = self.main.lfetcher.getFirstLectureTime(customUser.course, dateString)

					meme = None
					if customUser.course == 'TINF19B4':
						# Send memes for TINF19B4
						if 'Mathematik 1' in plan:
							meme = self.main.memes.getMeme(customUser.course, 'Felder-Memes', '-1')
						elif 'Programmieren 1' in plan:
							meme = self.main.memes.getMeme(customUser.course, 'Geiger-Memes', '-1')
						elif 'Theoretische Informatik I' in plan:
							meme = self.main.memes.getMeme(customUser.course, 'Rotzinger-Memes', '-1')
						elif 'Projekt-Management 1' in plan:
							meme = self.main.memes.getMeme(customUser.course, 'Vetter-Memes', '-1')
						elif 'Webengineering 1' in plan:
							meme = self.main.memes.getMeme(customUser.course, 'Eisenbiegler-Memes', '-1')

					self.main.bot.sendMessage(customUser.chatID, (
							'Good evening ' + customUser.name + '. Tomorrow your first lecture begins '
							+ 'at ' + firstLectureTime + '. Here is the plan for tomorrow:'))
					self.main.bot.sendMessage(customUser.chatID, plan)

					if meme is not None:
						self.sendMeme(customUser, meme)

					if customUser.address is not None and customUser.wantsTransportInfo and customUser.address != '':
						time = datetime(int(tomorrow.year), int(tomorrow.month), int(tomorrow.day),
										int(firstLectureTime[:2]), int(firstLectureTime[3:]))

						try:
							direc = Directions.Direction(time, customUser.address)
							trainPlan = direc.create_message()

							self.main.bot.sendMessage(customUser.chatID, 'Here are the public transport directions:')
							self.main.bot.sendMessage(customUser.chatID, trainPlan)
						except:
							self.main.bot.sendMessage(customUser.chatID, (
									'Could not fetch public transport directions for your address '
									+ customUser.address))
							logging.warning('In HelperFunctions(): Fetching directions for address %s not successful.',
											customUser.address)
				else:
					if 'Beginn Theoriephase' in plan:
						self.main.bot.sendMessageWithOptions(customUser.chatID,
															 ("I noticed that your next theory phase starts "
															  + "tomorrow. Do you want to unpause the push notifications?"),
															 self.main.bot.generateReplyMarkup([['Yes', 'No']]))
						customUser.expectedMessageType = 'wantstounpausepush'

		else:
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
				if user.wantsLecturePlan and user.course != None and user.pushTimes['lecture'] == '18:00':
					plan = courseDict[user.course][0]
					if not user.pauseAllNotifications:
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
								self.main.bot.sendMessage(user.chatID, (
										'Could not fetch public transport directions for your address '
										+ user.address))
								logging.warning(
									'In HelperFunctions(): Fetching directions for address %s not successful.',
									user.address)
					else:
						if 'Beginn Theoriephase' in plan:
							self.main.bot.sendMessageWithOptions(user.chatID,
																 ("I noticed that your next theory phase starts "
																  + "tomorrow. Do you want to unpause the push notifications?"),
																 self.main.bot.generateReplyMarkup([['Yes', 'No']]))
							user.expectedMessageType = 'wantstounpausepush'

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
			if user.wantsMenu and user.wantsToRateMeals and not user.pauseAllNotifications:
				self.main.bot.sendMessageWithOptions(user.chatID, (
						"Please rate your meal today. The available meals were:\n\n" + mealString),
													 self.main.bot.generateReplyMarkup(
														 [['Meal 1', 'Meal 2', 'Meal 3'], ['Don\'t rate']]))
				user.tempParams['ratingMealset'] = mealArr
				user.expectedMessageType = 'mealtoberated'

	def sendReturnDirections(self):
		for user in self.main.bot.users:
			if user.wantsTransportInfo:
				if user.address is not None and user.wantsTransportInfo and user.address != '' \
						and not user.pauseAllNotifications:
					now = datetime.now()
					lectures = self.main.lfetcher.getEventObjects(user.course, datetime.now().strftime('%Y-%m-%d'))
					endTime = str(lectures[len(lectures) - 1].end)[11:16]
					time = datetime(int(now.year), int(now.month), int(now.day),
									int(endTime[:2]), int(endTime[3:]))

					try:
						direc = Directions.Direction(time, user.address, True, True)
						trainPlan = direc.create_message()

						self.main.bot.sendMessage(user.chatID,
												  'Here are the public transport directions for your way home:')
						self.main.bot.sendMessage(user.chatID, trainPlan)
					except:
						self.main.bot.sendMessage(user.chatID, (
								'Could not fetch public transport directions for your address '
								+ user.address))
						logging.warning('In HelperFunctions(): Fetching directions for address %s not successful.',
										user.address)

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
			if user.get('pushTimes') is not None:
				currentUser.pushTimes = user.get('pushTimes')
			if user.get('pauseAllNotifications') is not None:
				currentUser.pauseAllNotifications = user.get('pauseAllNotifications')

			users.append(currentUser)

		return users

	"""
	Returns all preferred pushTimes in this format:
	
	{
		"time": [
			[TYPE, USER]
		]
	}
	
	So we have a dict with all requested times where at each time every user that wants to get some type of push at 
	this time is listed with his id and the type of message.
	"""

	def getPreferredPushTimes(self):
		ret = {}
		for user in self.main.bot.users:
			# If it is not the standard push time
			if user.pushTimes['menu'] != '06:00':
				# If the time already exists in the array
				if user.pushTimes['menu'] in list(ret):
					ret[user.pushTimes['menu']].append(['menu', user])
				else:
					ret[user.pushTimes['menu']] = [['menu', user]]

			if user.pushTimes['lecture'] != '18:00':
				if user.pushTimes['lecture'] in list(ret):
					ret[user.pushTimes['lecture']].append(['lecture', user])
				else:
					ret[user.pushTimes['lecture']] = [['lecture', user]]

		return ret
