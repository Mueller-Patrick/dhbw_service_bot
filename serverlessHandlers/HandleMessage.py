"""
 Bot class, an object of type bot is created in main.init() at startup with the required parameters.
"""

import telegram
import logging

import bot.User as usr
import bot.Message as msg
import sql.SQLConnectionHandler as sqlhandler
import sql.SQLRowConverter as sqlconverter
import sys
import traceback

import bot.Command as cmd

logger = logging.getLogger()


class HandleMessage:
	def __init__(self, bot, chat_id, text, message_id):
		# Get user object from SQL
		conn = sqlhandler.getConnection()
		cur = conn.cursor()
		select_user_query = """SELECT userID, chatID, name, expectedMsgType, tempParams, wantsMenu, course, 
		wantsLecturePlan, address, wantsTransportInfo, wantsToRateMeals, menuPushTime, lecturePushTime, 
		pauseAllNotifications FROM users WHERE chatID = %s """
		cur.execute(select_user_query, (chat_id,))
		userSqlRow = cur.fetchall()
		conn.commit()
		user = usr.User(chat_id)
		newUser = False
		if cur.rowcount == 1:
			user = sqlconverter.getUser(userSqlRow[0])
		elif cur.rowcount > 1:
			logging.warning('More than one user with chatID %s found!', chat_id)
			user = sqlconverter.getUser(userSqlRow[0])
		else:
			logging.info('Creating new user for chatID %s.', chat_id)
			newUser = True
		cur.close()

		# Process message
		try:
			message = msg.Message(user, text, message_id)

			if message.isCommand:
				cmd.Command(message, bot, conn).findCommand()
			else:
				cmd.Command(message, bot, conn).interpretMessage()
		except:
			e = sys.exc_info()
			exc_type, exc_value, exc_traceback = sys.exc_info()
			stack = traceback.extract_tb(exc_traceback)
			logging.warning("An error occured handling the following message: %s. Error: %s, Stacktrace: %s", text, e,
							stack)
			bot.sendMessage(chat_id,
							"An Error occured while trying to fulfill your request. Currently, not all commands"
							+ " are available due to the porting. Please try again another time. You can check the progress"
							+ " here: https://github.com/Mueller-Patrick/dhbw_service_bot")

		# Save user object to SQL
		cur = conn.cursor()
		if newUser:
			print("new")
			insert_user_query = """INSERT INTO users (chatID, name, expectedMsgType, tempParams, wantsMenu, course, 
			wantsLecturePlan, address, wantsTransportInfo, wantsToRateMeals, menuPushTime, lecturePushTime, 
			pauseAllNotifications) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) """
			cur.execute(insert_user_query, sqlconverter.getUserInsertTuple(user))
		else:
			print("Update")
			update_user_query = """UPDATE users SET name = %s, expectedMsgType = %s, tempParams = %s, wantsMenu = %s, 
			course = %s, wantsLecturePlan = %s, address = %s, wantsTransportInfo = %s, wantsToRateMeals = %s, 
			menuPushTime = %s, lecturePushTime = %s, pauseAllNotifications = %s WHERE userID = %s """
			cur.execute(update_user_query, sqlconverter.getUserUpdateTuple(user))

		conn.commit()
		cur.close()
		conn.close()
