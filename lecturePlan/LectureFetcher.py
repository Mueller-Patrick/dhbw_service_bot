"""
 This class is used to fetch the lectures for the next day from the .ical file provided via DHBW RaPla.
"""
from icalevents.icalevents import events
import logging
import sys
import traceback
from dateutil.parser import parse


class LectureFetcher:
	def __init__(self, conn):
		self.conn = conn
		self.linkDict = self.getRaplaLinks()

	def getRaplaLinks(self) -> {}:
		"""
		Fetches all courses and the corresponding RaPla links from SQL
		@return: A dict with the course name as key and the RaPla link as value
		"""
		cur = self.conn.cursor()
		fetch_links_sql = """SELECT name, rapla_link FROM courses"""
		linkList = {}
		cur.execute(fetch_links_sql)
		for course in cur.fetchall():
			name = course[0]
			link = course[1]
			linkList[name] = link

		self.conn.commit()
		cur.close()
		return linkList

	def courseExists(self, course: str) -> bool:
		"""
		Check if the given course is known to the bot
		@param course: The course to be checked
		@return: If this course is known to the bot
		"""
		return course.upper() in self.linkDict

	def validateLink(self, link: str) -> bool:
		"""
		Check if the given link could be a valid RaPla link
		@param link: The link to be checked
		@return: If the link could be valid
		"""
		try:
			events(link)
			# TODO: Rewrite this with a regex
			if 'https://rapla.dhbw-karlsruhe.de/rapla' in link:
				return True
			else:
				return False
		except:
			return False

	def addRaplaLink(self, courseName: str, link: str):
		"""
		Add a rapla link to the SQL table
		@param courseName: The name of the course the link belongs to
		@param link: The RaPla link
		"""
		self.linkDict[courseName.upper()] = link
		cur = self.conn.cursor()
		insert_link_sql = """UPDATE courses SET rapla_link = %s WHERE name = %s"""
		cur.execute(insert_link_sql, (link, courseName.upper()))
		self.conn.commit()
		cur.close()

	# Get all events for this link
	# The dayString needs to have the format YYYY-MM-DD (The only decent date format if you asked me)
	def getLecturesByLink(self, link: str, dayString: str) -> []:
		"""
		Get all events for the given day and ical link
		@param link: The link to the ical file
		@param dayString: The day for which the lectures should be returned in the format YYYY-MM-DD
		@return: A list of icalevents event objects
		"""
		try:
			lectures = events(url=link, start=parse(dayString).date())
			lectures.sort()
			returnList = []
			for lec in lectures:
				if dayString in str(lec):
					returnList.append(lec)
			return returnList
		except:
			e = sys.exc_info()
			exc_type, exc_value, exc_traceback = sys.exc_info()
			stack = traceback.extract_tb(exc_traceback)
			logging.warning('Error while fetching lectures, Error: %s, Stacktrace: %s', e, stack)
			logging.warning('LectureFetcher.getLecturesByLink: Invalid link or dayString given: %s, %s', link,
							dayString)
			return ''

	# Get all events for this course
	# The dayString needs to have the format YYYY-MM-DD (The only decent date format if you asked me)
	def getLecturesByCourseName(self, courseName: str, dayString: str) -> []:
		"""
		Get all events for the given day and course
		@param courseName: The name of the course to return the lectures for, e.g. TINF19B4
		@param dayString: The day for which the lectures should be returned in the format YYYY-MM-DD
		@return: A list of icalevents event objects
		"""
		try:
			link = self.linkDict.get(courseName.upper())  # courseName.upper() writes the name in all caps
		# just in case the user was to stupid to enter it right
		except:
			# If no link is found
			link = ''

		if link == '':
			logging.warning('In LectureFetcher: Link for course %s not provided, but requested', courseName)
			return ''
		else:
			return self.getLecturesByLink(link, dayString)

	def getFirstLectureTime(self, courseName: str, dayString: str) -> str:
		"""
		Get the time when the first lecture begins for the given day and course
		@param courseName: The name of the course to return the lectures for, e.g. TINF19B4
		@param dayString: The day for which the lectures should be returned in the format YYYY-MM-DD
		@return: The time when the first lecture starts in the format HH:MM
		"""
		lectures = self.getLecturesByCourseName(courseName, dayString)

		if lectures and lectures != '':
			beginTime = str(lectures[0].start)[
						11:16]  # Get the substring from index 11 to index 16 of the first lecture (this
			# substring is the HH:MM format of the begin time)
			return beginTime
		else:
			logging.warning('In LectureFetcher.getFirstLectureTime(): Tried to fetch time but can\'t fetch plan')
			return ''

	def getFormattedLectures(self, courseName: str, dayString: str) -> str:
		"""
		Returns the lectures for the given day and course in a human-friendly format ready to be sent by the bot

		@param courseName: The name of the course to return the lectures for, e.g. TINF19B4
		@param dayString: The day for which the lectures should be returned in the format YYYY-MM-DD
		@return: The formatted lectures
		"""
		lectures = self.getLecturesByCourseName(courseName, dayString)

		# If no link for this course has been provided
		if lectures == '':
			retString = 'No RaPla link for this course has been provided. Please contact @P4ddy_m.'
		else:
			retString = ''
			for lecture in lectures:
				beginTime = str(lecture.start)[11:16]
				endTime = str(lecture.end)[11:16]
				if retString != '':  # To skip the first item in the list
					retString += ('\n' + beginTime + ' - ' + endTime + ': <b>' + lecture.summary + '</b>')
				else:  # The first element doesnt need a line break at the start
					retString += (beginTime + ' - ' + endTime + ': <b>' + lecture.summary + '</b>')

		return retString

	def setUserOfCourse(self, courseName: str):
		"""
		Updates the given courses field "has_users" to true
		@param courseName: The course to be updated
		"""
		cur = self.conn.cursor()
		if courseName.upper() not in self.linkDict:

			self.linkDict[courseName.upper()] = ''
			# Insert the new course
			course_insert_sql = """INSERT INTO courses (name) VALUES (%s)"""
			cur.execute(course_insert_sql, (courseName.upper(),))
		else:
			# Update the course
			course_insert_sql = """UPDATE courses SET has_users = 1 WHERE name = %s"""
			cur.execute(course_insert_sql, (courseName.upper(),))

		self.conn.commit()
		cur.close()

	def getAllKnownCourses(self) -> [str]:
		"""
		Get all known course names
		@return: A list of course names
		"""
		return list(self.linkDict)
