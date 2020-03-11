"""
 User class. Used to save every registered user with their personal preferences.
"""


class User:
	def __init__(self, chatID):
		self.chatID = chatID
		self.name = ''
		self.expectedMessageType = ''
		self.tempParams = {}
		self.wantsMenu = False
		self.course = ''
		self.wantsLecturePlan = False
		self.address = ''
		self.wantsTransportInfo = False
		self.wantsToRateMeals = True
		self.pushTimes = {
			'menu': '06:00',
			'lecture': '18:00'
		}
