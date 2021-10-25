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
	# save_to_sql(conn, menu)
	add_rating_to_dish(conn, 42, 1, 5)
