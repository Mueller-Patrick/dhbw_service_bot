"""
 This class is used to fetch the lectures for the next day from the .ical file provided via DHBW RaPla.
"""
import json
from icalevents.icalevents import events
from icalendar import Calendar as cal, Event as ev
import logging


class LectureFetcher:
	def __init__(self):
		self.linkDict = self.getRaplaLinks()

	def getRaplaLinks(self):
		try:
			with open('lecturePlan/raplaLinks.json', 'r') as raplaFile:
				raplaJson = raplaFile.read()
			raplaFile.close()

			linkList = json.loads(raplaJson)
		except:
			with open('lecturePlan/raplaLinks.json', 'w') as raplaFile:
				raplaFile.close()
			linkList = []

		return linkList

	def validateLink(self, link):
		try:
			events(link)
			if 'https://rapla.dhbw-karlsruhe.de/rapla' in link:
				return True
			else:
				return False
		except:
			return False

	def addRaplaLink(self, courseName, link):
		self.linkDict[courseName.upper()][0] = link

	def writeLinksToJson(self):
		linkJson = json.dumps(self.linkDict)

		with open("lecturePlan/raplaLinks.json", "w") as raplaFile:
			raplaFile.write(linkJson)
		raplaFile.close()

	# Check if the course is already known. If not, returns false so we can go on and ask the user for the link.
	def checkForCourse(self, course):
		if course.upper() in self.linkDict:
			if self.linkDict[course.upper()][0] != '':
				return True
			else:
				return False
		else:
			return False

	# Get all events for this link
	# The dayString needs to have the format YYYY-MM-DD (The only decent date format if you asked me)
	def getLecturesByLink(self, link, dayString):
		try:
			lectures = events(link)
			lectures.sort()
			returnList = []
			for lec in lectures:
				if dayString in str(lec):
					returnList.append(str(lec))
			return returnList
		except:
			print('LectureFetcher.getLecturesByLink: Invalid link or dayString given.')
			return ''

	# Get all events for this course
	# The dayString needs to have the format YYYY-MM-DD (The only decent date format if you asked me)
	def getLecturesByCourseName(self, courseName, dayString):
		try:
			link = self.linkDict.get(courseName.upper())[0]  # courseName.upper() writes the name in all caps
			# just in case the user was to stupid to enter it right
		except:
			# If no link is found
			link = ''

		if link == '':
			logging.warning('In LectureFetcher: Link for course %s not provided, but requested', courseName)
			return ''
		else:
			return self.getLecturesByLink(link, dayString)

	# Get the time when the first lecture begins
	# The dayString needs to have the format YYYY-MM-DD (The only decent date format if you asked me)
	def getFirstLectureTime(self, courseName, dayString):
		lectures = self.getLecturesByCourseName(courseName, dayString)

		if lectures and lectures != '':
			beginTime = lectures[0][11:16]  # Get the substring from index 11 to index 16 of the first lecture (this
			# substring is the HH:MM format of the begin time)
			return beginTime
		else:
			logging.warning('In LectureFetcher.getFirstLectureTime(): Tried to fetch time but can\'t fetch plan')
			return ''

	def getFormattedLectures(self, courseName, dayString):
		lectures = self.getLecturesByCourseName(courseName, dayString)

		# If no link for this course has been provided
		if lectures == '':
			retString = 'No RaPla link for this course has been provided. Please contact @PaddyOfficial.'
		else:
			retString = ''
			for lecture in lectures:
				startIndexOfLecture = 26
				endIndexOfLecture = lecture.index('(') - 1
				if retString != '':  # To skip the first item in the list
					retString += ('\n' + lecture[11:16] + ': ' + lecture[startIndexOfLecture:endIndexOfLecture])
				else:  # The first element doesnt need a line break at the start
					retString += (lecture[11:16] + ': ' + lecture[startIndexOfLecture:endIndexOfLecture])

		return retString

	# Returns  true if the course has no users yet
	def firstUserInCourse(self, courseName):
		try:
			firstUser = not self.linkDict.get(courseName.upper())[1]

			return firstUser
		except:
			return True

	def setUserOfCourse(self, courseName):
		if courseName.upper() not in self.linkDict:
			self.linkDict[courseName.upper()] = ['', True]
		else:
			self.linkDict[courseName.upper()][1] = True
