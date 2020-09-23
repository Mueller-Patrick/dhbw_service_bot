import pymysql
import os
import sys
import logging

def getConnection():
	try:
		conn = pymysql.connect(
			user=os.environ['AWS_DHBW_Bot_SQL_USER'],
			password=os.environ['AWS_DHBW_Bot_SQL_PASSWORD'],
			host=os.environ['AWS_DHBW_Bot_SQL_SERVER'],
			port=3306,
			database=os.environ['AWS_DHBW_Bot_SQL_DATABASE']
		)

		return conn
	except pymysql.Error as e:
		logging.error('SQL Connection error: %s', e)
		return
