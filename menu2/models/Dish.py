class Dish:
	dish_id: int
	name: str
	total_stars: int
	amount_of_ratings: int

	def __init__(self, name):
		self.name = name
