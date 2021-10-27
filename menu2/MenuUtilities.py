"""
Contains utility functions for saving / retrieving menus from / to SQL
"""
from datetime import datetime, timedelta
import json

import pymysql

from menu2 import WebCrawler
from menu2.models import Menu, Dish
from sql import SQLConnectionHandler as sqlhandler


def save_to_sql(conn: pymysql.Connection, menu: Menu):
	"""
	Saves the given menu to the database
	:param conn: The pymysql connection
	:param menu: The menu to be saved
	"""
	cur = conn.cursor()

	dish_tuples = []
	amount_of_dishes = 1

	dish_tuples.append((menu.dish1.dish_id, menu.dish1.name, menu.dish1.price))
	if menu.dish2 is not None:
		dish_tuples.append((menu.dish2.dish_id, menu.dish2.name, menu.dish2.price))
		amount_of_dishes = 2
	if menu.dish3 is not None:
		dish_tuples.append((menu.dish3.dish_id, menu.dish3.name, menu.dish3.price))
		amount_of_dishes = 3

	stmt = 'INSERT INTO dishes (dish_id, name, price) VALUES (%s, %s, %s)'

	cur.executemany(stmt, dish_tuples)

	if amount_of_dishes == 3:
		menu_tuple = (menu.date, menu.dish1.dish_id, menu.dish2.dish_id, menu.dish3.dish_id)
		menu_success = cur.execute('INSERT INTO menus (date, dish1, dish2, dish3) VALUES (%s, %s, %s, %s)', menu_tuple)
	elif amount_of_dishes == 2:
		menu_tuple = (menu.date, menu.dish1.dish_id, menu.dish2.dish_id)
		menu_success = cur.execute('INSERT INTO menus (date, dish1, dish2) VALUES (%s, %s, %s)', menu_tuple)
	else:
		menu_tuple = (menu.date, menu.dish1.dish_id)
		menu_success = cur.execute('INSERT INTO menus (date, dish1) VALUES (%s, %s)', menu_tuple)

	if menu_success:
		conn.commit()
	else:
		conn.rollback()
		raise Exception('Error saving menu to database')

	cur.close()
	conn.close()


def save_dishes_to_sql(conn: pymysql.Connection, dishes: [Dish]):
	"""
	Saves the given menu to the database
	:param conn: The pymysql connection
	:param menu: The menu to be saved
	"""
	cur = conn.cursor()

	dish_tuples = []
	dish_availability_tuples = []

	for dish in dishes:
		dish_tuples.append((dish.dish_id, dish.name))
		dish_availability_tuples.append((dish.dish_id, dish.date, dish.price, dish.category))

	insert_dish = 'INSERT INTO dishes (dish_id, name) VALUES (%s, %s)'
	insert_dish_availability = \
		'INSERT INTO dish_availability (dish, available_date, price, category) VALUES (%s, %s, %s, %s)'

	dishes_success = cur.executemany(insert_dish, dish_tuples)
	dish_availabilities_success = cur.executemany(insert_dish_availability, dish_tuples)

	if dishes_success and dish_availabilities_success:
		conn.commit()
	else:
		conn.rollback()
		raise Exception('Error saving menu to database')

	cur.close()
	conn.close()


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


def get_all_dishes_from_sql(conn: pymysql.Connection) -> [Dish]:
	"""
	Fetches and returns all known dishes from the database
	:param conn: The pymysql connection
	:return: The list of dishes
	"""
	cur = conn.cursor()


# this method has high risk of duplicating code from the method below, try preventing that if possible


def get_menu_from_sql_by_date(conn: pymysql.Connection, date: str) -> Menu:
	"""
	Returns the menu for the given day containing all information about the dishes of the menu
	:param conn: The pymysql connection
	:param date: The date in the format yyyy-MM-dd to return the menu for
	:return: The menu
	"""
	cur = conn.cursor()

	menu_stmt = 'SELECT dish1, dish2, dish3 FROM menus WHERE date = %s'
	dish_stmt = 'SELECT dish_id, name, price FROM dishes WHERE dish_id IN %s'
	rating_stmt = 'SELECT dish_id, stars FROM dish_ratings WHERE dish_id IN %s'

	cur.execute(menu_stmt, date)
	menu = cur.fetchone()

	# No menu in database for the given date
	if len(menu) < 1:
		return Menu.Menu(date, None, None, None)

	cur.execute(dish_stmt, (list(menu),))
	dishes = cur.fetchall()

	cur.execute(rating_stmt, (list(menu),))
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

	return_menu = Menu.Menu(date)

	for dish_idx in range(len(dishes)):
		dish = dishes[dish_idx]
		dish_id = dish[0]
		name = dish[1]
		price = dish[2]
		if dish_id in rating_map.keys():
			ratings = rating_map[dish_id]
			calculated_rating = sum(ratings) / len(ratings)
		else:
			calculated_rating = -1

		dish_obj = Dish.Dish(dish_id, name, price, calculated_rating)

		if dish_idx == 0:
			return_menu.dish1 = dish_obj
		elif dish_idx == 1:
			return_menu.dish2 = dish_obj
		else:
			return_menu.dish3 = dish_obj

	return return_menu


def are_dishes_equal(dish1, dish2) -> bool:
	"""
	Checks the given dishes for equality and returns True if they are the same dish.
	:param dish1: The first dish to compare
	:param dish2: The second dish to compare
	:return: If the two dishes are equal
	"""
	pass


def __test():
	conn = sqlhandler.getvServerConnection()

	# dish1 = Dish.Dish('Test1')
	# dish2 = Dish.Dish('Test2')
	# dish3 = Dish.Dish('Test3')
	# menu = Menu.Menu('2021-10-25', dish1, dish2, dish3)
	# save_to_sql(conn, menu)
	# add_rating_to_dish(conn, 42, 1, 5)
	# get_menu_from_sql_by_date(conn, '2021-10-26')

	date = datetime.strptime('2019-10-01', '%Y-%m-%d')

	while date < datetime.now():
		try:
			dishes = WebCrawler.get_dishes(date.strftime('%Y-%m-%d'))
			save_to_sql(conn, dishes)
		except json.decoder.JSONDecodeError as e:
			print(f'No stuff today: {e}')
		except IndexError as e:
			print(f'No stuff today: {e}')
		finally:
			date = date + timedelta(days=1)


if __name__ == '__main__':
	__test()
