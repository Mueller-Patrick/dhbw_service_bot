"""
 This class is used by the bot to run the commands.
"""
import telegram_secrets
from menu import MenuSaver as menu
from datetime import datetime
from bot import CommandFunctions as cf, MessageFunctions as mf


class Command:
	def __init__(self, message, bot):
		self.message = message
		self.bot = bot
		self.cfunctions = cf.CommandFunctions(message, bot)
		self.mfunctions = mf.MessageFunctions(message, bot)

		# Defined commands
		self.commands = ['/start', '/help', '/stopbot', '/privacy', '/whatdoyouknowaboutme', '/subscribemenu',
						 '/unsubscribemenu', '/getmenu', '/subscribelectureplan', '/unsubscribelectureplan',
						 '/sendmessagetoeveryone', '/getlectures', '/subscribetraininfo']

	# Used to find the requested command
	def findCommand(self):
		text = self.message.text.lower()
		if text in self.commands:
			self.performCommand(text)
		else:
			self.bot.sendMessage(self.message.user.chatID, "Unknown command. Say what?")

	def performCommand(self, command):
		callCommandFunctions = {
			'/help': self.cfunctions.command_help,
			'/start': self.cfunctions.command_start,
			'/stopbot': self.cfunctions.command_stopbot,
			'/privacy': self.cfunctions.command_privacy,
			'/subscribemenu': self.cfunctions.command_subscribemenu,
			'/unsubscribemenu': self.cfunctions.command_unsubscribemenu,
			'/whatdoyouknowaboutme': self.cfunctions.command_whatdoyouknowaboutme,
			'/getmenu': self.cfunctions.command_getmenu,
			'/subscribelectureplan': self.cfunctions.command_subscribelectureplan,
			'/unsubscribelectureplan': self.cfunctions.command_unsubscribelectureplan,
			'/sendmessagetoeveryone': self.cfunctions.command_sendmessagetoeveryone,
			'/getlectures': self.cfunctions.command_getlectures,
			'/subscribetraininfo': self.cfunctions.command_subscribetraininfo
		}

		commandFunc = callCommandFunctions.get(command)
		commandFunc()

	def interpretMessage(self):
		type = self.message.user.expectedMessageType

		callMessageFunctions = {
			'': self.mfunctions.message_unknown,
			'name': self.mfunctions.message_name,
			'coursename': self.mfunctions.message_coursename,
			'raplalink': self.mfunctions.message_raplalink,
			'broadcastmessage': self.mfunctions.message_broadcastmessage,
			'changecoursename': self.mfunctions.message_changecoursename,
			'raplalinkwithoutpush': self.mfunctions.message_raplalinkwithoutpush,
			'useraddress': self.mfunctions.message_useraddress,
			'lectureplanday': self.mfunctions.message_lectureplanday,
			'menuday': self.mfunctions.message_menuday
		}

		messageFunc = callMessageFunctions.get(type)
		messageFunc()
