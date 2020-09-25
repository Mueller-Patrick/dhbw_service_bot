import telegram
from telegram import ParseMode
import os
import logging
from datetime import datetime, timedelta
import sql.SQLConnectionHandler as sqlhandler
from lecturePlan.LectureFetcher import LectureFetcher
import menu.MenuSaver as menu
import sys
import traceback


def configure_telegram():
	"""
	Configures the bot with a Telegram Token.

	Returns a bot instance.
	"""

	TELEGRAM_TOKEN = os.environ.get('DHBW_TELEGRAM_TOKEN')
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
	#sendMenuPushes(conn, bot, current_time_minutes)
	sendReturnDirections(conn, bot, current_time_minutes)
	#sendMenuRatingPushes(conn, bot, current_time_minutes)
	sendLecturePushes(conn, bot, current_time_minutes)
	sendUnpauseNotificationsPushes(conn, bot, current_time_minutes)


def sendMenuPushes(conn, bot, current_time_minutes):
	# For the same day
	# Normally at 06:00 but customizable
	cur = conn.cursor()
	get_users_sql = """SELECT chatID, name FROM users WHERE menuPushTime = %s AND wantsMenu = true AND pauseAllNotifications = false AND userID = 1"""
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
				courseDict[course] = [lf.getFormattedLectures(course, dateString),
									  lf.getFirstLectureTime(course, dateString)]

			# Send the push for the users
			for user in users:
				chatID = user[0]
				name = user[1]
				course = user[2]

				plan = courseDict[course][0]
				firstLectureTime = courseDict[course][1]

				bot.sendMessage(chatID,
										  ('Howdy {}. Tomorrow your first lecture begins '
										   + 'at {}. Here is the plan for tomorrow:').format(name, firstLectureTime))
				bot.sendMessage(chatID, plan, parse_mode=ParseMode.HTML)

def sendUnpauseNotificationsPushes(conn, bot, current_time_minutes):
	# At 18:00
	if current_time_minutes == '18:00':
		pass
		# Condition: pauseAllNotifications, plan fpr tomorrow contains "Beginn Theoriephase"

if __name__ == '__main__':
	sendPushes()
	# For debugging
	#sendMenuPushes(sqlhandler.getvServerConnection(), configure_telegram(), '06:00')
