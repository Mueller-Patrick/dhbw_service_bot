import telegram
from telegram import ParseMode
from telegram import ReplyKeyboardMarkup
from telegram import KeyboardButton
import os
import logging
from datetime import datetime, timedelta
import sql.SQLConnectionHandler as sqlhandler
from lecturePlan.LectureFetcher import LectureFetcher
import menu.MenuSaver as menu
import sys
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
	bot = configure_telegram()
	logging.info('Running push check and sending now')
	current_time_minutes = str(datetime.now())[11:16]

	conn = sqlhandler.getvServerConnection()

	# Menu currently not sent because it doesnt work yet
	# sendMenuPushes(conn, bot, current_time_minutes)

	# Directions not supported currently due to shutdown of google maps API key
	# sendReturnDirections(conn, bot, current_time_minutes)

	# Menu rating currently not sent because it doesnt work yet
	# sendMenuRatingPushes(conn, bot, current_time_minutes)
	sendLecturePushes(conn, bot, current_time_minutes)
	sendUnpauseNotificationsPushes(conn, bot, current_time_minutes)


def sendMenuPushes(conn, bot, current_time_minutes):
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
			# TODO Fix formatting, this doesnt work yet!
			fetchedMenu = menu.Reader(1).get_menu_as_arr()
			print(fetchedMenu)

			# Send the push for the users
			for user in users:
				chatID = user[0]
				name = user[1]
				bot.sendMessage(chatID,
								"Good morning " + name + ", here is the menu for today:")
				for oneMenu in fetchedMenu:
					bot.sendMessage(chatID, oneMenu, parse_mode=ParseMode.HTML)
		except:
			exc_type, exc_value, exc_traceback = sys.exc_info()
			stack = traceback.extract_tb(exc_traceback)
			logging.warning("Could not fetch menu for today. Error: %s, Stacktrace: %s", sys.exc_info(), stack)


def sendReturnDirections(conn, bot, current_time_minutes):
	# For the same day
	# At 10:00
	if current_time_minutes == '10:00':
		pass


# Condition: wantsTransportInfo, !pauseAllNotifications


def sendMenuRatingPushes(conn, current_time_minutes):
	# For the same day
	# At 14:30
	if current_time_minutes == '14:30':
		pass
	# Condition: wantsMenu, wantsToRateMeals, !pauseAllNotifications


def sendLecturePushes(conn, bot, current_time_minutes):
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
				plan = lf.getFormattedLectures(course, dateString)
				if plan:
					time = lf.getFirstLectureTime(course, dateString)
					courseDict[course] = [plan, time]
				else:
					courseDict[course] = [None, None]

			# Send the push for the users
			for user in users:
				chatID = user[0]
				name = user[1]
				course = user[2]

				plan = courseDict[course][0]
				if plan:
					firstLectureTime = courseDict[course][1]

					bot.sendMessage(chatID,
									('Howdy {}. Tomorrow your first lecture begins '
									 + 'at {}. Here is the plan for tomorrow:').format(name, firstLectureTime))
					bot.sendMessage(chatID, plan, parse_mode=ParseMode.HTML)
				else:
					bot.sendMessage(chatID,
									('Howdy {}. Tomorrow, you don\'t have any lectures! Enjoy your free time!').format(
										name))


def sendUnpauseNotificationsPushes(conn, bot, current_time_minutes):
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

						bot.sendMessage(chatID, ("Hi, {}! I noticed that your next theory phase starts tomorrow. Do you want to unpause the push notifications?".format(name)),
											 reply_markup=ReplyKeyboardMarkup([[KeyboardButton('Yes'),
																				KeyboardButton('No')]],
																			  resize_keyboard=True,
																			  one_time_keyboard=True))
