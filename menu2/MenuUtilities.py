"""
Contains utility functions for saving / retrieving menus from / to SQL
"""
from menu2.models import Menu, Dish
from sql import SQLConnectionHandler as sqlhandler


def save_to_sql(menu: Menu):
	conn = sqlhandler.getvServerConnection()
	cur = conn.cursor()

	dish_tuples = []
	dish_ids = []

	dish_tuples.append((menu.dish1.name))
	dish_tuples.append((menu.dish2.name))
	dish_tuples.append((menu.dish3.name))

	stmt = 'INSERT INTO dishes (name) VALUES (%s) RETURNING dish_id'

	for i in range(3):
		cur.execute(stmt, dish_tuples[i])
		dish_ids.append(cur.fetchone()[0])

	menu_tuple = (menu.date, dish_ids[0], dish_ids[1], dish_ids[2])

	menu_success = cur.execute('INSERT INTO menus (date, dish1, dish2, dish3) VALUES (%s, %s, %s, %s)', menu_tuple)

	if menu_success:
		conn.commit()
	else:
		conn.rollback()

	cur.close()
	conn.close()


def add_rating_to_dish(dish_id: int, stars: int):
	pass


def get_all_from_sql() -> [Menu]:
	pass


def get_menu_from_sql_by_date(date: str) -> Menu:
	pass


def __test():
	dish1 = Dish.Dish('Test1')
	dish2 = Dish.Dish('Test2')
	dish3 = Dish.Dish('Test3')
	menu = Menu.Menu('2021-10-25', dish1, dish2, dish3)
	save_to_sql(menu)
