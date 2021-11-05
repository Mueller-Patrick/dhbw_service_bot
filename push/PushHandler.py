import telegram
from telegram import ParseMode
from telegram import ReplyKeyboardMarkup
from telegram import KeyboardButton
import os
import logging
from datetime import datetime, timedelta

from menu2 import MenuUtilities, WebCrawler
import sql.SQLConnectionHandler as sqlhandler
from lecturePlan.LectureFetcher import LectureFetcher
import menu.MenuSaver as menu
import sys
import ast
import traceback


# from maps import Directions


def configure_telegram():
	"""
	Configures the bot with a Telegram Token.

	Returns a bot instance.
	"""

	TELEGRAM_TOKEN = os.environ['DHBW_TELEGRAM_TOKEN']
	if not TELEGRAM_TOKEN:
		logging.error('The TELEGRAM_TOKEN must be set')
		raise NotImplementedError

	return telegram.Bot(TELEGRAM_TOKEN)


def sendPushes():
	"""
	Sends all push notifications that are to be sent at the current time
	"""
	bot = configure_telegram()
	logging.info('Running push check and sending now')
	current_time_minutes = str(datetime.now())[11:16]

	conn = sqlhandler.getvServerConnection()

	fetch_latest_dishes(conn, current_time_minutes)

	# Directions not supported currently due to shutdown of google maps API key
	# sendReturnDirections(conn, bot, current_time_minutes)

	sendMenuPushes(conn, bot, current_time_minutes)
	sendMenuRatingPushes(conn, bot, current_time_minutes)
	sendLecturePushes(conn, bot, current_time_minutes)
	sendExamWarningPushes(conn, bot, current_time_minutes)
	sendUnpauseNotificationsPushes(conn, bot, current_time_minutes)

	conn.close()


def fetch_latest_dishes(conn, current_time_minutes):
	"""
	Fetches and saves the dishes for the next days
	@param conn: The pymysql connection
	"""
	if current_time_minutes == '00:15':
		try:
			date = datetime.now() + timedelta(days=7)
			dishes = WebCrawler.get_dishes(date.strftime('%Y-%m-%d'))
			MenuUtilities.save_dishes_to_sql(conn, dishes)
		except:
			pass


def sendMenuPushes(conn, bot, current_time_minutes):
	"""
	Sends the menu pushes
	@param conn: The SQL connection
	@param bot: The bot instance
	@param current_time_minutes: The current time
	"""
	# For the same day
	# Normally at 06:00 but customizable
	cur = conn.cursor()
	get_users_sql = """SELECT chatID, name FROM users WHERE menuPushTime = %s AND wantsMenu = true AND pauseAllNotifications = false"""
	cur.execute(get_users_sql, (current_time_minutes,))
	users = cur.fetchall()
	cur.close()

	if len(users) > 0:
		# Try-catch so we don't send anything if not menu has been fetched
		try:
			today_date = datetime.now().strftime('%Y-%m-%d')
			fetchedMenu = MenuUtilities.get_formatted_dishes(conn, '2012-10-04')

			# Send the push for the users
			for user in users:
				try:
					chatID = user[0]
					name = user[1]
					bot.sendMessage(chatID,
									"Good morning {}, here is the menu for today:".format(name))
					bot.sendMessage(chatID, fetchedMenu, parse_mode=ParseMode.HTML)
				except telegram.error.Unauthorized:
					continue
		except:
			exc_type, exc_value, exc_traceback = sys.exc_info()
			stack = traceback.extract_tb(exc_traceback)
			logging.warning("Could not fetch menu for today. Error: %s, Stacktrace: %s", sys.exc_info(), stack)


def sendReturnDirections(conn, bot, current_time_minutes):
	"""
	Sends the return direction pushes
	@param conn: The SQL connection
	@param bot: The bot instance
	@param current_time_minutes: The current time
	"""
	# For the same day
	# At 10:00
	if current_time_minutes == '10:00':
		pass


