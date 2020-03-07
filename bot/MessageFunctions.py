import telegram_secrets
from menu import MenuSaver as menu
from datetime import datetime, timedelta
from maps import Directions
from menu import Rater


class MessageFunctions:
	def __init__(self, message, bot):
		self.message = message
		self.bot = bot

	def message_unknown(self):
		self.bot.sendMessageWithOptions(self.message.user.chatID,
										'I don\'t know what to do with your input :( Use this to get help:',
										self.bot.generateReplyMarkup([['/help']]))

	def message_name(self):
		self.message.user.name = self.message.text
		welcomeMsg = (
				'Hello, *' + self.message.text + '*! Pleased to meet you! To get you started, I\'ll now explain to '
				+ 'you the stuff I\'m able to do and what commands you may use.\n\n You already figured out the first command, /start. '
				+ 'Great work there!\n\nTo continue, you might want to *subscribe to the daily menu push service* via /subscribemenu '
				+ 'and the *daily lecture plan push* via /subscribelectureplan. Pretty easy to remember, right? If you want to '
				+ 'unsubscribe from these services, you just need to type /unsubscribemenu or /unsubscribelectureplan (You '
				+ 'probably already guessed these).\n\nTo *get the daily menu at any time*, send /getmenu. If you forgot '
				+ '*what lectures you have today*, type /getlectures to get the plan again.\n\n'
				+ 'Also, if you don\'t want to check the crappy DB app every day, type /subscribetraininfo and send the '
				+ 'required Information to *get public transport directions* alongside the lecture push.\n\n'
				+ 'We all love *memes*. Type /getmeme to access all of your favorite ones.\n\n'
				+ 'If you find a *bug*, report it via /reportbug.\n\nAnd because I '
				+ 'respect your *privacy*, type /privacy and /whatdoyouknowaboutme to get Info about what we save '
				+ 'about you. Last but not least, type /help to get a short description of every command.\n\n'
				+ 'If you have any questions, contact @PaddyOfficial on Telegram.')
		self.bot.sendMessage(self.message.user.chatID, welcomeMsg)
		self.message.user.expectedMessageType = ''

	# From /subscribelectureplan
	def message_coursename(self):
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

	# From /subscribelectureplan -> coursename
	def message_coursepassword(self):
		password = self.message.text
		self.bot.deleteMessage(self.message.user.chatID, self.message.id)

		if password == self.bot.memes.getPassword(self.message.user.tempParams['enteredCourse']):
			self.message.user.course = self.message.user.tempParams['enteredCourse']
			self.message.user.tempParams['enteredCourse'] = ''

			if self.bot.lectureFetcher.checkForCourse(self.message.user.course):
				self.message.user.wantsLecturePlan = True
				self.bot.sendMessage(self.message.user.chatID,
									 "You successfully subscribed to the daily lecture plan push."
									 + " May the RaPla be with you! If you also want to receive public transport "
									 + "Information, send /subscribetraininfo")
				self.message.user.expectedMessageType = ''
			else:
				self.bot.sendMessage(self.message.user.chatID, "Unknown course. Please send me the link to your courses"
									 + " iCal calendar:")
				self.message.user.expectedMessageType = "raplalink"
		else:
			self.bot.sendMessage(self.message.user.chatID,
								 "Wrong password. Please start again using /subscribelectureplan")
			self.message.user.expectedMessageType = ''

	# From /subscribelectureplan -> coursename
	def message_newcoursepassword(self):
		password = self.message.text
		self.bot.deleteMessage(self.message.user.chatID, self.message.id)

		self.bot.memes.setPassword(self.message.user.course, password)

		if self.bot.lectureFetcher.checkForCourse(self.message.user.course):
			self.message.user.wantsLecturePlan = True
			self.bot.sendMessage(self.message.user.chatID,
								 "You successfully subscribed to the daily lecture plan push."
								 + " May the RaPla be with you! If you also want to receive public transport "
								 + "Information, send /subscribetraininfo")
			self.message.user.expectedMessageType = ''
		else:
			self.bot.sendMessage(self.message.user.chatID, "Unknown course. Please send me the link to your courses"
								 + " iCal calendar:")
			self.message.user.expectedMessageType = "raplalink"

	# From /getlectures
	def message_changecoursename(self):
		if self.bot.lectureFetcher.firstUserInCourse(self.message.text):
			self.message.user.course = self.message.text
			self.bot.sendMessage(self.message.user.chatID,
								 "You are the first user in this course. Please send me "
								 + "a password that future users have to enter in order to "
								 + "join this course. Write it down somewhere save because "
								 + "I will delete your message after I received it:")
			self.message.user.expectedMessageType = 'changedcoursenewcoursepassword'
			self.bot.lectureFetcher.setUserOfCourse(self.message.user.course)
		else:
			self.message.user.tempParams['enteredCourse'] = self.message.text
			self.bot.sendMessage(self.message.user.chatID, "Please send me the password for " + self.message.text)
			self.message.user.expectedMessageType = 'changedcoursepassword'

	# From /getlectures -> changecoursename
	def message_changedcoursepassword(self):
		password = self.message.text
		self.bot.deleteMessage(self.message.user.chatID, self.message.id)

		if password == self.bot.memes.getPassword(self.message.user.tempParams['enteredCourse']):
			self.message.user.course = self.message.user.tempParams['enteredCourse']
			self.message.user.tempParams['enteredCourse'] = ''

			if self.bot.lectureFetcher.checkForCourse(self.message.user.course):
				self.bot.sendMessage(self.message.user.chatID,
									 'Successfully added/changed course. Here is the plan for today:')
				self.message.text = 'Today'
				self.message_lectureplanday()
				self.message.user.expectedMessageType = ''
			else:
				self.bot.sendMessage(self.message.user.chatID, "Unknown course. Please send me the link to your courses"
									 + " iCal calendar:")
				self.message.user.expectedMessageType = "raplalinkwithoutpush"
		else:
			self.bot.sendMessage(self.message.user.chatID,
								 "Wrong password. Please start again using /getlectures")
			self.message.user.expectedMessageType = ''

	# From /getlectures -> changecoursename
	def message_changedcoursenewcoursepassword(self):
		password = self.message.text
		self.bot.deleteMessage(self.message.user.chatID, self.message.id)

		self.bot.memes.setPassword(self.message.user.course, password)

		if self.bot.lectureFetcher.checkForCourse(self.message.user.course):
			self.bot.sendMessage(self.message.user.chatID,
								 'Successfully added/changed course. Here is the plan for today:')
			self.message.text = 'Today'
			self.message_lectureplanday()
			self.message.user.expectedMessageType = ''
		else:
			self.bot.sendMessage(self.message.user.chatID, "Unknown course. Please send me the link to your courses"
								 + " iCal calendar:")
			self.message.user.expectedMessageType = "raplalinkwithoutpush"

	# From /subscribelectureplan -> coursepassword / newcoursepassword
	def message_raplalink(self):
		if self.message.text == 'stop':
			self.message.user.expectedMessageType = ''
			self.bot.sendMessage(self.message.user.chatID, 'Mission aborted, repeating: MISSION ABORTED.')
		else:
			if self.bot.lectureFetcher.validateLink(self.message.text):
				self.bot.lectureFetcher.addRaplaLink(self.message.user.course, self.message.text)
				self.message.user.wantsLecturePlan = True
				self.bot.sendMessage(self.message.user.chatID,
									 "You successfully subscribed to the daily lecture plan push."
									 + " May the RaPla be with you! If you also want to receive public transport "
									 + "Information, send /subscribetraininfo")
				self.message.user.expectedMessageType = ''
			else:
				self.bot.sendMessage(self.message.user.chatID,
									 "Invalid link. Please try again. Write stop to cancel setup.")
				self.message.user.expectedMessageType = 'raplalink'

	# From /getlectures -> changedcoursepassword / changedcoursenewcoursepassword
	def message_raplalinkwithoutpush(self):
		if self.message.text == 'stop':
			self.message.user.expectedMessageType = ''
			self.bot.sendMessage(self.message.user.chatID, 'Mission aborted, repeating: MISSION ABORTED.')
		else:
			if self.bot.lectureFetcher.validateLink(self.message.text):
				self.bot.lectureFetcher.addRaplaLink(self.message.user.course, self.message.text)
				self.bot.sendMessage(self.message.user.chatID,
									 "Successfully added RaPla link for your course. Here is the plan for today:")
				self.message.text = 'Today'
				self.message_lectureplanday()
				self.message.user.expectedMessageType = ''
			else:
				self.bot.sendMessage(self.message.user.chatID,
									 "Invalid link. Please try again. Write stop to cancel setup.")
				self.message.user.expectedMessageType = 'raplalinkwithoutpush'

	def message_broadcastmessage(self):
		for user in self.bot.users:
			self.bot.sendMessage(user.chatID, self.message.text)

		self.message.user.expectedMessageType = ''

	def message_useraddress(self):
		self.message.user.address = self.message.text
		self.bot.sendMessage(self.message.user.chatID,
							 'Successfully added address. Big Brother is now watching you. 😈')

		self.message.user.expectedMessageType = ''

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

			if self.message.user.address != None and self.message.user.address != '':
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

	def message_bugdescription(self):
		self.bot.log(('Got a bug report:\n\n' + self.message.text))
		self.bot.sendMessage(self.message.user.chatID, "Thanks for reporting this bug. We will fix it ASAP.")
		self.message.user.expectedMessageType = ''
