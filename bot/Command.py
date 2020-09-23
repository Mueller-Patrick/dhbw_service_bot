"""
 This class is used by the bot to run the commands.
"""
from menu import MenuSaver as menu
from datetime import datetime
from bot import CommandFunctions as cf, MessageFunctions as mf


class Command:
	def __init__(self, message, bot, conn):
		self.message = message
		self.bot = bot
		self.cfunctions = cf.CommandFunctions(message, bot, conn)
		self.mfunctions = mf.MessageFunctions(message, bot, conn)
		self.conn = conn

		# Defined commands
		self.commands = ['/start', '/help', '/privacy', '/whatdoyouknowaboutme', '/getmenu',
						 '/sendmessagetoeveryone', '/getlectures', '/getmeme', '/reportbug', '/settings',
						 '/adminrate', '/getdirections']

	# Used to find the requested command
	def findCommand(self):
		text = self.message.text.lower()
		if text in self.commands:
			self.performCommand(text)
		else:
			self.bot.sendMessage(self.message.user.chatID, "Unknown command. Say what?")

	def performCommand(self, command):
		callCommandFunctions = {
			# Basic commands
			'/help': self.cfunctions.command_help,
			'/start': self.cfunctions.command_start,
			'/privacy': self.cfunctions.command_privacy,
			'/whatdoyouknowaboutme': self.cfunctions.command_whatdoyouknowaboutme,
			'/getmenu': self.cfunctions.command_getmenu,
			'/getlectures': self.cfunctions.command_getlectures,
			'/getmeme': self.cfunctions.command_getmeme,
			'/reportbug': self.cfunctions.command_reportbug,
			'/settings': self.cfunctions.command_settings,
			# Commands only Patrick can use
			'/sendmessagetoeveryone': self.cfunctions.command_sendmessagetoeveryone,
			'/adminrate': self.cfunctions.command_adminrate,
			'/getdirections': self.cfunctions.command_getdirections
		}

		commandFunc = callCommandFunctions.get(command)
		commandFunc()

	def interpretMessage(self):
		type = self.message.user.expectedMessageType

		callMessageFunctions = {
			# No normal message expected
			'': self.mfunctions.message_unknown,
			# Name of user from /start
			'startname': self.mfunctions.message_startname,
			# Expects a day input from the user
			'lectureplanday': self.mfunctions.message_lectureplanday,
			'menuday': self.mfunctions.message_menuday,
			# Meme-related stuff
			'memetype': self.mfunctions.message_memetype,
			'memeid': self.mfunctions.message_memeid,
			# Meal-rating-related stuff
			'mealtoberated': self.mfunctions.message_mealtoberated,
			'mealrating': self.mfunctions.message_mealrating,
			# Expects a bug description
			'bugdescription': self.mfunctions.message_bugdescription,
			# Expects a direction type
			'directionstype': self.mfunctions.message_directionstype,
			# Settings
			'settingstype': self.mfunctions.message_settingstype,
			'settingspersonalinfo': self.mfunctions.message_settingspersonalinfo,
			'settingssubscriptions': self.mfunctions.message_settingssubscriptions,
			'settingstimes': self.mfunctions.message_settingstimes,
			'changepersonalinfo': self.mfunctions.message_changepersonalinfo,
			'changepushtime': self.mfunctions.message_changepushtime,
			'newcoursepassword': self.mfunctions.message_newcoursepassword,
			'coursepassword': self.mfunctions.message_coursepassword,
			'raplalink': self.mfunctions.message_raplalink,
			# If the user wants to unpause push notifications again when the next theory phase starts
			'wantstounpausepush': self.mfunctions.message_wantstounpausepush,
			# Broadcast function for Patrick
			'broadcastmessage': self.mfunctions.message_broadcastmessage
		}

		messageFunc = callMessageFunctions.get(type)
		messageFunc()
