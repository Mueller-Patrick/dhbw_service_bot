class Dish:
	dish_id: int
	name: str
	rating: float
	price: int

	def __init__(self, name):
		self.name = name
