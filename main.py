"""
 Main file. Handles the bot activity.
"""
import requests
import json
import asyncio
import Bot as bt
import User as usr
import patrickID


class main:
	def __init__(self):
		self.token = self.get_token()
		self.users = self.get_users()
		self.bot = bt.Bot(telegram_token=self.token, users=self.users)
		asyncio.run(self.mainLoop())

	async def mainLoop(self):
		run = True
		while(run):
			await asyncio.sleep(1)
			self.bot.getUpdates()
			self.bot.handleMessages()
			if self.bot.tellMainToClose:
				run = False
		self.close()

	def get_token(self):
		return patrickID.token

	def get_users(self):
		with open('userDict.json', 'r') as userFile:
			usersJson = userFile.read()
		userFile.close()

		usersList = json.loads(usersJson)

		users = []
		for user in usersList:
			chatID = user.get('chatID')
			name = user.get('name')
			expectedMsgType = user.get('expectedMsgType')
			currentUser = usr.User(chatID)
			currentUser.setName(name)
			currentUser.setExpectedMessageType(expectedMsgType)
			users.append(currentUser)

		return users

	# Used to save all users to a dict before closing.
	def close(self):
		usersList = []
		for user in self.bot.users:
			toAppend = {
				"chatID": user.chatID,
				"name": user.name,
				"expectedMsgType": user.expectedMessageType
			}
			usersList.append(toAppend)
		usersJson = json.dumps(usersList)

		with open('userDict.json', 'w') as userFile:
			userFile.write(usersJson)
		userFile.close()

		self.bot.close()
		if len(self.bot.messages) > 0:
			print("Bot has to handle some more commands, please wait.")


# Starting method
if __name__ == "__main__":
	main()
