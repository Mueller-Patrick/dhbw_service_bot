import requests
import re

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
	# print(meals_url)
	dishes = []

	for meal in meals:
		try:
			name = re.sub(
				r"\[.*\]",
				"",
				meal['name']
			)

			price = meal.get('prices', {'students': -0.01}).get('students', -0.01)
			if price is None:
				price = -0.01

			dishes.append(
				Dish(
					dish_id=meal['id'],
					date=date,
					name=name,
					price=int(float(price) * 100),
					category=meal['category']
				)
			)
		except Exception as e:
			raise e

	return dishes