# Condition: wantsTransportInfo, !pauseAllNotifications


def sendMenuRatingPushes(conn, bot, current_time_minutes):
	"""
	Sends the menu rating pushes
	@param conn: The SQL connection
	@param bot: The bot instance
	@param current_time_minutes: The current time
	"""
	# For the same day
	# At 14:30
	if current_time_minutes == '14:30':
		today_date = datetime.now().strftime('%Y-%m-%d')
		dishes = MenuUtilities.get_dishes_from_sql_by_date(conn, today_date)

		# So days when the canteen is closed are skipped
		if len(dishes) < 1:
			return

		menu = MenuUtilities.get_formatted_dishes(conn, today_date, dishes)
		users_query = 'SELECT userID, chatID, name, expectedMsgType, tempParams FROM users WHERE wantsToRateMeals = 1 AND pauseAllNotifications = 0'
		cur = conn.cursor()
		cur.execute(users_query)
		users = cur.fetchall()

		update_users = []

		for user in users:
			user_id = user[0]
			chat_id = user[1]
			name = user[2]
			expected_type = user[3]
			temp_params = ast.literal_eval(user[4])

			expected_type = 'meal_category'

			temp_params['ratingMealset'] = {}

			for categ_dishes in dishes.values():
				for dish in categ_dishes:
					temp_params['ratingMealset'][dish.name] = {
						'dish_id': dish.dish_id,
						'category': dish.category
					}

			reply_buttons = []
			for categ in dishes.keys():
				reply_buttons.append(KeyboardButton(categ))

			bot.sendMessage(chat_id, "Please rate your meal today. The available meals were:\n\n" + menu,
							parse_mode=ParseMode.HTML,
							reply_markup=ReplyKeyboardMarkup([reply_buttons,
															  [KeyboardButton('Don\'t rate')]], resize_keyboard=True,
															 one_time_keyboard=True))

			update_users.append((expected_type, str(temp_params), user_id))

		update_stmt = 'UPDATE users SET expectedMsgType = %s, tempParams = %s WHERE userID = %s'
		cur.executemany(update_stmt, update_users)
		conn.commit()


def sendLecturePushes(conn, bot, current_time_minutes):
	"""
	Sends the lecture plan pushes
	@param conn: The SQL connection
	@param bot: The bot instance
	@param current_time_minutes: The current time
	"""
	# For the next day
	tomorrow = datetime.now() + timedelta(days=1)
	weekday = int(tomorrow.weekday())
	dateString = tomorrow.strftime("%Y-%m-%d")
	# Normally at 18:00 but customizable
	if weekday < 5:
		cur = conn.cursor()
		get_users_sql = """SELECT chatID, name, course FROM users WHERE lecturePushTime = %s AND wantsLecturePlan = true AND pauseAllNotifications = false"""
		cur.execute(get_users_sql, (current_time_minutes,))
		users = cur.fetchall()
		cur.close()

		if len(users) > 0:
			lf = LectureFetcher(conn)
			courses = lf.getAllKnownCourses()
			courseDict = {}
			for course in courses:
				plan = lf.getFormattedLectures(course, dateString, False)
				if plan:
					time = lf.getFirstLectureTime(course, dateString, False)
					courseDict[course] = [plan, time]
				else:
					courseDict[course] = [None, None]

			# Send the push for the users
			for user in users:
				chatID = user[0]
				name = user[1]
				course = user[2]

				plan = courseDict[course][0]
				try:
					if plan:
						firstLectureTime = courseDict[course][1]

						bot.sendMessage(chatID,
										('Howdy {}. Tomorrow your first lecture begins '
										 + 'at {}. Here is the plan for tomorrow:').format(name, firstLectureTime))
						bot.sendMessage(chatID, plan, parse_mode=ParseMode.HTML)
					else:
						bot.sendMessage(chatID,
										(
											'Howdy {}. Tomorrow, you don\'t have any lectures! Enjoy your free time!').format(
											name))
				except telegram.error.Unauthorized:
					continue


