import mariadb
import os
import sys
import logging

def getConnection():
	try:
		conn = mariadb.connect(
			user=os.environ['AWS_DHBW_Bot_SQL_USER'],
			password=os.environ['AWS_DHBW_Bot_SQL_PASSWORD'],
			host=os.environ['AWS_DHBW_Bot_SQL_SERVER'],
			port=3306,
			database=os.environ['AWS_DHBW_Bot_SQL_DATABASE']
		)

		return conn
	except mariadb.Error as e:
		logging.error('SQL Connection error: %s', e)
		return
