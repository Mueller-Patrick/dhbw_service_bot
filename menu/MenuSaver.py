import json
import os
import datetime

from menu import Requests
from menu import Utility as Util
from datetime import timedelta


def foods_to_json(food_array):
    foods = []
    for food_name in food_array:
        food = {
            "name": food_name,
            "rating": 0,
            "amount_of_ratings": 0,
            "was_available_on": str(datetime.datetime.today().strftime("%Y-%m-%d"))
        }
        foods.append(food)
    return foods


def check_if_in_file(path, unsaved_json):
    if not check_if_path_exists(path):
        return False
    data = Util.load_data(path)

    for saved_json in data:
        if saved_json == unsaved_json:
            return True

    return False


def check_if_key_in_file(path, unsaved_json, json_key):
    if not check_if_path_exists(path):
        return False
    data = Util.load_data(path)

    for saved_json in data:
        if Util.similar(saved_json[json_key], unsaved_json[json_key]) >= 0.8:
            return True

    return False


def check_if_path_exists(path):
    if not os.path.exists(path) or os.stat(path).st_size == 0:
        return False
    return True


def increment_array_in_json(food, path, compare_key, increment_key):
    """
    @param food: food, where an array is being incremented
    @param path: path to .json file
    @param compare_key: key to find food in list
    @param increment_key: key to array to increment

    This method automatically saves data with incremented array
    """

    dates = [food['was_available_on']]
    data = Util.load_data(path)
    for dataset in data:
        if Util.similar(dataset[compare_key], food[compare_key]) >= 0.8:
            if isinstance(dataset[increment_key], list):
                for date in dataset[increment_key]:
                    if date not in dates:
                        dates.append(date)
            data[data.index(dataset)][increment_key] = dates
            Util.save_data(path, data)


class Saver(object):
    def __init__(self, day):
        self.menu = Requests.Menu(day)

        if self.menu.valid:
            # Save new foods
            self.unsaved_foods = foods_to_json(self.menu.create_foods())

            self.foods = []

            food_path = "menu/savedFoods.json"
            for food in self.unsaved_foods:
                if not check_if_key_in_file(food_path, food, "name"):
                    self.foods.append(food)
                else:
                    increment_array_in_json(food, food_path, 'name', 'was_available_on')

            if check_if_path_exists(food_path):
                data = Util.load_data(food_path)

                for dataset in data:
                    self.foods.append(dataset)

            Util.save_data(food_path, self.foods)

            # Save new menu
            self.unsaved_menu = {
                "day": str(self.menu.create_date_string()),
                "menu": str(self.menu.create_string())
            }

            self.menus = []

            menu_path = "menu/savedMenus.json"
            if not check_if_in_file(menu_path, self.unsaved_menu):
                if check_if_path_exists(menu_path):
                    data = Util.load_data(menu_path)
                    for dataset in data:
                        self.menus.append(dataset)

                self.menus.append(self.unsaved_menu)

                Util.save_data(menu_path, self.menus)


def get_foods_as_arr():
    foods = Util.load_data("menu/savedFoods.json")
    return foods


class Reader(object):
    def __init__(self, day):
        Saver(day)
        data = Util.load_data("menu/savedMenus.json")
        self.day = datetime.datetime.today() + timedelta(days=day - 1)
        self.day = self.day.strftime("%Y-%m-%d")
        for x in data:
            if self.day == x['day']:
                self.menu = x['menu']

    def get_food_with_ratings_as_string_array(self):
        data = Util.load_data("menu/savedFoods.json")
        date = self.day
        array = []
        for dataset in data:
            if date in dataset["was_available_on"]:
                string = str(dataset["name"]) + " [" + "%.2f" % dataset["rating"] + "⭐]"
                array.append(string)

        return array

    def get_menu_as_str(self):
        return self.menu

    def get_menu_as_arr(self):
        menu = str(self.menu)
        array = menu.split("%i%")
        return array

    def get_day(self):
        return self.day
