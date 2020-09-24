import bot.User as usr
import ast

def getUser(sql_row):
	userID = sql_row[0]
	chatID = sql_row[1]
	name = sql_row[2]
	expectedMsgType = sql_row[3]
	tempParams = ast.literal_eval(sql_row[4])
	wantsMenu = sql_row[5] == 1
	course = sql_row[6]
	wantsLecturePlan = sql_row[7] == 1
	address = sql_row[8]
	wantsTransportInfo = sql_row[9] == 1
	wantsToRateMeals = sql_row[10] == 1
	menuPushTime = str(sql_row[11])[0:5]
	menuPushTime = menuPushTime if menuPushTime[len(menuPushTime)-1] != ':' else ('0' + menuPushTime)[0:5]
	lecturePushTime = str(sql_row[12])[0:5]
	pauseAllNotifications = sql_row[13] == 1


	user = usr.User(chatID)
	user.userID = userID
	user.name = name
	user.expectedMessageType = expectedMsgType
	user.tempParams = tempParams
	user.wantsMenu = wantsMenu
	user.course = course
	user.wantsLecturePlan = wantsLecturePlan
	user.address = address
	user.wantsTransportInfo = wantsTransportInfo
	user.wantsToRateMeals = wantsToRateMeals
	user.pushTimes['menu'] = menuPushTime
	user.pushTimes['lecture'] = lecturePushTime
	user.pauseAllNotifications = pauseAllNotifications

	return user

def getUserUpdateTuple(user):
	tuple = (
		user.name,
		user.expectedMessageType,
		str(user.tempParams),
		user.wantsMenu,
		user.course,
		user.wantsLecturePlan,
		user.address,
		user.wantsTransportInfo,
		user.wantsToRateMeals,
		user.pushTimes['menu'],
		user.pushTimes['lecture'],
		user.pauseAllNotifications,
		user.userID
	)

	return tuple

def getUserInsertTuple(user):
	tuple = (
		user.chatID,
		user.name,
		user.expectedMessageType,
		str(user.tempParams),
		user.wantsMenu,
		user.course,
		user.wantsLecturePlan,
		user.address,
		user.wantsTransportInfo,
		user.wantsToRateMeals,
		user.pushTimes['menu'],
		user.pushTimes['lecture'],
		user.pauseAllNotifications
	)

	return tuple