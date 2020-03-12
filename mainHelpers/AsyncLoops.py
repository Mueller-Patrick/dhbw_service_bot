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
			await asyncio.sleep(30)
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
			if str(timeString) == '06:00' and canteenOpen and int(datetime.now().strftime('%S')) < 30:
				logging.info('Sending menu')
				self.helpers.sendMenu()
			elif str(timeString) == '18:00' and sendPlanToday and int(datetime.now().strftime('%S')) < 30:
				logging.info('Sending lecture plans')
				self.helpers.sendLectures()
			elif str(timeString) == '14:30' and canteenOpen and int(datetime.now().strftime('%S')) < 30:
				logging.info('Sending menu rating requests')
				self.helpers.sendMenuRating()
			elif str(timeString) == '10:00' and int(datetime.now().strftime('%S')) < 30:
				logging.info('Sending return directions')
				self.helpers.sendReturnDirections()
			# Reset the boolean to send the menu for today again.
			# Do this only if seconds < 30 because otherwise it would happen twice.
			elif timeString == '23:59' and int(datetime.now().strftime('%S')) < 30:
				logging.info('Writing usage stats')
				self.helpers.writeUsageStats(True)

			# Run all the custom push times
			if timeString in list(self.main.customPushTimes) and int(datetime.now().strftime('%S')) >= 30:
				for pushPreference in self.main.customPushTimes[timeString]:
					if pushPreference[0] == 'menu':
						self.helpers.sendMenu(True, pushPreference[1])
					elif pushPreference[0] == 'lecture':
						self.helpers.sendLectures(True, pushPreference[1])
					else:
						logging.warning('AsyncLoops.pushLoop(): Tried to send custom push with unknown type %s',
										pushPreference[0])

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
						"wantsToRateMeals": user.wantsToRateMeals,
						"pushTimes": user.pushTimes
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

				# Also reload the custom push times in case something changed
				self.main.customPushTimes = self.helpers.getPreferredPushTimes()

				logging.info('Saved all preferences')

			# Check if it should stop
			if self.main.bot.tellMainToClose:
				break
		self.main.close()
