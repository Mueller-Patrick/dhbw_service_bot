from menu import MenuSaver as menu
from datetime import datetime, timedelta
from maps import Directions
from menu import Rater
import logging
import re
import os
import bot.User as usr
from telegram import ReplyKeyboardMarkup, KeyboardButton, ParseMode
import logging
from lecturePlan.LectureFetcher import LectureFetcher


class MessageFunctions:
	def __init__(self, message, bot, conn):
		self.message = message
		self.bot = bot
		self.conn = conn

	def message_unknown(self):
		"""
		Called when user sends a normal message but we don't expect any input
		"""
		self.bot.sendMessage(self.message.user.chatID,
							 'I don\'t know what to do with your input :( Use /help to get help:',
							 reply_markup=ReplyKeyboardMarkup([[KeyboardButton('/help')]], resize_keyboard=True,
															  one_time_keyboard=True))

	def message_startname(self):
		"""
		Called when user registers for the first time and sends his name
		"""
		self.message.user.name = self.message.text
		welcomeMsg = (
				'Hello, <b>' + self.message.text + '</b>! Pleased to meet you! To get you started, I\'ll now explain to '
				+ 'you the stuff I\'m able to do and what commands you may use.\n\n'
				+ 'To <b>set everything up</b>, use the /settings command. Under \'Personal Information\' you can add or '
				+ 'change the Information that I need about you to provide my services to you. Under \'Subscription-Settings\' '
				+ 'you can set up which push-messages you want to get from me.\n\n'
				+ 'My Push-Service includes lecture plan pushes, daily menu pushes and public transport information for '
				+ 'each day. If you receive the menu push, I\'ll also ask you to <b>rate your meal</b>. If you don\'t '
				+ 'want that, you can opt-out in the subscription settings. To <b>pause all notifications</b> for example '
				+ 'while you are in your practical phase, use /settings -> Subscription-Settings.\n\n'
				+ 'To <b>get the daily menu at any time</b>, send /getmenu. If you forgot '
				+ '<b>what lectures you have today</b>, type /getlectures to get the plan again. And if you want the <b>public '
				+ 'transport directions</b> now, type /getdirections.\n\n'
				+ 'If you find a <b>bug</b>, report it via /reportbug.\n\nAnd because I '
				+ 'respect your <b>privacy</b>, type /privacy and /whatdoyouknowaboutme to get Info about what we save '
				+ 'about you. Last but not least, type /help to get a list of available commands.\n\n'
				+ 'If you have any questions, contact @P4ddy_m on Telegram.')
		self.bot.sendMessage(self.message.user.chatID, welcomeMsg, parse_mode=ParseMode.HTML)
		self.message.user.expectedMessageType = ''

	def message_broadcastmessage(self):
		"""
		Called when Patrick wants to broadcast something
		"""
		users = []
		cur = self.conn.cursor()
		getAllUsersString = """SELECT chatID FROM users"""
		cur.execute(getAllUsersString)
		userRows = cur.fetchall()
		self.conn.commit()

		for user in userRows:
			self.bot.sendMessage(user[0], self.message.text)

		cur.close()

		self.message.user.expectedMessageType = ''

	def message_lectureplanday(self):
		"""
		Called when user sends the day he wants the lecture plan for
		"""
		if self.message.text == 'Today':
			day = 0
		elif self.message.text == 'Tomorrow':
			day = 1
		elif self.message.text == 'Monday':
			day = 3
		else:
			self.bot.sendMessage(self.message.user.chatID, "Wrong input. Please try again.")
			return

		forDay = datetime.now() + timedelta(days=day)
		dateString = forDay.strftime("%Y-%m-%d")
		lf = LectureFetcher(self.conn)
		plan = lf.getFormattedLectures(self.message.user.course, dateString)
		firstLectureTime = lf.getFirstLectureTime(self.message.user.course, dateString)
		print(('First lecture time for {}: {}').format(dateString, firstLectureTime))

		if not plan:
			self.bot.sendMessage(self.message.user.chatID, 'No more lectures for that day.')
		else:
			self.bot.sendMessage(self.message.user.chatID, plan, parse_mode=ParseMode.HTML)

		# Not available due to missing google maps API key
		# if self.message.user.wantsTransportInfo and self.message.user.address is not None and self.message.user.address != '':
		# 	time = datetime(int(forDay.year), int(forDay.month), int(forDay.day),
		# 					int(firstLectureTime[:2]), int(firstLectureTime[3:]))
		#
		# 	if time < datetime.now():
		# 		self.bot.sendMessage(self.message.user.chatID,
		# 							 ('Your first lecture already began, so I suppose you '
		# 							  + 'are at the DHBW already and don\'t need the public transport Info.'))
		# 	else:
		# 		try:
		# 			direc = Directions.Direction(time, self.message.user.address)
		# 			trainPlan = direc.create_message()
		#
		# 			self.bot.sendMessage(self.message.user.chatID, 'Here are the public transport directions:')
		# 			self.bot.sendMessage(self.message.user.chatID, trainPlan, parse_mode=ParseMode.HTML)
		# 		except IndexError:
		# 			self.bot.sendMessage(self.message.user.chatID, (
		# 					'Could not fetch public transport directions for your address '
		# 					+ self.message.user.address))
		# 			logging.warning('In MessageFunctions(): Fetching directions for address %s not successful.',
		# 							self.message.user.address)

		self.message.user.expectedMessageType = ''

	def message_menuday(self):
		"""
		Called when user sends the day he wants the menu for
		"""
		if self.message.text == 'Today':
			day = 0
		elif self.message.text == 'Tomorrow':
			day = 1
		else:
			day = 0

		# Try-except to catch any errors during menu fetching and not cause the bug to crash
		try:
			# If it's sunday and the user requests the menu for monday, inform him that the menu for next week can not be fetched yet.
			if datetime.now().weekday() == 6 and day == 1:
				self.bot.sendMessage(self.message.user.chatID,
									 "The menu for next week is not yet available, check back tomorrow.")
			else:
				forDay = datetime.now() + timedelta(days=day)
				weekday = forDay.weekday()
				if weekday < 5:  # Because monday is 0...
					fetchedMenu = menu.Reader(self.conn,
											  day + 1).get_menu_as_arr()  # day+1 because 1 is today, 2 is tomorrow...
					self.bot.sendMessage(self.message.user.chatID, "Here you go: ")
					for oneMenu in fetchedMenu:
						self.bot.sendMessage(self.message.user.chatID, oneMenu)
				else:
					self.bot.sendMessage(self.message.user.chatID,
										 "The canteen is closed there. Hence no menu for you.")
		except:
			self.bot.sendMessage(self.message.user.chatID,
								 "There was an error during the fetching process. Please try again later.")

		self.message.user.expectedMessageType = ''

	def message_mealtoberated(self):
		"""
		Called when user sends the meal that he wants to rate
		"""
		mealToBeRated = self.message.text

		if mealToBeRated == 'Don\'t rate':
			self.bot.sendMessage(self.message.user.chatID, "Ok, no rating. This is fine.")
			self.message.user.tempParams['ratingMealset'] = ''
			self.message.user.expectedMessageType = ''
		else:
			if mealToBeRated in ('Meal 1', 'Meal 2', 'Meal 3'):
				self.message.user.tempParams['ratedMeal'] = mealToBeRated
				self.bot.sendMessage(self.message.user.chatID, "How many stars do you give?",
									 reply_markup=ReplyKeyboardMarkup(
										 [[KeyboardButton('0 ⭐'),
										   KeyboardButton('1 ⭐'),
										   KeyboardButton('2 ⭐'),
										   KeyboardButton('3 ⭐'),
										   KeyboardButton('4 ⭐'),
										   KeyboardButton('5 ⭐')]], resize_keyboard=True,
										 one_time_keyboard=True))
				self.message.user.expectedMessageType = 'mealrating'
			else:
				self.bot.sendMessage(self.message.user.chatID, "Wrong input. Try again",
									 reply_markup=ReplyKeyboardMarkup(
										 [[KeyboardButton('Meal 1'),
										   KeyboardButton('Meal 2'),
										   KeyboardButton('Meal 3')],
										  [KeyboardButton('Don\'t rate')]], resize_keyboard=True,
										 one_time_keyboard=True))

	def message_mealrating(self):
		"""
		Called when user sends the rating for his meal
		"""
		rating = self.message.text
		mealArr = self.message.user.tempParams['ratingMealset']

		rating = int(rating[:1])

		if rating in (0, 1, 2, 3, 4, 5):
			ratedMeal = mealArr[int(self.message.user.tempParams['ratedMeal'][5]) - 1]
			Rater.Rater(ratedMeal, rating)
			self.bot.sendMessage(self.message.user.chatID, "Thank you for rating! 😁")
			self.message.user.tempParams['ratingMealset'] = ''
			self.message.user.tempParams['ratedMeal'] = ''
			self.message.user.expectedMessageType = ''
		else:
			self.bot.sendMessage(self.message.user.chatID, "Wrong input. Try again.",
								 reply_markup=ReplyKeyboardMarkup(
									 [[KeyboardButton('0 ⭐'),
									   KeyboardButton('1 ⭐'),
									   KeyboardButton('2 ⭐'),
									   KeyboardButton('3 ⭐'),
									   KeyboardButton('4 ⭐'),
									   KeyboardButton('5 ⭐')]], resize_keyboard=True,
									 one_time_keyboard=True))

	def message_bugdescription(self):
		"""
		Called when user sends the description of a bug he encountered
		"""
		logging.warning(('Got a bug report by ' + self.message.user.name + ':\n\n' + self.message.text))
		self.bot.sendMessage(os.environ['PATRICK_TELEGRAM_ID'],
							 ('Got a bug report by ' + self.message.user.name + ':\n\n' + self.message.text))
		self.bot.sendMessage(self.message.user.chatID, "Thanks for reporting this bug. We will fix it ASAP.")
		self.message.user.expectedMessageType = ''

	def message_directionstype(self):
		"""
		@deprecated
		"""
		if self.message.text == '-> DHBW':
			try:
				direc = Directions.Direction(datetime.now(), self.message.user.address, False, True)
				trainPlan = direc.create_message()

				self.bot.sendMessage(self.message.user.chatID,
									 'Here are the public transport directions for your way to DHBW:')
				self.bot.sendMessage(self.message.user.chatID, trainPlan, parse_mode=ParseMode.HTML)
			except:
				self.bot.sendMessage(self.message.user.chatID, (
						'Could not fetch public transport directions for your address '
						+ self.message.user.address))
				logging.warning('In HelperFunctions(): Fetching directions for address %s not successful.',
								self.message.user.address)
			self.message.user.expectedMessageType = ''
		elif self.message.text == '-> Home':
			try:
				direc = Directions.Direction(datetime.now(), self.message.user.address, True, True)
				trainPlan = direc.create_message()

				self.bot.sendMessage(self.message.user.chatID,
									 'Here are the public transport directions for your way home:')
				self.bot.sendMessage(self.message.user.chatID, trainPlan, parse_mode=ParseMode.HTML)
			except:
				self.bot.sendMessage(self.message.user.chatID, (
						'Could not fetch public transport directions for your address '
						+ self.message.user.address))
				logging.warning('In HelperFunctions(): Fetching directions for address %s not successful.',
								self.message.user.address)
			self.message.user.expectedMessageType = ''
		else:
			self.bot.sendMessage(self.message.user.chatID, "Wrong input. Please try again:",
								 reply_markup=ReplyKeyboardMarkup([[KeyboardButton('-> DHBW')],
																   [KeyboardButton('-> Home')]],
																  resize_keyboard=True,
																  one_time_keyboard=True))

	def message_settingstype(self):
		"""
		Called when user sends the type of settings he wants to change
		"""
		if self.message.text == '️🧍 Personal Information':
			self.bot.sendMessage(self.message.user.chatID,
								 "Here are the Information about you that you can change:",
								 reply_markup=ReplyKeyboardMarkup(
									 [[KeyboardButton('🗣 Name')],
									  [KeyboardButton('🚅 Address')],
									  [KeyboardButton('🏫 Course')],
									  [KeyboardButton('⏪ Back')]], resize_keyboard=True,
									 one_time_keyboard=True))
			self.message.user.expectedMessageType = 'settingspersonalinfo'
		elif self.message.text == '📲 Subscription-Settings':
			# Fetch the user's subscriptions to show them the current status
			options = []
			if self.message.user.pauseAllNotifications:
				options.append([KeyboardButton('🔔 Unpause all Push Notifications')])
			else:
				options.append([KeyboardButton('🔕 Pause all Push Notifications')])

			if self.message.user.wantsMenu:
				options.append([KeyboardButton('❌ Unsubscribe the Menu Push')])
			else:
				options.append([KeyboardButton('✅ Subscribe the Menu Push')])

			if self.message.user.wantsLecturePlan:
				options.append([KeyboardButton('❌ Unsubscribe the Lecture Plan Push')])
			else:
				options.append([KeyboardButton('✅ Subscribe the Lecture Plan Push')])

			if self.message.user.wantsTransportInfo:
				options.append([KeyboardButton('❌ Unsubscribe the Public Transport Info')])
			else:
				options.append([KeyboardButton('✅ Subscribe the Public Transport Info')])

			if self.message.user.wantsToRateMeals:
				options.append([KeyboardButton('❌ Opt-out of the Meal Rating')])
			else:
				options.append([KeyboardButton('✅ Opt-in to the Meal Rating')])

			options.append([KeyboardButton('⏪ Back')])

			self.bot.sendMessage(self.message.user.chatID,
								 "Here are your Subscriptions:",
								 reply_markup=ReplyKeyboardMarkup(options, resize_keyboard=True,
																  one_time_keyboard=True))
			self.message.user.expectedMessageType = 'settingssubscriptions'
		elif self.message.text == '⏰ Push Time Settings':
			menuPushTime = self.message.user.pushTimes['menu']
			lecturePushTime = self.message.user.pushTimes['lecture']
			self.bot.sendMessage(self.message.user.chatID,
								 "What push notification should come on another time? ",
								 reply_markup=ReplyKeyboardMarkup(
									 [[KeyboardButton(('🍜 Menu Push (currently ' + menuPushTime + ')'))],
									  [KeyboardButton(
										  ('🕒 Lecture Plan Push (currently ' + lecturePushTime + ')'))],
									  [KeyboardButton('⏪ Back')]], resize_keyboard=True,
									 one_time_keyboard=True))
			self.message.user.expectedMessageType = 'settingstimes'
		elif self.message.text == '🧨 Cancel':
			self.bot.sendMessage(self.message.user.chatID, "ALLES BLEIBT HIER WIE ES IST.")
			self.message.user.expectedMessageType = ''
		else:
			self.bot.sendMessage(self.message.user.chatID, "Wrong input. Please try again:",
								 reply_markup=ReplyKeyboardMarkup(
									 [[KeyboardButton('️🧍 Personal Information')],
									  [KeyboardButton('📲 Subscription-Settings')],
									  [KeyboardButton('⏰ Push Time Settings')],
									  [KeyboardButton('🧨 Cancel')]], resize_keyboard=True,
									 one_time_keyboard=True))

	def message_settingspersonalinfo(self):
		"""
		Called when user sends the information that he wants to change his personal info
		"""
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
									  + "the master, I guess... Go on then, what's your new course? (Please use the format "
									  + "TINF19B4)"))
			else:
				self.bot.sendMessage(self.message.user.chatID,
									 ("Please send me your course name (Please use the format TINF19B4):"))
			self.message.user.expectedMessageType = 'changepersonalinfo'
			self.message.user.tempParams['personalInfoToBeChanged'] = 'course'
		elif self.message.text == '⏪ Back':
			self.bot.sendMessage(self.message.user.chatID, 'What do you want to change?',
								 reply_markup=ReplyKeyboardMarkup(
									 [[KeyboardButton('️🧍 Personal Information')],
									  [KeyboardButton('📲 Subscription-Settings')],
									  [KeyboardButton('⏰ Push Time Settings')],
									  [KeyboardButton('🧨 Cancel')]], resize_keyboard=True,
									 one_time_keyboard=True))
			self.message.user.expectedMessageType = 'settingstype'
		else:
			self.bot.sendMessage(self.message.user.chatID, "Wrong input. Please try again:",
								 reply_markup=ReplyKeyboardMarkup(
									 [[KeyboardButton('🗣 Name')],
									  [KeyboardButton('🚅 Address')],
									  [KeyboardButton('🏫 Course')],
									  [KeyboardButton('⏪ Back')]], resize_keyboard=True,
									 one_time_keyboard=True))

	def message_settingssubscriptions(self):
		"""
		Called when user sends the information that he wants to change his subscription settings
		"""
		if self.message.text == '🔔 Unpause all Push Notifications':
			self.message.user.pauseAllNotifications = False
			self.bot.sendMessage(self.message.user.chatID, "Unpaused the Push Notifications. Just for you.")
			self.message.user.expectedMessageType = ''
		elif self.message.text == '🔕 Pause all Push Notifications':
			self.message.user.pauseAllNotifications = True
			self.bot.sendMessage(self.message.user.chatID, "Paused all Push Notifications. Just for you.")
			self.message.user.expectedMessageType = ''
		elif self.message.text == '❌ Unsubscribe the Menu Push':
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
				self.bot.sendMessage(self.message.user.chatID,
									 ("‼️ You have not entered your course yet. "
									  + "Please do that via /settings -> Personal Information."),
									 reply_markup=ReplyKeyboardMarkup([[KeyboardButton('/settings')]],
																	  resize_keyboard=True,
																	  one_time_keyboard=True))
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
				self.bot.sendMessage(self.message.user.chatID,
									 ("‼️ You have not entered your address yet. "
									  + "Please do that via /settings -> Personal Information"),
									 reply_markup=ReplyKeyboardMarkup([[KeyboardButton('/settings')]],
																	  resize_keyboard=True,
																	  one_time_keyboard=True))
			self.message.user.expectedMessageType = ''
		elif self.message.text == '❌ Opt-out of the Meal Rating':
			self.message.user.wantsToRateMeals = False
			self.bot.sendMessage(self.message.user.chatID, "💔 Opted you out of the meal rating system")
			self.message.user.expectedMessageType = ''
		elif self.message.text == '✅ Opt-in to the Meal Rating':
			self.message.user.wantsToRateMeals = True
			self.bot.sendMessage(self.message.user.chatID, "❤️ Opted you in to the meal rating system")
			self.message.user.expectedMessageType = ''
		elif self.message.text == '⏪ Back':
			self.bot.sendMessage(self.message.user.chatID, 'What do you want to change?',
								 reply_markup=ReplyKeyboardMarkup([[KeyboardButton('️🧍 Personal Information')],
																   [KeyboardButton('📲 Subscription-Settings')],
																   [KeyboardButton('⏰ Push Time Settings')],
																   [KeyboardButton('🧨 Cancel')]],
																  resize_keyboard=True,
																  one_time_keyboard=True))
			self.message.user.expectedMessageType = 'settingstype'
		else:
			# Fetch the user's subscriptions to show them the current status
			options = []
			if self.message.user.pauseAllNotifications:
				options.append([KeyboardButton('🔔 Unpause all Push Notifications')])
			else:
				options.append([KeyboardButton('🔕 Pause all Push Notifications')])

			if self.message.user.wantsMenu:
				options.append([KeyboardButton('❌ Unsubscribe the Menu Push')])
			else:
				options.append([KeyboardButton('✅ Subscribe the Menu Push')])

			if self.message.user.wantsLecturePlan:
				options.append([KeyboardButton('❌ Unsubscribe the Lecture Plan Push')])
			else:
				options.append([KeyboardButton('✅ Subscribe the Lecture Plan Push')])

			if self.message.user.wantsTransportInfo:
				options.append([KeyboardButton('❌ Unsubscribe the Public Transport Info')])
			else:
				options.append([KeyboardButton('✅ Subscribe the Public Transport Info')])

			if self.message.user.wantsToRateMeals:
				options.append([KeyboardButton('❌ Opt-out of the Meal Rating')])
			else:
				options.append([KeyboardButton('✅ Opt-in to the Meal Rating')])

			options.append([KeyboardButton('⏪ Back')])

			self.bot.sendMessage(self.message.user.chatID,
								 "Wrong input. Please try again:",
								 reply_markup=ReplyKeyboardMarkup(options, resize_keyboard=True,
																  one_time_keyboard=True))

	def message_settingstimes(self):
		"""
		Called when the user sends the information which push time he wants to change
		"""
		if '🍜 Menu Push' in self.message.text:
			menuPushTime = self.message.user.pushTimes['menu']
			self.bot.sendMessage(self.message.user.chatID, (
					"You currently receive the menu push at " + menuPushTime
					+ ". To change that, send me the new time in the format <b>HH:MM</b>. Please notice that it has to be "
					+ "a quarter of an hour, e.g. 10:15 and that the push is always for the <b>current</b> day."),
								 parse_mode=ParseMode.HTML)
			self.message.user.tempParams['pushtimeToBeChanged'] = 'menu'
			self.message.user.expectedMessageType = 'changepushtime'
		elif '🕒 Lecture Plan Push' in self.message.text:
			lecturePushTime = self.message.user.pushTimes['lecture']
			self.bot.sendMessage(self.message.user.chatID, (
					"You currently receive the lecture push at " + lecturePushTime
					+ ". To change that, send me the new time in the format <b>HH:MM</b>. Please notice that it has to be "
					+ "a quarter of an hour, e.g. 17:15 and that the push is always for the <b>next</b> day."),
								 parse_mode=ParseMode.HTML)
			self.message.user.tempParams['pushtimeToBeChanged'] = 'lecture'
			self.message.user.expectedMessageType = 'changepushtime'
		elif '⏪ Back' in self.message.text:
			self.bot.sendMessage(self.message.user.chatID, 'What do you want to change?',
								 reply_markup=ReplyKeyboardMarkup([[KeyboardButton('️🧍 Personal Information')],
																   [KeyboardButton('📲 Subscription-Settings')],
																   [KeyboardButton('⏰ Push Time Settings')],
																   [KeyboardButton('🧨 Cancel')]],
																  resize_keyboard=True,
																  one_time_keyboard=True))
			self.message.user.expectedMessageType = 'settingstype'
		else:
			menuPushTime = self.message.user.pushTimes['menu']
			lecturePushTime = self.message.user.pushTimes['lecture']
			self.bot.sendMessage(self.message.user.chatID,
								 "What push notification should come on another time? ",
								 reply_markup=ReplyKeyboardMarkup(
									 [[KeyboardButton(('🍜 Menu Push (currently ' + menuPushTime + ')'))],
									  [KeyboardButton(
										  ('🕒 Lecture Plan Push (currently ' + lecturePushTime + ')'))],
									  [KeyboardButton('⏪ Back')]], resize_keyboard=True,
									 one_time_keyboard=True))

	def message_changepersonalinfo(self):
		"""
		Called when the user sends the new info about him
		"""
		type = self.message.user.tempParams['personalInfoToBeChanged']

		if type == 'name':
			if self.message.user.name == self.message.text:
				self.bot.sendMessage(self.message.user.chatID, "That\'s the name I already know")
				self.message.user.expectedMessageType = ''
				self.message.user.tempParams['personalInfoToBeChanged'] = ''
			else:
				self.message.user.name = self.message.text
				self.bot.sendMessage(self.message.user.chatID,
									 ("Successfully changed your name to " + self.message.text))
				self.message.user.expectedMessageType = ''
				self.message.user.tempParams['personalInfoToBeChanged'] = ''
		elif type == 'address':
			if self.message.user.address == self.message.text:
				self.bot.sendMessage(self.message.user.chatID, "That\'s the address I already know")
				self.message.user.expectedMessageType = ''
				self.message.user.tempParams['personalInfoToBeChanged'] = ''
			else:
				self.message.user.address = self.message.text
				self.bot.sendMessage(self.message.user.chatID,
									 ("Successfully changed your address to " + self.message.text))
				self.message.user.expectedMessageType = ''
				self.message.user.tempParams['personalInfoToBeChanged'] = ''
		elif type == 'course':
			if self.message.user.course == self.message.text.upper():
				self.bot.sendMessage(self.message.user.chatID, "That\'s the course I already know")
				self.message.user.expectedMessageType = ''
				self.message.user.tempParams['personalInfoToBeChanged'] = ''
			else:
				self.message.user.course = self.message.text.upper()
				self.bot.sendMessage(self.message.user.chatID,
									 ("Added you to the {} course!").format(self.message.text.upper()))
				# Check if the course already exists. If not, add it to SQL
				lf = LectureFetcher(self.conn)
				if not lf.courseExists(self.message.text):
					lf.setUserOfCourse(self.message.user.course)
					self.bot.sendMessage(self.message.user.chatID,
										 "I don't know the RaPla link for this course yet. Please be so kind and supply me"
										 + " with the link for your course ❤️")
					self.message.user.expectedMessageType = 'raplalink'
				else:
					lf.setUserOfCourse(self.message.user.course)
					self.message.user.expectedMessageType = ''
		else:
			logging.warning(
				'Wrong type for changing personal info given in MessageFunctions.message_changepersonalinfo. Given type: %s',
				type)

	def message_changepushtime(self):
		"""
		Called when the user sends the new push time
		"""
		type = self.message.user.tempParams['pushtimeToBeChanged']

		if type == 'menu':
			# Possible values: Quarter hours
			timeRegex = re.compile('[0-1][0-9]:(00|15|30|45)')
			timeObj = timeRegex.search(self.message.text)

			# A regex valid time is found
			if timeObj is not None:
				timeString = timeObj.group()
				# Is a valid time
				if int(timeString[:2]) <= 24:
					self.message.user.pushTimes['menu'] = timeString
					self.bot.sendMessage(self.message.user.chatID,
										 ("Successfully updated your menu push time to " + timeString))
					self.message.user.tempParams['pushtimeToBeChanged'] = ''
					self.message.user.expectedMessageType = ''
				else:
					self.bot.sendMessage(self.message.user.chatID, (
							"Invalid time: " + self.message.text
							+ ". Please use the format HH:MM and notice that it has to be a quarter of an hour, e.g. 10:15"))
			else:
				self.bot.sendMessage(self.message.user.chatID, (
						"Invalid time: " + self.message.text
						+ ". Please use the format HH:MM and notice that it has to be a quarter of an hour, e.g. 10:15"))
		elif type == 'lecture':
			# Possible values: Quarter hours
			timeRegex = re.compile('[0-2][0-9]:(00|15|30|45)')
			timeObj = timeRegex.search(self.message.text)

			# A regex valid time is found
			if timeObj is not None:
				timeString = timeObj.group()
				# Is a valid time
				if int(timeString[:2]) <= 24:
					self.message.user.pushTimes['lecture'] = timeString
					self.bot.sendMessage(self.message.user.chatID,
										 ("Successfully updated your lecture push time to " + timeString))
					self.message.user.tempParams['pushtimeToBeChanged'] = ''
					self.message.user.expectedMessageType = ''
				else:
					self.bot.sendMessage(self.message.user.chatID, (
							"Invalid time: " + self.message.text
							+ ". Please use the format HH:MM and notice that it has to be a quarter of an hour, e.g. 17:15"))
			else:
				self.bot.sendMessage(self.message.user.chatID, (
						"Invalid time: " + self.message.text
						+ ". Please use the format HH:MM and notice that it has to be a quarter of an hour, e.g. 17:15"))
		else:
			logging.warning(
				'Wrong type for changing push time given in MessageFunctions.message_changepushtime. Given type: %s',
				type)

	def message_raplalink(self):
		"""
		Called when a user sends the RaPla link for a newly created course.
		"""
		if self.message.text == 'cancel':
			self.message.user.expectedMessageType = ''
			self.bot.sendMessage(self.message.user.chatID, 'Mission aborted, repeating: MISSION ABORTED.')
			logging.warning('User %s, name %s created a new course but didn\'t supply a link!',
							self.message.user.chatID, self.message.user.name)
		else:
			lf = LectureFetcher(self.conn)

			if lf.validateLink(self.message.text):
				lf.addRaplaLink(self.message.user.course, self.message.text)
				self.bot.sendMessage(self.message.user.chatID,
									 "Thank you for sending me the link! ❤️❤️❤️")
				self.message.user.expectedMessageType = ''
			else:
				self.bot.sendMessage(self.message.user.chatID,
									 "Invalid link. Please try again. Write 'cancel' to cancel setup.")
				self.message.user.expectedMessageType = 'raplalink'

	def message_wantstounpausepush(self):
		"""
		Called when the user sends an answer whether or not he wants to unpause the push notifications
		"""
		if self.message.text == 'Yes':
			self.message.user.pauseAllNotifications = False
			self.bot.sendMessage(self.message.user.chatID, "Unpaused your push notifications. Have a good start!")
			self.message.user.expectedMessageType = ''
		elif self.message.text == 'No':
			self.bot.sendMessage(self.message.user.chatID,
								 ("Ok, you still don\'t want any messages from me. If I can "
								  + "do anything better, please tell me via /reportbug."))
			self.message.user.expectedMessageType = ''
		else:
			self.bot.sendMessage(self.message.user.chatID, "Wrong input. Please try again: ",
								 reply_markup=ReplyKeyboardMarkup([[KeyboardButton('Yes'),
																	KeyboardButton('No')]], resize_keyboard=True,
																  one_time_keyboard=True))
