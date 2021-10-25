class Dish:
	dish_id: int
	name: str
	rating: float
	price: int

	def __init__(self, dish_id, name, price, rating=0):
		self.dish_id = int(dish_id)
		self.name = name
		self.price = price
		self.rating = rating
