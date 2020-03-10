import logging
import asyncio
from datetime import datetime
import json
from mainHelpers import HelperFunctions


class AsnycLoops:
	def __init__(self, main):
		self.main = main
		self.helpers = HelperFunctions.HelperFunctions(self.main)

	async def mainLoop(self):
		while True:
			try:
				# Wait for commands by users
				await self.main.bot.getUpdates()
				self.main.bot.handleMessages()
			except Exception as exc:
				logging.error('Exception on mainLoop: %s', exc)

			# Check if it should stop
			if self.main.bot.tellMainToClose:
				break

		self.main.close()

	async def pushLoop(self):
		while True:
			await asyncio.sleep(29)
			now = datetime.now()
			timeString = now.strftime("%H:%M")
			weekday = now.weekday()

			# For menu push
			if weekday < 5:  # Because monday is 0...
				canteenOpen = True
			else:
				canteenOpen = False

			# For lecture Plan push
			if weekday < 4 or weekday == 6:  # Monday to Thursday and also Sunday
				sendPlanToday = True
			else:
				sendPlanToday = False

			# run daily at 06:00 for all users that want the menu
			if str(timeString) == '06:00' and not self.main.sentMenuToday and canteenOpen:
				self.main.sentMenuToday = True
				logging.info('Sending menu')
				self.helpers.sendMenu()
			elif str(timeString) == '11:24' and not self.main.sentLecturesToday and sendPlanToday:
				self.main.sentLecturesToday = True
				logging.info('Sending lecture plans')
				self.helpers.sendLectures()
			elif str(timeString) == '14:30' and not self.main.askedForRatingToday and canteenOpen:
				self.main.askedForRatingToday = True
				logging.info('Sending menu rating requests')
				self.helpers.sendMenuRating()
			# Reset the boolean to send the menu for today again.
			# Do this only if seconds < 30 because otherwise it would happen twice.
			elif timeString == '23:59' and int(datetime.now().strftime('%S')) < 30:
				logging.info('Resetting variables and writing usage stats')
				self.helpers.writeUsageStats(True)
				self.main.sentMenuToday = False
				self.main.sentLecturesToday = False

			# Check if it should stop
			if self.main.bot.tellMainToClose:
				break
		self.main.close()

	# Used to save the current users all hour to minimize data loss in case of a server failure.
	async def saveLoop(self):
		while True:
			await asyncio.sleep(59)
			now = datetime.now()
			timeString = now.strftime("%H:%M")
			# run every full our (so at xx:00)
			if ':05' in str(timeString):
				# Save user data
				usersList = []
				for user in self.main.bot.users:
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
						"wantsToRateMeals": user.wantsToRateMeals
					}
					usersList.append(toAppend)
				usersJson = json.dumps(usersList, indent=4)

				with open('bot/userDict.json', 'w') as userFile:
					userFile.write(usersJson)
				userFile.close()

				# save rapla links
				self.main.lfetcher.writeLinksToJson()

				# save usage stats
				self.helpers.writeUsageStats(False)

				logging.info('Saved all preferences')

			# Check if it should stop
			if self.main.bot.tellMainToClose:
				break
		self.main.close()
