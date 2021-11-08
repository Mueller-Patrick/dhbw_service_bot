"""
 This class is used to fetch the lectures for the next day from the .ical file provided via DHBW RaPla.
"""
import re
from icalevents.icalevents import events
import logging
import sys
import traceback
from dateutil.parser import parse


def validate_link(link: str) -> bool:
	"""
	Check if the given link could be a valid RaPla link
	@param link: The link to be checked
	@return: If the link could be valid
	"""

	# https://api.plutodev.de/rapla-middleware?user=eisenbiegler&file=TINF19B4&blockers=0&wahl=4&pflicht=2
	# https://rapla.dhbw-karlsruhe.de/rapla?page=calendar&user=eisenbiegler&file=TINF19B4

	pattern = r"^(https://)?" \
	          r"((rapla\\.dhbw-karlsruhe\\.de/rapla)" \
	          r"|(api\\.plutodev\\.de/rapla-middleware)" \
	          r"\?(\\w+=\\w+)(&\\w+=\\w+)*)$"
	if bool(re.match(pattern, link)):
		try:
			events(link)
			return True
		except Exception as e:
			e = sys.exc_info()
			exc_type, exc_value, exc_traceback = sys.exc_info()
			stack = traceback.extract_tb(exc_traceback)
			logging.error('Error while validating link, Error: %s, Stacktrace: %s', e, stack)
			return False
	return False


class LectureFetcher(object):
	def __init__(self, conn=None):
		if conn is None:  # For testing purposes. If no connection is given, prefill the link_dict with the 19B4 link.
			self.link_dict = {1: 'https://rapla.dhbw-karlsruhe.de/rapla?page=ical&user=eisenbiegler&file=TINF19B4'}
		else:
			self.conn = conn
			self.link_dict = self.get_rapla_links()

	def get_rapla_links(self) -> {}:
		"""
		Fetches all courses and the corresponding RaPla links from SQL
		@return: A dict with the course name as key and the RaPla link as value
		"""
		link_list = {}
		fetch_links_sql = """
			SELECT userID, custom_rapla_link 
			FROM users 
			WHERE custom_rapla_link != ''
		"""

		cur = self.conn.cursor()
		cur.execute(fetch_links_sql)

		for course in cur.fetchall():
			user_id = int(course[0])
			link = course[1]
			link_list[user_id] = link

		self.conn.commit()
		cur.close()

		return link_list

	def add_rapla_link(self, user_id: int, link: str):
		"""
		Add a rapla link to the SQL table
		@param user_id: The id of the user the link belongs to
		@param link: The RaPla link
		"""
		self.link_dict[user_id] = link
		cur = self.conn.cursor()
		insert_link_sql = """UPDATE users SET custom_rapla_link = %s WHERE userID = %s"""
		cur.execute(insert_link_sql, (link, user_id))
		self.conn.commit()
		cur.close()

	# Get all events for this link
	# The dayString needs to have the format YYYY-MM-DD (The only decent date format if you asked me)
	def get_lectures_by_link(self, link: str, dayString: str) -> []:
		"""
		Get all events for the given day and ical link
		@param link: The link to the ical file
		@param dayString: The day for which the lectures should be returned in the format YYYY-MM-DD
		@return: A list of icalevents event objects
		"""
		try:
			lectures = events(url=link, start=parse(dayString).date())
			lectures.sort()
			return_list = []
			for lec in lectures:
				if dayString in str(lec):
					return_list.append(lec)
			return return_list
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
	def get_lectures_by_user_id(self, user_id: int, day_string: str) -> []:
		"""
		Get all events for the given day and course
		@param courseName: The name of the course to return the lectures for, e.g. TINF19B4
		@param dayString: The day for which the lectures should be returned in the format YYYY-MM-DD
		@return: A list of icalevents event objects
		"""
		try:
			link = self.link_dict.get(user_id)  # courseName.upper() writes the name in all caps
		# just in case the user was to stupid to enter it right
		except:
			# If no link is found
			link = ''

		if link == '':
			logging.warning('In LectureFetcher: Link for user %s not provided, but requested', user_id)
			return ''
		else:
			return self.get_lectures_by_link(link, day_string)

	def get_formatted_lectures(self, user_id: int, day_string: str, include_blockers: bool = True) -> str:
		"""
		Returns the lectures for the given day and course in a human-friendly format ready to be sent by the bot

		@param courseName: The name of the course to return the lectures for, e.g. TINF19B4
		@param dayString: The day for which the lectures should be returned in the format YYYY-MM-DD
		@param includeBlockers: If blockers should be treated as lectures and hence be returned
		@return: The formatted lectures
		"""
		lectures = self.get_lectures_by_user_id(user_id, day_string)

		# If no link for this course has been provided
		if lectures == '':
			ret_string = 'No RaPla link for this course has been provided. Please contact @P4ddy_m.'
		else:
			ret_string = ''
			for lecture in lectures:
				if not include_blockers and ('Sonstiger Termin' in lecture.categories or 'Präsenz' in lecture.summary):
					continue

				begin_time = str(lecture.start)[11:16]
				end_time = str(lecture.end)[11:16]
				if ret_string != '':  # To skip the first item in the list
					ret_string += ('\n' + begin_time + ' - ' + end_time + ': <b>' + lecture.summary + '</b>')
				else:  # The first element doesnt need a line break at the start
					ret_string += (begin_time + ' - ' + end_time + ': <b>' + lecture.summary + '</b>')

		return ret_string

	def get_all_known_courses(self) -> [str]:
		"""
		Get all known course names
		@return: A list of course names
		"""
		return list(self.link_dict)
