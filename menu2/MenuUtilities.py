"""
Contains utility functions for saving / retrieving menus from / to SQL
"""
import pymysql

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
	dish_ids = []

	dish_tuples.append((menu.dish1.name, menu.dish1.price))
	dish_tuples.append((menu.dish2.name, menu.dish2.price))
	dish_tuples.append((menu.dish3.name, menu.dish3.price))

	stmt = 'INSERT INTO dishes (name, price) VALUES (%s, %s) RETURNING dish_id'

	for i in range(3):
		cur.execute(stmt, dish_tuples[i])
		dish_ids.append(cur.fetchone()[0])

	menu_tuple = (menu.date, dish_ids[0], dish_ids[1], dish_ids[2])

	menu_success = cur.execute('INSERT INTO menus (date, dish1, dish2, dish3) VALUES (%s, %s, %s, %s)', menu_tuple)

	if menu_success:
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
	pass

def get_menu_from_sql_by_date(conn: pymysql.Connection, date: str) -> Menu:
	"""
	Returns the menu for the given day containing all information about the dishes of the menu
	:param conn: The pymysql connection
	:param date: The date in the format yyyy-MM-dd to return the menu for
	:return: The menu
	"""
	pass


def __test():
	conn = sqlhandler.getvServerConnection()

	dish1 = Dish.Dish('Test1')
	dish2 = Dish.Dish('Test2')
	dish3 = Dish.Dish('Test3')
	menu = Menu.Menu('2021-10-25', dish1, dish2, dish3)
	#save_to_sql(conn, menu)
	add_rating_to_dish(conn, 42, 1, 5)
