from menu import MenuSaver as menu
from datetime import datetime
import os
from telegram import ReplyKeyboardMarkup, KeyboardButton, ParseMode
import logging


class CommandFunctions:
	def __init__(self, message, bot, conn):
		self.message = message
		self.bot = bot
		self.conn = conn

	def command_help(self):
		# Provide help list for patrick with full command list and for other users with commands they can use.
		if str(self.message.user.chatID) == os.environ.get('PATRICK_TELEGRAM_ID'):
			self.bot.sendMessage(self.message.user.chatID,
								 "/help\n/stopbot\n/sendmessagetoeveryone\n\n/getmenu\n\n/getlectures\n\n/getdirections\n\n/reportbug\n\n/privacy\n/whatdoyouknowaboutme",
								 reply_markup=ReplyKeyboardMarkup(
									 [[KeyboardButton('/sendmessagetoeveryone')],
									  [KeyboardButton('/help')],
									  [KeyboardButton('/settings')],
									  [KeyboardButton('/getmenu')],
									  [KeyboardButton('/getlectures')],
									  [KeyboardButton('/getdirections')],
									  [KeyboardButton('/reportbug')],
									  [KeyboardButton('/privacy')],
									  [KeyboardButton('/whatdoyouknowaboutme')]], resize_keyboard=True,
									 one_time_keyboard=True))
		else:
			replyString = ('<b>Help</b>: /help\n\n'
						   + '<b>Settings</b>: /settings\n\n'
						   + '<b>Menu</b>: /getmenu\n\n'
						   + '<b>Lecture plan</b>: /getlectures\n\n'
						   + '<b>Public transport</b>: /getdirections\n\n'
						   + '<b>Report a bug</b>: /reportbug\n\n'
						   + '<b>Privacy information</b>: /privacy\n'
						   + 'To get <b>all information</b> we have about you: /whatdoyouknowaboutme\n\n'
						   + 'If you have any questions, contact @P4ddy_m on Telegram.')
			self.bot.sendMessage(self.message.user.chatID, replyString,
								 reply_markup=ReplyKeyboardMarkup(
									 [[KeyboardButton('/help')],
									  [KeyboardButton('/settings')],
									  [KeyboardButton('/getmenu')],
									  [KeyboardButton('/getlectures')],
									  [KeyboardButton('/getdirections')],
									  [KeyboardButton('/reportbug')],
									  [KeyboardButton('/privacy')],
									  [KeyboardButton('/whatdoyouknowaboutme')]], resize_keyboard=True,
									 one_time_keyboard=True),
								 parse_mode=ParseMode.HTML)

	def command_start(self):
		self.bot.sendMessage(self.message.user.chatID, "Please send me your name so we get to know each other")
		self.message.user.expectedMessageType = 'startname'

	def command_privacy(self):
		self.bot.sendMessage(self.message.user.chatID,
							 "We save everything you provide us for you to get the best experience.")

	def command_whatdoyouknowaboutme(self):
		self.bot.sendMessage(self.message.user.chatID, "🤔 I know the following things about you :")
		self.bot.sendMessage(self.message.user.chatID,
							 ("📥 Your Telegram chat id is " + str(self.message.user.chatID)))
		self.bot.sendMessage(self.message.user.chatID, ("🗣 Your name is " + str(self.message.user.name)))
		if self.message.user.address != '' and self.message.user.address is not None:
			self.bot.sendMessage(self.message.user.chatID,
								 ('🚅 The address you entered is ' + self.message.user.address))
		if self.message.user.wantsMenu:
			self.bot.sendMessage(self.message.user.chatID, "✅ You want to receive the daily menu push")
		else:
			self.bot.sendMessage(self.message.user.chatID, "❌ You don't want to receive the daily menu push")

		if self.message.user.wantsLecturePlan:
			self.bot.sendMessage(self.message.user.chatID, "✅ You want to receive the daily lecture plan push")
		else:
			self.bot.sendMessage(self.message.user.chatID,
								 "❌ You don't want to receive the daily lecture plan push")

		if self.message.user.wantsTransportInfo:
			self.bot.sendMessage(self.message.user.chatID, "✅ You want to receive public transport info")
		else:
			self.bot.sendMessage(self.message.user.chatID, "❌ You don't want to receive public transport info")

		if not self.message.user.wantsToRateMeals:
			self.bot.sendMessage(self.message.user.chatID, "❌ You don't want to rate meals")

		if self.message.user.course:
			self.bot.sendMessage(self.message.user.chatID,
								 ("🏫 You are in the " + self.message.user.course + " course"))
		else:
			self.bot.sendMessage(self.message.user.chatID,
								 "❓ But I don't know which course you are in, so I can't send you "
								 + "your lecture plan :(")

	def command_getmenu(self):
		self.bot.sendMessage(self.message.user.chatID, 'For which day do you want the plan?',
							 reply_markup=ReplyKeyboardMarkup([[KeyboardButton('Today'),
																KeyboardButton('Tomorrow')]], resize_keyboard=True,
															  one_time_keyboard=True))

		self.message.user.expectedMessageType = 'menuday'

	def command_getlectures(self):
		# TODO: On fridays, options should be Today / Monday
		isFriday = datetime.now().weekday() == 4
		if self.message.user.course == None or self.message.user.course == '':
			self.bot.sendMessage(self.message.user.chatID,
								 'I don\'t know which course you are in. Please provide me this information under /settings -> Personal Information')
		else:
			if isFriday:
				self.bot.sendMessage(self.message.user.chatID, 'For which day do you want the plan?',
									 reply_markup=ReplyKeyboardMarkup([[KeyboardButton('Today'),
																		KeyboardButton('Monday')]],
																	  resize_keyboard=True,
																	  one_time_keyboard=True))
			else:
				self.bot.sendMessage(self.message.user.chatID, 'For which day do you want the plan?',
									 reply_markup=ReplyKeyboardMarkup([[KeyboardButton('Today'),
																		KeyboardButton('Tomorrow')]],
																	  resize_keyboard=True,
																	  one_time_keyboard=True))

			self.message.user.expectedMessageType = 'lectureplanday'

	def command_sendmessagetoeveryone(self):
		if str(self.message.user.chatID) == os.environ.get('PATRICK_TELEGRAM_ID'):
			self.bot.sendMessage(self.message.user.chatID, "What do you want to broadcast?")
			self.message.user.expectedMessageType = "broadcastmessage"
		else:
			logging.warning(("Wrong user " + str(self.message.user.chatID) + ", entered name " + str(
				self.message.user.name) + " tried to broadcast a message"))
			self.bot.sendMessage(self.message.user.chatID, "You are not allowed to do this.")

	def command_reportbug(self):
		self.bot.sendMessage(self.message.user.chatID, "Please describe the bug:")
		self.message.user.expectedMessageType = 'bugdescription'

	def command_settings(self):
		self.bot.sendMessage(self.message.user.chatID, 'What do you want to change?',
							 reply_markup=ReplyKeyboardMarkup(
								 [[KeyboardButton('️🧍 Personal Information')],
								  [KeyboardButton('📲 Subscription-Settings')],
								  [KeyboardButton('⏰ Push Time Settings')],
								  [KeyboardButton('🧨 Cancel')]], resize_keyboard=True,
								 one_time_keyboard=True))
		self.message.user.expectedMessageType = 'settingstype'

	def command_adminrate(self):
		if str(self.message.user.chatID) == os.environ.get('PATRICK_TELEGRAM_ID'):
			mealArr = menu.Reader(1).get_food_with_ratings_as_string_array()

			mealString = ("Meal 1:\n" + mealArr[0] + "\nMeal 2:\n" + mealArr[1] + "\nMeal 3:\n" + mealArr[2])
			for user in self.bot.users:
				if user.wantsMenu and user.wantsToRateMeals:
					self.bot.sendMessage(user.chatID, (
							"Please rate your meal today. The available meals were:\n\n" + mealString),
										 reply_markup=ReplyKeyboardMarkup(
											 [[KeyboardButton('Meal 1'),
											   KeyboardButton('Meal 2'),
											   KeyboardButton('Meal 3')],
											  [KeyboardButton('Don\'t rate')]], resize_keyboard=True,
											 one_time_keyboard=True))
					user.tempParams['ratingMealset'] = mealArr
					user.expectedMessageType = 'mealtoberated'
		else:
			logging.warning(("Wrong user " + str(self.message.user.chatID) + ", entered name " + str(
				self.message.user.name) + " tried to stop the bot."))
			self.bot.sendMessage(self.message.user.chatID, "You are not allowed to do this.")

	def command_getdirections(self):
		if self.message.user.address is not None and self.message.user.address != '':
			self.bot.sendMessage(self.message.user.chatID, "What directions do you want?",
								 reply_markup=ReplyKeyboardMarkup([[KeyboardButton('-> DHBW')],
																   [KeyboardButton('-> Home')]], resize_keyboard=True,
																  one_time_keyboard=True))
			self.message.user.expectedMessageType = 'directionstype'
		else:
			self.bot.sendMessage(self.message.user.chatID,
								 "I don\'t know your address. Please provide me this with /settings -> Personal Information")