def sendUnpauseNotificationsPushes(conn, bot, current_time_minutes):
	"""
	Sends the unpause notification reminder pushes
	@param conn: The SQL connection
	@param bot: The bot instance
	@param current_time_minutes: The current time
	"""
	# Get required dates
	tomorrow = datetime.now() + timedelta(days=1)
	weekday = int(tomorrow.weekday())
	dateString = tomorrow.strftime("%Y-%m-%d")

	# At 18:00 and if the next day is a monday because thats when theory phases start
	if current_time_minutes == '18:00' and weekday == 0:
		lf = LectureFetcher(conn)
		courses = lf.getAllKnownCourses()
		for course in courses:
			plan = lf.getFormattedLectures(course, dateString)

			if plan:
				if "beginn theoriephase" in plan.lower():
					cur = conn.cursor()
					get_users_sql = """SELECT chatID, name, course FROM users WHERE course = %s AND pauseAllNotifications = true"""
					set_expected_msg_type = """UPDATE users SET expectedMsgType = 'wantstounpausepush' WHERE course = %s AND pauseAllNotifications = true"""
					cur.execute(get_users_sql, (course,))
					cur.execute(set_expected_msg_type, (course,))
					users = cur.fetchall()
					cur.close()

					for user in users:
						chatID = user[0]
						name = user[1]
						course = user[2]

						try:
							bot.sendMessage(chatID, (
								"Hi, {}! I noticed that your next theory phase starts tomorrow. Do you want to unpause the push notifications?".format(
									name)),
											reply_markup=ReplyKeyboardMarkup([[KeyboardButton('Yes'),
																			   KeyboardButton('No')]],
																			 resize_keyboard=True,
																			 one_time_keyboard=True))
						except telegram.error.Unauthorized:
							continue


def sendExamWarningPushes(conn, bot, current_time_minutes):
	"""
	Sends the exam warning pushes
	@param conn: The SQL connection
	@param bot: The bot instance
	@param current_time_minutes: The current time
	"""

	# Run only at 18:00
	if current_time_minutes == '18:00':
		# Check for exam 7 days from now
		oneWeekFromNow = datetime.now() + timedelta(days=7)
		dateString = oneWeekFromNow.strftime("%Y-%m-%d")

		lf = LectureFetcher(conn)
		courses = lf.getAllKnownCourses()
		courseDict = {}
		for course in courses:
			plan = lf.getLecturesByCourseName(course, dateString)
			if len(plan) > 0:
				planContainsExam = False
				examName = ''
				beginTime = ''
				endTime = ''
				for event in plan:
					if 'Prüfung' in event.categories:
						planContainsExam = True
						examName = event.summary
						beginTime = str(event.start)[11:16]
						endTime = str(event.end)[11:16]

				if planContainsExam:
					courseDict[course] = [examName, beginTime, endTime]

		# Only run the following code if at least one exam has to be announced
		if len(list(courseDict)) > 0:
			cur = conn.cursor()
			get_users_sql = """SELECT chatID, name, course FROM users WHERE wantsExamWarning = true"""
			cur.execute(get_users_sql)
			users = cur.fetchall()
			cur.close()

			if len(users) > 0:
				# Send the push for the users
				for user in users:
					chatID = user[0]
					name = user[1]
					course = user[2]

					try:
						# Only send the push if there is an exam for the current user's course
						if course in list(courseDict):
							examInfo = courseDict[course]

							bot.sendMessage(chatID,
											('Howdy {}. Unfortunately, you have an exam one week from now on {}: {}.\n'
											 + 'The exam will start at {} and end at {}. I wish you the best of luck!')
											.format(name, dateString, examInfo[0], examInfo[1], examInfo[2]))
					except telegram.error.Unauthorized:
						continue
