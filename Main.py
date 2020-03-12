"""
 Main file. Handles the bot activity.
"""
import json
import asyncio
from bot import Bot as bt
import telegram_secrets
from datetime import datetime
from lecturePlan import LectureFetcher as lf
from memes import Memes
import logging
from mainHelpers import AsyncLoops, HelperFunctions


class Main:
	def __init__(self):
		self.token = self.getToken()
		self.lfetcher = lf.LectureFetcher()
		self.memes = Memes.Memes()

		self.asyncLoops = AsyncLoops.AsnycLoops(self)
		self.helperFunctions = HelperFunctions.HelperFunctions(self)

		self.bot = bt.Bot(telegram_token=self.token, users=self.helperFunctions.getUsers(),
						  lectureFetcher=self.lfetcher,
						  memes=self.memes)

		self.customPushTimes = self.helperFunctions.getPreferredPushTimes()

		# Configure logging
		logfile = 'logs/main_application_' + datetime.now().strftime('%Y-%m-%d') + '.log'
		logging.basicConfig(filename=logfile, level=logging.INFO,
							format='%(asctime)s---%(levelname)s:%(message)s',
							datefmt='%Y-%m-%d %H:%M:%S')

		# Runs the three coroutines independent from each other
		loop = asyncio.get_event_loop()
		cors = asyncio.wait([self.asyncLoops.mainLoop(), self.asyncLoops.pushLoop(), self.asyncLoops.saveLoop()])
		# Problem here: If one loop dies, the other two are still running and no error is thrown.
		# If e.g. the mainLoop dies from an error, we see nothing on the console and the other two coroutines
		# still work as expected.
		loop.run_until_complete(cors)

	def getToken(self):
		return telegram_secrets.token

	# Used to save all users to a dict before closing.
	def close(self):
		logging.info('Closing bot now')
		# save user data
		usersList = []
		for user in self.bot.users:
			toAppend = {
				"chatID": user.chatID,
				"name": user.name,
				"expectedMsgType": user.expectedMessageType,
				"tempParams": user.tempParams,
				"wantsMenu": user.wantsMenu,
				"course": user.course,
				"wantsLecturePlan": user.wantsLecturePlan,
				"address": user.address,
				"wantsTransportInfo": user.wantsTransportInfo,
				"wantsToRateMeals": user.wantsToRateMeals,
				"pushTimes": user.pushTimes,
				"pauseAllNotifications": user.pauseAllNotifications
			}
			usersList.append(toAppend)
		usersJson = json.dumps(usersList, indent=4)

		with open('bot/userDict.json', 'w') as userFile:
			userFile.write(usersJson)
		userFile.close()

		# Save rapla links
		self.lfetcher.writeLinksToJson()

		# Save usage stats
		self.helperFunctions.writeUsageStats(False)

		# tell the bot to terminate
		self.bot.close()
		if len(self.bot.messages) > 0:
			logging.info('Bot has to handle more commands and will terminate once finished.')


# Starting method
if __name__ == "__main__":
	Main()
