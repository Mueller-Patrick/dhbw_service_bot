import requests

from datetime import datetime
from menu2.models.Dish import Dish
from menu2.models.Menu import Menu

API_URL = 'https://openmensa.org/api/v2/canteens'
CANTEEN_ID = 33  # 33 = Mensa Erzbergerstraße


class WebCrawler(object):
	def __init__(self, date=datetime.now().strftime('%Y-%m-%d')):
		"""
		This class is responsible for crawling the API of the Mensa.
		It takes a date to check which dishes are available for this date. (e.g. 2021-12-31)
		"""
		self.date = date
		meals_url = f'{API_URL}/{CANTEEN_ID}/days/{self.date}/meals'
		self.meals = requests.get(meals_url).json()

	def get_menu(self):
		"""
		This method returns the menu consisting of all dishes for the date provided in constructor.
		"""
		meals = self.meals

		meal1 = list(filter(lambda meal: meal['category'] == 'Wahlessen 1', meals))[0]
		meal2 = list(filter(lambda meal: meal['category'] == 'Wahlessen 2', meals))[0]

		dish1 = Dish(
			dish_id=meal1['id'],
			name=meal1['name'],
			price=(meal1['prices']['students'] * 100)
		)
		dish2 = Dish(
			dish_id=meal2['id'],
			name=meal2['name'],
			price=(meal2['prices']['students'] * 100)
		)

		menu = Menu(
			date=self.date,
			dish1=dish1,
			dish2=dish2
		)

		return menu
