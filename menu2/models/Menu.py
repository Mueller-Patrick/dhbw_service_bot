from ..models import Dish


class Menu:
	date: str  # yyyy-MM-dd
	dish1: Dish
	dish2: Dish
	dish3: Dish

	def __init__(self, date, dish1=None, dish2=None, dish3=None):
		self.date = date
		self.dish1 = dish1
		self.dish2 = dish2
		self.dish3 = dish3
