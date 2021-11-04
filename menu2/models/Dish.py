from datetime import datetime


class Dish:
	dish_id: int
	date: datetime
	name: str
	comparable_name: str
	rating: float
	price: int  # cent
	category: str

	def __init__(self, dish_id, date, name, comparable_name, price, category, rating=0):
		self.dish_id = int(dish_id)
		self.date = date
		self.name = name
		self.comparable_name = comparable_name
		self.price = price
		self.category = category
		self.rating = rating

	def get_formatted_dish(self, category_index):

		food_emoji = {
			0: '🥘',
			1: '🍲',
			2: '🥗'
		}

		price_emoji = {
			0: '💳',
			1: '💰',
			2: '💵'
		}

		ret_str = f'<b>{food_emoji[category_index]} {self.name} </b>\n'
		price = round(int(self.price) / 100, 2)

		if price >= 3:
			price_index = 0
		elif price >= 1:
			price_index = 1
		else:
			price_index = 2

		ret_str += '<i>{} {:0.2f} € - '.format(price_emoji[price_index], price)

		if self.rating is None:
			ret_str += 'Not rated yet'
		else:
			ret_str += '' + str(round(self.rating, 1)) + ' ⭐'

		ret_str += '</i>\n'
		return ret_str
