import requests
import re

from datetime import datetime
from menu2.models.Dish import Dish

API_URL = 'https://openmensa.org/api/v2/canteens'
CANTEEN_ID = 33  # 33 = Mensa Erzbergerstraße

LIST_OF_WORDS_TO_REMOVE = [
	'mit',
	'den',
	'in',
	'von',
	'vom',
	'der',
	'die',
	'das',
	'im',
	'und',
	'u.',
	'-',
	';',
	',',
	'.'
]


def _remove_ingredients(text: str) -> str:
	return re.sub(
		r"\[.*\]",
		"",
		text
	)


def _make_comparable_text(text: str) -> str:
	comparable_text = ""
	comparable_words = []

	for word in text.split(" "):
		if word not in LIST_OF_WORDS_TO_REMOVE:
			comparable_words.append(word)

	comparable_words.sort()

	for idx, word in enumerate(comparable_words):
		if idx + 1 != len(comparable_words):
			comparable_text += f'{word} '
		else:
			comparable_text += word

	return comparable_text


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
		try:
			name = _remove_ingredients(meal['name'])
			comparable_name = _make_comparable_text(name)

			price = meal.get('prices', {'students': -0.01}).get('students', -0.01)
			if price is None:
				price = -0.01

			dishes.append(
				Dish(
					dish_id=meal['id'],
					date=date,
					name=name,
					comparable_name=comparable_name,
					price=int(float(price) * 100),
					category=meal['category']
				)
			)

		except Exception as e:
			raise e

	return dishes
