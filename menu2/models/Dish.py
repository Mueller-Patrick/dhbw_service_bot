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
