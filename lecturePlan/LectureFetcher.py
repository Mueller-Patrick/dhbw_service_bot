"""
 This class is used to fetch the lectures for the next day from the .ical file provided via DHBW RaPla.
"""
import json
from icalevents.icalevents import events
from icalendar import Calendar as cal, Event as ev


class LectureFetcher:
	def __init__(self):
		self.linkDict = self.getRaplaLinks()

	def getRaplaLinks(self):
		with open('lecturePlan/raplaLinks.json', 'r') as raplaFile:
			raplaJson = raplaFile.read()
		raplaFile.close()

		linkList = json.loads(raplaJson)

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
		self.linkDict[courseName] = link

	def writeLinksToJson(self):
		linkJson = json.dumps(self.linkDict)

		with open("lecturePlan/raplaLinks.json", "w") as raplaFile:
			raplaFile.write(linkJson)
		raplaFile.close()

	# Check if the course is already known. If not, returns false so we can go on and ask the user for the link.
	def checkForCourse(self, course):
		if course.upper() in self.linkDict:
			return True
		else:
			return False

	# Get all events for this link
	# The dayString needs to have the format YYYY-MM-DD (The only decent date format if you asked me)
	def getLecturesByLink(self, link, dayString):
		lectures = events(link)
		lectures.sort()
		returnList = []
		for lec in lectures:
			if dayString in str(lec):
				returnList.append(str(lec))

		return returnList

	# Get all events for this course
	# The dayString needs to have the format YYYY-MM-DD (The only decent date format if you asked me)
	def getLecturesByCourseName(self, courseName, dayString):
		link = self.linkDict.get(courseName.upper())  # courseName.upper() writes the name in all caps
		# just in case the user was to stupid to enter it right
		return self.getLecturesByLink(link, dayString)

	# Get the time when the first lecture begins
	# The dayString needs to have the format YYYY-MM-DD (The only decent date format if you asked me)
	def getFirstLectureTime(self, courseName, dayString):
		lectures = self.getLecturesByCourseName(courseName, dayString)

		beginTime = lectures[0][11:16]  # Get the substring from index 11 to index 16 of the first lecture (this
		# substring is the HH:MM format of the begin time)
		return beginTime

	def getFormattedLectures(self, courseName, dayString):
		lectures = self.getLecturesByCourseName(courseName, dayString)

		retString = ''
		for lecture in lectures:
			startIndexOfLecture = 26
			endIndexOfLecture = lecture.index('(') - 1
			if retString != '':  # To skip the first item in the list
				retString += ('\n' + lecture[11:16] + ': ' + lecture[startIndexOfLecture:endIndexOfLecture])
			else:  # The first element doesnt need a line break at the start
				retString += (lecture[11:16] + ': ' + lecture[startIndexOfLecture:endIndexOfLecture])

		return retString
