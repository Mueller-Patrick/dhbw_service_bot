import requests
import re

from datetime import datetime
from menu2.models.Dish import Dish

API_URL = 'https://openmensa.org/api/v2/canteens'
CANTEEN_ID = 33  # 33 = Mensa Erzbergerstraße

NUMBERS = [x for x in range(10)]

LIST_OF_WORDS_TO_REMOVE = [
	'frites',  # so "pommes frites" becomes "pommes"
	'mit',
	'den',
	'in',
	'von',
	'vom',
	'oder',
	'der',
	'die',
	'das',
	'im',
	'und',
	'u.',
	'jumbo',
	'zu',
	'art',
	'hausfrauen',
	'oma',
	'grossmutter',
	'großmutter',
	'beilage',
	'beilagen',
	'mini'
]

LIST_OF_CHARS_TO_REMOVE = [
	';',
	',',
	'.',
	'&',
	'"',
	'/',
	'\''
]
LIST_OF_CHARS_TO_REMOVE.extend(NUMBERS)

CHARS_TO_REPLACE = {
	'ü': 'ue',
	'Ăź': 'ue',
	'ö': 'oe',
	'Ä': 'AE',
	'Ü': 'UE',
	'Ö': 'OE',
	'Ă¤': 'ae',
	'ä': 'ae',
	'ĂŠ': 'e',
	'Ã©': 'e',
	'é': 'e',
	'è': 'e',
	'ê': 'e',
	'Ă': 'ss',
	'ß': 'ss',
}

WORDS_TO_REPLACE = {
	'veget': 'vegetarisch',
	'schniposa': 'schnitzel pommes salat',
	'pan': 'paniert'
}


def _remove_ingredients(text: str) -> str:
	return re.sub(
		r"\[.*\]",
		"",
		text
	)


def _make_comparable_text(text: str) -> str:
	comparable_text = ""
	comparable_words = []
	comparable_words_encoded = []

	text = text.replace('-', ' ')
	text = text.replace('`', ' ')
	text = text.replace('´', ' ')

	while '  ' in text:  # replace double space with single space
		text = text.replace('  ', ' ')

	# Remove unwanted chars
	for unwanted in LIST_OF_CHARS_TO_REMOVE:
		if unwanted in text:
			text = text.replace(unwanted, '')

	# Deletes heading spaces
	while len(text) > 0 and text[0] == ' ':
		text = text[1:]

	# Remove unwanted words
	for word in text.split(" "):
		if word not in LIST_OF_WORDS_TO_REMOVE:
			comparable_words.append(word)

	# Replace unwanted strings
	for word in comparable_words:
		encoded_word = word

		for unwanted_key in CHARS_TO_REPLACE.keys():
			if unwanted_key in encoded_word:
				encoded_word = encoded_word.replace(unwanted_key, CHARS_TO_REPLACE.get(unwanted_key))

		for replace_key in WORDS_TO_REPLACE.keys():
			if replace_key.lower() == encoded_word.lower():
				encoded_word = WORDS_TO_REPLACE.get(replace_key)

		comparable_words_encoded.extend(encoded_word.split(' '))

	# convert to lowercase
	comparable_words_encoded = map(lambda x: x.lower(), comparable_words_encoded)

	# Converting to set to get rid of duplicates, then converting back to list to sort it
	comparable_words_encoded = set(comparable_words_encoded)
	comparable_words_encoded = list(comparable_words_encoded)
	comparable_words_encoded.sort()

	# For some reason, sometimes the list contains empty shit which then causes weird stuff to happen
	if '' in comparable_words_encoded:
		comparable_words_encoded.remove('')

	for idx, word in enumerate(comparable_words):
		if idx + 1 != len(comparable_words):
			comparable_text += f'{word} '
		else:
			comparable_text += word

	if len(comparable_text) < 1:
		raise ValueError('comparable_text is not a valid name')

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
