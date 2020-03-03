import telegram_secrets
from menu import MenuSaver as menu
from datetime import datetime, timedelta
from maps import Directions


class MessageFunctions:
	def __init__(self, message, bot):
		self.message = message
		self.bot = bot

	def message_unknown(self):
		self.bot.sendMessageWithOptions(self.message.user.chatID,
										'I don\'t know what to do with your input :( Use this to get help:',
										self.bot.generateReplyMarkup(['/help']))

	def message_name(self):
		self.message.user.name = self.message.text
		welcomeMsg = ('Hello, ' + self.message.text + '! Pleased to meet you! To get you started, I\'ll now explain to '
					  + 'you the stuff I\'m able to do and what commands may use. You already figured out the first command, /start. '
					  + 'Great work there! To continue, you might want to subscribe to the daily menu push service via /subscribemenu '
					  + 'and the daily lecture plan push via /subscribelectureplan. Pretty easy to remember, right? If you want to '
					  + 'unsubscribe from these services, you just need to type /unsubscribemenu or /unsubscribelectureplan (You '
					  + 'probably already guessed these). To get the daily menu at any time, send /getmenu. If you forgot '
					  + 'what lectures you had today, type /getlectures to get the plan again. And because I '
					  + 'respect your privacy, type /privacy and /whatdoyouknowaboutme to get Info about what we save '
					  + 'about you. Last but not least, type /help to get a short description of every command.')
		self.bot.sendMessage(self.message.user.chatID, welcomeMsg)
		self.message.user.expectedMessageType = ''

	def message_coursename(self):
		self.message.user.course = self.message.text

		if self.bot.lectureFetcher.checkForCourse(self.message.user.course):
			self.message.user.wantsLecturePlan = True
			self.bot.sendMessage(self.message.user.chatID, "You successfully subscribed to the daily lecture plan push."
								 + " May the RaPla be with you! If you also want to receive public transport "
								 + "Information, send /subscribetraininfo")
			self.message.user.expectedMessageType = ''
		else:
			self.bot.sendMessage(self.message.user.chatID, "Unknown course. Please send me the link to your courses"
								 + " iCal calendar:")
			self.message.user.expectedMessageType = "raplalink"

	def message_changecoursename(self):
		self.message.user.course = self.message.text

		if self.bot.lectureFetcher.checkForCourse(self.message.user.course):
			self.bot.sendMessage(self.message.user.chatID,
								 'Successfully added/changed course. Here is the plan for today:')
			now = datetime.now()
			dateString = now.strftime("%Y-%m-%d")
			plan = self.bot.lectureFetcher.getFormattedLectures(self.message.user.course, dateString)
			self.bot.sendMessage(self.message.user.chatID, plan)
			self.message.user.expectedMessageType = ''
		else:
			self.bot.sendMessage(self.message.user.chatID, "Unknown course. Please send me the link to your courses"
								 + " iCal calendar:")
			self.message.user.expectedMessageType = "raplalinkwithoutpush"

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

	def message_raplalinkwithoutpush(self):
		if self.message.text == 'stop':
			self.message.user.expectedMessageType = ''
			self.bot.sendMessage(self.message.user.chatID, 'Mission aborted, repeating: MISSION ABORTED.')
		else:
			if self.bot.lectureFetcher.validateLink(self.message.text):
				self.bot.lectureFetcher.addRaplaLink(self.message.user.course, self.message.text)
				self.bot.sendMessage(self.message.user.chatID,
									 "Successfully added RaPla link for your course. Here is the plan for today:")
				now = datetime.now()
				dateString = now.strftime("%Y-%m-%d")
				plan = self.bot.lectureFetcher.getFormattedLectures(self.message.user.course, dateString)
				self.bot.sendMessage(self.message.user.chatID, plan)
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
			fetchedMenu = menu.Reader(day+1).get_menu_as_arr() # day+1 because 1 is today, 2 is tomorrow...
			self.bot.sendMessage(self.message.user.chatID, "Here you go: ")
			for oneMenu in fetchedMenu:
				self.bot.sendMessage(self.message.user.chatID, oneMenu)
		else:
			self.bot.sendMessage(self.message.user.chatID, "The canteen is closed there. Hence no menu for you.")
