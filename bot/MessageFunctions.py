import telegram_secrets
from menu import MenuSaver as menu
from datetime import datetime, timedelta
from maps import Directions
from menu import Rater
import logging


class MessageFunctions:
	def __init__(self, message, bot):
		self.message = message
		self.bot = bot

	# Called when user sends a normal message but we don't expect any input
	def message_unknown(self):
		self.bot.sendMessageWithOptions(self.message.user.chatID,
										'I don\'t know what to do with your input :( Use /help to get help:',
										self.bot.generateReplyMarkup([['/help']]))

	# Called when user registers for the first time and sends his name
	def message_startname(self):
		self.message.user.name = self.message.text
		welcomeMsg = (
				'Hello, *' + self.message.text + '*! Pleased to meet you! To get you started, I\'ll now explain to '
				+ 'you the stuff I\'m able to do and what commands you may use.\n\n'
				+ 'To *set everything up*, use the /settings command. Under \'Personal Information\' you can add or '
				+ 'change the Information that I need about you to provide my services to you. Under \'Subscription-Settings\' '
				+ 'you can set up which push-messages you want to get from me.\n\n'
				+ 'My Push-Service includes lecture plan pushes, daily menu pushes and public transport information for '
				+ 'each day.\n\nTo *get the daily menu at any time*, send /getmenu. If you forgot '
				+ '*what lectures you have today*, type /getlectures to get the plan again.\n\n'
				+ 'We all love *memes*. Type /getmeme to access all of your favorite ones.\n\n'
				+ 'If you find a *bug*, report it via /reportbug.\n\nAnd because I '
				+ 'respect your *privacy*, type /privacy and /whatdoyouknowaboutme to get Info about what we save '
				+ 'about you. Last but not least, type /help to get a list of available commands.\n\n'
				+ 'If you have any questions, contact @PaddyOfficial on Telegram.')
		self.bot.sendMessage(self.message.user.chatID, welcomeMsg)
		self.message.user.expectedMessageType = ''

	# Called when Patrick wants to broadcast something
	def message_broadcastmessage(self):
		for user in self.bot.users:
			self.bot.sendMessage(user.chatID, self.message.text)

		self.message.user.expectedMessageType = ''

	# Called when user sends the day he wants the lecture plan for
	def message_lectureplanday(self):
		if self.message.text == 'Today':
			day = 0
		else:
			day = 1

		forDay = datetime.now() + timedelta(days=day)
		dateString = forDay.strftime("%Y-%m-%d")
		plan = self.bot.lectureFetcher.getFormattedLectures(self.message.user.course, dateString)
		firstLectureTime = self.bot.lectureFetcher.getFirstLectureTime(self.message.user.course, dateString)

		if not plan:
			self.bot.sendMessage(self.message.user.chatID, 'No more lectures for that day.')
		else:
			self.bot.sendMessage(self.message.user.chatID, plan)

			if self.message.user.wantsTransportInfo and self.message.user.address is not None and self.message.user.address != '':
				time = datetime(int(forDay.year), int(forDay.month), int(forDay.day),
								int(firstLectureTime[:2]), int(firstLectureTime[3:]))

				if time < datetime.now():
					self.bot.sendMessage(self.message.user.chatID,
										 ('Your first lecture already began, so I suppose you '
										  + 'are at the DHBW already and don\'t need the public transport Info.'))
				else:
					direc = Directions.Direction(time, self.message.user.address)
					trainPlan = direc.create_message()

					self.bot.sendMessage(self.message.user.chatID, 'Here are the public transport directions:')
					self.bot.sendMessage(self.message.user.chatID, trainPlan)

		self.message.user.expectedMessageType = ''

	# Called when user sends the day he wants the menu for
	def message_menuday(self):
		if self.message.text == 'Today':
			day = 0
		elif self.message.text == 'Tomorrow':
			day = 1
		else:
			day = 0

		forDay = datetime.now() + timedelta(days=day)
		weekday = forDay.weekday()
		if weekday < 5:  # Because monday is 0...
			fetchedMenu = menu.Reader(day + 1).get_menu_as_arr()  # day+1 because 1 is today, 2 is tomorrow...
			self.bot.sendMessage(self.message.user.chatID, "Here you go: ")
			for oneMenu in fetchedMenu:
				self.bot.sendMessage(self.message.user.chatID, oneMenu)
		else:
			self.bot.sendMessage(self.message.user.chatID, "The canteen is closed there. Hence no menu for you.")

	# Called when user sends the type of meme he wants to get
	def message_memetype(self):
		if self.message.text == 'Random':
			self.message.text = '-1'
			self.message.user.tempParams['requestedMemeType'] = '-1'
			self.message_memeid()
		else:
			memeIds = self.bot.memes.getMemeId(self.message.user.course, self.message.text)
			memeIdsConverted = []

			for meme in memeIds:
				memeIdsConverted.append([meme])
			memeIdsConverted.append(['Random'])

			self.bot.sendMessageWithOptions(self.message.user.chatID, "Please select the meme:",
											self.bot.generateReplyMarkup(memeIdsConverted))
			self.message.user.tempParams['requestedMemeType'] = self.message.text
			self.message.user.expectedMessageType = 'memeid'

	# Called when user sends the exact meme he wants to get
	def message_memeid(self):
		# Memes.getMeme returns a list in this format: ['MEME_FILE_OR_ID', FETCH_ID, TYPEINDEX, MEMEINDEX]
		# If the meme has not been uploaded to telegram yet, the file itself is sent with the boolean FETCH_ID
		# set to true so the file_id provided by telegram gets saved.

		self.bot.sendMessage(self.message.user.chatID, "Here is the requested meme:")

		if self.message.text == 'Random':
			self.message.text = '-1'

		meme = self.bot.memes.getMeme(self.message.user.course, self.message.user.tempParams['requestedMemeType'],
									  self.message.text)
		# If the id is needed, clearly this getting sent here is the photo itself
		if meme[1]:
			meme_id = self.bot.sendPhoto(self.message.user.chatID, meme[0], False)
			self.bot.memes.addMemeId(self.message.user.course, meme[2], meme[3], meme_id)
		else:
			meme_id = self.bot.sendPhoto(self.message.user.chatID, meme[0], True)

			# If telegram returned an error whilst sending the photo via id, the id is invalid and has to be refreshed
			if meme_id == '-1':
				# Resets the id
				self.bot.memes.addMemeId(self.message.user.course, meme[2], meme[3], '')

				# Fetches the meme again to get the file itself and send it to the user. Also note the new file_id.
				meme = self.bot.memes.getMeme(self.message.user.course,
											  self.message.user.tempParams['requestedMemeType'], self.message.text)
				meme_id = self.bot.sendPhoto(self.message.user.chatID, meme[0], False)
				self.bot.memes.addMemeId(self.message.user.course, meme[2], meme[3], meme_id)

		self.message.user.expectedMessageType = ''
		self.message.user.tempParams['requestedMemeType'] = ''

	# Called when user sends the meal that he wants to rate
	def message_mealtoberated(self):
		mealToBeRated = self.message.text

		if mealToBeRated == 'Don\'t rate':
			self.bot.sendMessage(self.message.user.chatID, "Ok, no rating. This is fine.")
			self.message.user.expectedMessageType = ''
		else:
			if mealToBeRated in ('Meal 1', 'Meal 2', 'Meal 3'):
				self.message.user.tempParams['ratedMeal'] = mealToBeRated
				self.bot.sendMessageWithOptions(self.message.user.chatID, "How many stars do you give?",
												self.bot.generateReplyMarkup(
													[['0 ⭐', '1 ⭐', '2 ⭐', '3 ⭐', '4 ⭐', '5 ⭐']]))
				self.message.user.expectedMessageType = 'mealrating'
			else:
				self.bot.sendMessageWithOptions(self.message.user.chatID, "Wrong input. Try again",
												self.bot.generateReplyMarkup(
													[['Meal 1', 'Meal 2', 'Meal 3'], ['Don\'t rate']]))

	# Called when user sends the rating for his meal
	def message_mealrating(self):
		rating = self.message.text
		mealArr = self.message.user.tempParams['ratingMealset']

		rating = int(rating[:1])

		if rating in (0, 5):
			ratedMeal = mealArr[int(self.message.user.tempParams['ratedMeal'][5]) - 1]
			Rater.Rater(ratedMeal, rating)
			self.bot.sendMessage(self.message.user.chatID, "Thank you for rating! 😁")
			self.message.user.tempParams['ratingMealset'] = ''
			self.message.user.tempParams['ratedMeal'] = ''
			self.message.user.expectedMessageType = ''
		else:
			self.bot.sendMessageWithOptions(self.message.user.chatID, "Wrong input. Try again.",
											self.bot.generateReplyMarkup([['0 ⭐', '1 ⭐', '2 ⭐', '3 ⭐', '4 ⭐', '5 ⭐']]))

	# Called when user sends the description of a bug he encountered
	def message_bugdescription(self):
		self.bot.log(('Got a bug report by ' + self.message.user.name + ':\n\n' + self.message.text))
		self.bot.sendMessage(self.message.user.chatID, "Thanks for reporting this bug. We will fix it ASAP.")
		self.message.user.expectedMessageType = ''

	# Called when user sends the type of settings he wants to change
	def message_settingstype(self):
		if self.message.text == '️🧍 Personal Information':
			self.bot.sendMessageWithOptions(self.message.user.chatID,
											"Here are the Information about you that you can change:",
											self.bot.generateReplyMarkup(
												[['🗣 Name'], ['🚅 Address'], ['🏫 Course'], ['⏪ Back']]))
			self.message.user.expectedMessageType = 'settingspersonalinfo'
		elif self.message.text == '📲 Subscription-Settings':
			# Fetch the user's subscriptions to show them the current status
			options = []
			if self.message.user.wantsMenu:
				options.append(['❌ Unsubscribe the Menu Push'])
			else:
				options.append(['✅ Subscribe the Menu Push'])

			if self.message.user.wantsLecturePlan:
				options.append(['❌ Unsubscribe the Lecture Plan Push'])
			else:
				options.append(['✅ Subscribe the Lecture Plan Push'])

			if self.message.user.wantsTransportInfo:
				options.append(['❌ Unsubscribe the Public Transport Info'])
			else:
				options.append(['✅ Subscribe the Public Transport Info'])

			options.append(['⏪ Back'])

			self.bot.sendMessageWithOptions(self.message.user.chatID,
											"Here are your Subscriptions:",
											self.bot.generateReplyMarkup(options))
			self.message.user.expectedMessageType = 'settingssubscriptions'
		elif self.message.text == '🧨 Cancel':
			self.bot.sendMessage(self.message.user.chatID, "ALLES BLEIBT HIER WIE ES IST.")
			self.message.user.expectedMessageType = ''
		else:
			self.bot.sendMessageWithOptions(self.message.user.chatID, "Wrong input. Please try again:",
											self.bot.generateReplyMarkup(
												[['️🧍 Personal Information'], ['📲 Subscription-Settings'],
												 ['🧨 Cancel']]))

	# Called when user sends the information that he wants to change his personal info
	def message_settingspersonalinfo(self):
		if self.message.text == '🗣 Name':
			self.bot.sendMessage(self.message.user.chatID,
								 "So you changed your name, huh? Interesting. Alright, send me your new one then:")
			self.message.user.expectedMessageType = 'changepersonalinfo'
			self.message.user.tempParams['personalInfoToBeChanged'] = 'name'
		elif self.message.text == '🚅 Address':
			self.bot.sendMessage(self.message.user.chatID,
								 "Ok, please provide me the new address where you would like to get on the train:")
			self.message.user.expectedMessageType = 'changepersonalinfo'
			self.message.user.tempParams['personalInfoToBeChanged'] = 'address'
		elif self.message.text == '🏫 Course':
			if self.message.user.course != '':
				self.bot.sendMessage(self.message.user.chatID,
									 ("What the hell? How can one change their course? But you must not question "
									  + "the master, I guess... Go on then, what's your new course?"))
			else:
				self.bot.sendMessage(self.message.user.chatID, "Please send me your course name:")
			self.message.user.expectedMessageType = 'changepersonalinfo'
			self.message.user.tempParams['personalInfoToBeChanged'] = 'course'
		elif self.message.text == '⏪ Back':
			self.bot.sendMessageWithOptions(self.message.user.chatID, 'What do you want to change?',
											self.bot.generateReplyMarkup(
												[['️🧍 Personal Information'], ['📲 Subscription-Settings'],
												 ['🧨 Cancel']]))
			self.message.user.expectedMessageType = 'settingstype'
		else:
			self.bot.sendMessageWithOptions(self.message.user.chatID, "Wrong input. Please try again:",
											self.bot.generateReplyMarkup(
												[['🗣 Name'], ['🚅 Address'], ['🏫 Course'], ['⏪ Back']]))

	# Called when user sends the information that he wants to change his subscription settings
	def message_settingssubscriptions(self):
		if self.message.text == '❌ Unsubscribe the Menu Push':
			self.message.user.wantsMenu = False
			self.bot.sendMessage(self.message.user.chatID, "💔 Unsubscribed you from the menu push")
			self.message.user.expectedMessageType = ''
		elif self.message.text == '✅ Subscribe the Menu Push':
			self.message.user.wantsMenu = True
			self.bot.sendMessage(self.message.user.chatID, "❤️ Subscribed you to the menu push")
			self.message.user.expectedMessageType = ''
		elif self.message.text == '❌ Unsubscribe the Lecture Plan Push':
			self.message.user.wantsLecturePlan = False
			self.bot.sendMessage(self.message.user.chatID, "💔 Unsubscribed you from the lecture plan push")
			self.message.user.expectedMessageType = ''
		elif self.message.text == '✅ Subscribe the Lecture Plan Push':
			self.message.user.wantsLecturePlan = True
			self.bot.sendMessage(self.message.user.chatID, "❤️ Subscribed you to the lecture plan push")
			# Check if the user has already entered his course
			if self.message.user.course == '' or self.message.user.course is None:
				self.bot.sendMessageWithOptions(self.message.user.chatID,
												("‼️ You have not entered your course yet. "
												 + "Please do that via /settings -> Personal Information."),
												self.bot.generateReplyMarkup([['/settings']]))
			self.message.user.expectedMessageType = ''
		elif self.message.text == '❌ Unsubscribe the Public Transport Info':
			self.message.user.wantsTransportInfo = False
			self.bot.sendMessage(self.message.user.chatID, "💔 Unsubscribed you from the public transport info")
			self.message.user.expectedMessageType = ''
		elif self.message.text == '✅ Subscribe the Public Transport Info':
			self.message.user.wantsTransportInfo = True
			self.bot.sendMessage(self.message.user.chatID, "❤️ Subscribed you to the public transport info")
			# Check if the user has already entered his address
			if self.message.user.address == '' or self.message.user.address is None:
				self.bot.sendMessageWithOptions(self.message.user.chatID, ("‼️ You have not entered your address yet. "
																		   + "Please do that via /settings -> Personal Information"),
												self.bot.generateReplyMarkup([['/settings']]))
			self.message.user.expectedMessageType = ''
		elif self.message.text == '⏪ Back':
			self.bot.sendMessageWithOptions(self.message.user.chatID, 'What do you want to change?',
											self.bot.generateReplyMarkup([['️🧍 Personal Information'],
																		  ['📲 Subscription-Settings'], ['🧨 Cancel']]))
			self.message.user.expectedMessageType = 'settingstype'
		else:
			# Fetch the user's subscriptions to show them the current status
			options = []
			if self.message.user.wantsMenu:
				options.append(['❌ Unsubscribe the Menu Push'])
			else:
				options.append(['✅ Subscribe the Menu Push'])

			if self.message.user.wantsLecturePlan:
				options.append(['❌ Unsubscribe the Lecture Plan Push'])
			else:
				options.append(['✅ Subscribe the Lecture Plan Push'])

			if self.message.user.wantsTransportInfo:
				options.append(['❌ Unsubscribe the Public Transport Info'])
			else:
				options.append(['✅ Subscribe the Public Transport Info'])

			options.append(['⏪ Back'])

			self.bot.sendMessageWithOptions(self.message.user.chatID,
											"Wrong input. Please try again:",
											self.bot.generateReplyMarkup(options))

	# Called when the user sends the new info about him
	def message_changepersonalinfo(self):
		type = self.message.user.tempParams['personalInfoToBeChanged']

		if type == 'name':
			self.message.user.name = self.message.text
			self.bot.sendMessage(self.message.user.chatID, ("Successfully changed your name to " + self.message.text))
			self.message.user.expectedMessageType = ''
			self.message.user.tempParams['personalInfoToBeChanged'] = ''
		elif type == 'address':
			self.message.user.address = self.message.text
			self.bot.sendMessage(self.message.user.chatID,
								 ("Successfully changed your address to " + self.message.text))
			self.message.user.expectedMessageType = ''
			self.message.user.tempParams['personalInfoToBeChanged'] = ''
		elif type == 'course':
			if self.bot.lectureFetcher.firstUserInCourse(self.message.text):
				self.message.user.course = self.message.text
				self.bot.sendMessage(self.message.user.chatID,
									 "You are the first user in this course. Please send me "
									 + "a password that future users have to enter in order to "
									 + "join this course. Write it down somewhere save because "
									 + "I will delete your message after I received it:")
				self.message.user.expectedMessageType = 'newcoursepassword'
				self.bot.lectureFetcher.setUserOfCourse(self.message.user.course)
			else:
				self.message.user.tempParams['enteredCourse'] = self.message.text
				self.bot.sendMessage(self.message.user.chatID, "Please send me the password for " + self.message.text)
				self.message.user.expectedMessageType = 'coursepassword'
			self.message.user.tempParams['personalInfoToBeChanged'] = ''
		else:
			logging.warning(
				'Wrong type for changing personal info given in MessageFunctions.message_changepersonalinfo. Given type: %s',
				type)

	# Called when the user sends the new password for a course
	def message_newcoursepassword(self):
		password = self.message.text
		self.bot.deleteMessage(self.message.user.chatID, self.message.id)

		self.bot.memes.setPassword(self.message.user.course, password)

		if self.bot.lectureFetcher.checkForCourse(self.message.user.course):
			self.bot.sendMessage(self.message.user.chatID, (
					"You successfully joined the course " + self.message.user.course + " and set the passwort."))
			self.message.user.expectedMessageType = ''
		else:
			self.bot.sendMessage(self.message.user.chatID,
								 ("I don\'t know the RaPla link for this course yet. Would you "
								  + "be so kind and send me the link?"))
			self.message.user.expectedMessageType = "raplalink"

	# Called when the users sends the password for a course
	def message_coursepassword(self):
		if self.message.text == 'cancel':
			self.bot.sendMessage(self.message.user.chatID, 'Cancelled course setup.')
			self.message.user.expectedMessageType = ''
		else:
			password = self.message.text
			self.bot.deleteMessage(self.message.user.chatID, self.message.id)

			if password == self.bot.memes.getPassword(self.message.user.tempParams['enteredCourse']):
				self.message.user.course = self.message.user.tempParams['enteredCourse']
				self.message.user.tempParams['enteredCourse'] = ''

				self.bot.sendMessage(self.message.user.chatID,
									 ("You successfully joined the course " + self.message.user.course))
				self.message.user.expectedMessageType = ''
			else:
				self.bot.sendMessage(self.message.user.chatID,
									 "Wrong password. Please try again. Write 'cancel' to cancel.")
				self.message.user.expectedMessageType = 'coursepassword'

	# Called when a user sends the RaPla link for a newly created course.
	def message_raplalink(self):
		if self.message.text == 'cancel':
			self.message.user.expectedMessageType = ''
			self.bot.sendMessage(self.message.user.chatID, 'Mission aborted, repeating: MISSION ABORTED.')
			logging.warning('User %s, name %s created a new course but didn\'t supply a link!', self.message.user.chatID, self.message.user.name)
		else:
			if self.bot.lectureFetcher.validateLink(self.message.text):
				self.bot.lectureFetcher.addRaplaLink(self.message.user.course, self.message.text)
				self.bot.sendMessage(self.message.user.chatID,
									 "Thank you for sending me the link! ❤️❤️❤️")
				self.message.user.expectedMessageType = ''
			else:
				self.bot.sendMessage(self.message.user.chatID,
									 "Invalid link. Please try again. Write 'cancel' to cancel setup.")
				self.message.user.expectedMessageType = 'raplalink'
