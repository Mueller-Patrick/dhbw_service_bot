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

def getvServerConnection():
	try:
		if os.environ['IS_VSERVER'] == 'true':
			conn = pymysql.connect(
				user=os.environ['vServer_SQL_User'],
				password=os.environ['vServer_SQL_Password'],
				host='localhost',
				port=3306,
				database=os.environ['DHBW_Bot_Database']
			)
		else:
			conn = pymysql.connect(
				user=os.environ['PADDY_SQL_USER'],
				password=os.environ['PADDY_SQL_PASSWORD'],
				host=os.environ['SQL_SERVER'],
				port=3306,
				database=os.environ['DHBW_Bot_Database']
			)

		return conn
	except pymysql.Error as e:
		logging.error('SQL Connection error: %s', e)
		return
