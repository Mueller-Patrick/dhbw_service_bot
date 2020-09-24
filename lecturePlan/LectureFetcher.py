"""
 This class is used to fetch the lectures for the next day from the .ical file provided via DHBW RaPla.
"""
import json
from icalevents.icalevents import events
from icalendar import Calendar as cal, Event as ev
import logging
from datetime import datetime
import sys
import traceback


class LectureFetcher:
	def __init__(self, conn):
		self.conn = conn
		self.linkDict = self.getRaplaLinks()

	def getRaplaLinks(self):
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
		self.linkDict[courseName.upper()] = link
		cur = self.conn.cursor()
		insert_link_sql = """UPDATE courses SET rapla_link = %s WHERE name = %s"""
		cur.execute(insert_link_sql, (link, courseName.upper()))
		self.conn.commit()
		cur.close()

	# Check if the course is already known. If not, returns false so we can go on and ask the user for the link.
	def checkForCourse(self, course):
		if course.upper() in self.linkDict:
			if self.linkDict[course.upper()] != '':
				return True
			else:
				return False
		else:
			return False

	# Get all events for this link
	# The dayString needs to have the format YYYY-MM-DD (The only decent date format if you asked me)
	def getLecturesByLink(self, link, dayString):
		try:
			lectures = events(url=link)
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
			logging.warning('LectureFetcher.getLecturesByLink: Invalid link or dayString given: %s, %s', link, dayString)
			return ''

	# Get all events for this course
	# The dayString needs to have the format YYYY-MM-DD (The only decent date format if you asked me)
	def getLecturesByCourseName(self, courseName, dayString):
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

	# Get the time when the first lecture begins
	# The dayString needs to have the format YYYY-MM-DD (The only decent date format if you asked me)
	def getFirstLectureTime(self, courseName, dayString):
		lectures = self.getLecturesByCourseName(courseName, dayString)

		if lectures and lectures != '':
			beginTime = str(lectures[0].start)[
						11:16]  # Get the substring from index 11 to index 16 of the first lecture (this
			# substring is the HH:MM format of the begin time)
			return beginTime
		else:
			logging.warning('In LectureFetcher.getFirstLectureTime(): Tried to fetch time but can\'t fetch plan')
			return ''

	def getFormattedLectures(self, courseName, dayString):
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
					retString += ('\n' + beginTime + ' - ' + endTime + ': *' + lecture.summary + '*')
				else:  # The first element doesnt need a line break at the start
					retString += (beginTime + ' - ' + endTime + ': *' + lecture.summary + '*')

		return retString

	def getEventObjects(self, courseName, dayString):
		lectures = self.getLecturesByCourseName(courseName, dayString)

		# If no link for this course has been provided
		if lectures == '':
			return False
		else:
			return lectures

	def setUserOfCourse(self, courseName):
		if courseName.upper() not in self.linkDict:
			cur = self.conn.cursor()
			self.linkDict[courseName.upper()] = ''
			# Insert the new course
			course_insert_sql = """INSERT INTO courses (name) VALUES (%s)"""
			cur.execute(course_insert_sql, (courseName.upper(),))
			self.conn.commit()
			cur.close()

	def getAllKnownCourses(self):
		return list(self.linkDict)
