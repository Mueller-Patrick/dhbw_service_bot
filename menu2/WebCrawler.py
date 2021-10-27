import requests

from datetime import datetime
from menu2.models.Dish import Dish

API_URL = 'https://openmensa.org/api/v2/canteens'
CANTEEN_ID = 33  # 33 = Mensa Erzbergerstraße


def get_dishes(date=datetime.now().strftime('%Y-%m-%d')) -> [Dish]:
	"""
	This class is responsible for crawling the API of the Mensa.
	It takes a date to check which dishes are available for this date. (e.g. 2021-12-31)

	This method returns the menu consisting of all dishes for the date provided in constructor.
	"""
	meals_url = f'{API_URL}/{CANTEEN_ID}/days/{date}/meals'
	meals = requests.get(meals_url).json()

	dishes = []

	for meal in meals:
		dishes.append(
			Dish(
				dish_id=meal['id'],
				date=date,
				name=meal['name'],
				price=int(float(meal['prices']['students']) * 100),
				category=meal['category']
			)
		)

	return dishes
