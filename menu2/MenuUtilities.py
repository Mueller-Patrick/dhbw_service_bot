"""
Contains utility functions for saving / retrieving menus from / to SQL
"""
from datetime import datetime, timedelta
import json

import pymysql

from menu2 import WebCrawler
from menu2.models import Dish
from sql import SQLConnectionHandler as sqlhandler


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
		'	dish_id = VALUES(dish_id);'
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


def get_dishes_from_sql_by_date(conn: pymysql.Connection, date: str):
	"""
	Returns the dishes for the given day containing all relevant information like the rating
	:param conn: The pymysql connection
	:param date: The date in the format yyyy-MM-dd to return the menu for
	:return: The menu
	"""
	cur = conn.cursor()

	dish_stmt = \
		'SELECT d.dish_id, da.available_date, d.name, da.price, da.category FROM dish_availability da ' \
		'LEFT OUTER JOIN dishes d ON da.dish = d.dish_id ' \
		'WHERE da.available_date = %s ' \
		'ORDER BY da.category'
	rating_stmt = 'SELECT dish_id, stars FROM dish_ratings WHERE dish_id IN %s'

	cur.execute(dish_stmt, date)
	dishes = cur.fetchall()

	dish_ids = []
	for dish in dishes:
		dish_ids.append(dish[0])

	cur.execute(rating_stmt, (list(dish_ids),))
	ratings = cur.fetchall()

	rating_map = dict()

	# Map ratings so we can access the list of all ratings by dish id
	for rating in ratings:
		dish_id = rating[0]
		stars = rating[1]

		if dish_id in rating_map.keys():
			rating_map[dish_id].append(stars)
		else:
			rating_map[dish_id] = [stars]

	return_dishes = []

	for dish in dishes:
		dish_id = dish[0]
		available_date = dish[1]
		name = dish[2]
		price = dish[3]
		category = dish[4]
		if dish_id in rating_map.keys():
			ratings = rating_map[dish_id]
			calculated_rating = sum(ratings) / len(ratings)
		else:
			calculated_rating = -1

		dish_obj = Dish.Dish(dish_id, available_date, name, '', price, category, calculated_rating)

		return_dishes.append(dish_obj)

	return return_dishes


def __test():
	conn = sqlhandler.getvServerConnection()

	date = datetime.strptime('2019-10-01', '%Y-%m-%d')

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


if __name__ == '__main__':
	__test()
