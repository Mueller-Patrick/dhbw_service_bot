"""
Contains utility functions for saving / retrieving menus from / to SQL
"""
from datetime import datetime, timedelta
import json

import pymysql

from menu2 import WebCrawler
from menu2.models import Dish
from sql import SQLConnectionHandler as sqlhandler
from push import PushHandler as ph


def save_dishes_to_sql(conn: pymysql.Connection, dishes: [Dish]):
	"""
	Saves the given dishes to the database
	:param conn: The pymysql connection
	:param dishes: The dishes to be saved
	"""
	if len(dishes) < 1:
		return

	cur = conn.cursor()

	dish_tuples = []
	dish_availability_tuples = []

	for dish in dishes:
		if len([item for item in dish_tuples if item[1] == dish.name]) > 0:
			continue
		dish_tuples.append((dish.dish_id, dish.name, dish.comparable_name))
		dish_availability_tuples.append((dish.dish_id, dish.date, dish.price, dish.category))

	insert_dish = \
		'INSERT INTO dishes (dish_id, name, comparable_name) ' \
		'VALUES (%s, %s, %s) ' \
		'ON DUPLICATE KEY UPDATE ' \
		'	dish_id = VALUES(dish_id),' \
		'	name = VALUES(name)'  # TODO fix (421 rows expected)
	insert_dish_availability = \
		'INSERT INTO dish_availability (dish, available_date, price, category) VALUES (%s, %s, %s, %s)'

	dishes_success = cur.executemany(insert_dish, dish_tuples)
	dish_availabilities_success = cur.executemany(insert_dish_availability, dish_availability_tuples)

	if dishes_success and dish_availabilities_success:
		conn.commit()
	else:
		conn.rollback()
		raise Exception('Error saving menu to database')

	cur.close()


def add_rating_to_dish(conn: pymysql.Connection, dish_id: int, user_id, stars: int):
	"""
	Adds a rating to the given dish
	:param conn: The pymysql connection
	:param dish_id: The id of the rated dish
	:param user_id: The id of the rating user
	:param stars: The amount of stars the user gave the dish
	"""
	cur = conn.cursor()

	insert_stmt = 'INSERT INTO dish_ratings (dish_id, user_id, stars) VALUES (%s, %s, %s)'

	cur.execute(insert_stmt, (dish_id, user_id, stars))

	conn.commit()

	cur.close()


def get_dishes_from_sql_by_date(conn: pymysql.Connection, date: str) -> {}:
	"""
	Fetches the dishes for the given date and returns them as a dict.
	The key is the category (e.g. Wahlessen 1) and the values are the contained dishes
	@param conn: The pymysql connection
	@param date: The date to fetch the dishes for
	@return: The dishes for that day
	"""
	cur = conn.cursor()

	dish_stmt = 'SELECT d.dish_id, d.name, d.comparable_name, da.category, da.price, da.available_date, AVG(dr.stars) ' \
				'FROM dishes d ' \
				'LEFT OUTER JOIN dish_availability da ON d.dish_id = da.dish ' \
				'LEFT OUTER JOIN dish_ratings dr ON d.dish_id = dr.dish_id ' \
				'WHERE da.available_date = %s ' \
				'GROUP BY d.dish_id, da.category, da.price ' \
				'ORDER BY da.category, da.price DESC'

	cur.execute(dish_stmt, date)
	dishes = cur.fetchall()

	cur.close()

	return_dishes = {}

	for dish in dishes:
		dish_obj = Dish.Dish(
			dish_id=dish[0],
			name=dish[1],
			comparable_name=dish[2],
			category=dish[3],
			price=dish[4],
			date=dish[5],
			rating=dish[6]
		)

		try:
			return_dishes[dish_obj.category].append(dish_obj)
		except KeyError:
			return_dishes[dish_obj.category] = [dish_obj]

	return return_dishes


def get_formatted_dishes(conn: pymysql.Connection, date: str, dishes=None):
	"""
	Fetches the dishes for the given date and returns them formatted in a fancy manner
	@param conn: The pymysql connection
	@param date: The date to fetch the dishes for
	@param dishes: Optionally provide a list of dishes that will be formatted instead of fetching the dishes from sql
	@return: The formatted string. Markup is HTML.
	"""
	if dishes is None:
		dishes = get_dishes_from_sql_by_date(conn, date)


	if len(dishes.values()) < 1:
		return 'No menu available for that day'

	ret_str = ''

	categories = dishes.keys()
	categories = sorted(categories)

	for categ_idx, category in enumerate(categories):
		categ_dishes = dishes.get(category)

		ret_str += '<u>' + category + '</u>\n'
		for dish_idx, dish in enumerate(categ_dishes):
			ret_str += dish.get_formatted_dish(categ_idx)
			if dish_idx != len(categ_dishes)-1:
				ret_str += '------\n'

		ret_str += '\n'

	print(ret_str)
	return ret_str


def __test():
	conn = sqlhandler.getvServerConnection()

	date = datetime.strptime('2012-10-01', '%Y-%m-%d')

	while date <= datetime.now():
		successful = False
		try:
			dishes = WebCrawler.get_dishes(date.strftime('%Y-%m-%d'))
			save_dishes_to_sql(conn, dishes)
			successful = True
		except json.decoder.JSONDecodeError as e:
			pass
		except IndexError as e:
			pass
		except ValueError as e:
			pass
		finally:
			print(f'Date {date} {"successful" if successful else "not successful"}')
			date = date + timedelta(days=1)


def __test_push():
	bot = ph.configure_telegram()
	conn = sqlhandler.getvServerConnection()

	# ph.sendMenuRatingPushes(conn, bot, '14:30')
	ph.sendMenuRatingPushes(conn, bot, '14:30')


if __name__ == '__main__':
	conn = sqlhandler.getvServerConnection()

	#print(get_formatted_dishes(conn, '2021-11-04'))
	__test_push()
