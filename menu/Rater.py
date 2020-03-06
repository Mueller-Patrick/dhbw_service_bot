import datetime

from menu import MenuSaver
from menu import Utility as Util

food_path = "menu/savedFoods.json"


class Rater(object):
    def __init__(self, name, user_rating):
        """
        @param name: name of food
        @param user_rating: rating by user
        """
        self.name = name
        self.user_rating = user_rating
        self.today = datetime.datetime.today().strftime("%Y-%m-%d")

        data = Util.load_data(food_path)
        for dataset in data:
            if Util.similar(dataset["name"], self.name) >= 0.8:
                if self.today in dataset["was_available_on"]:
                    rating = dataset["rating"]
                    amount_of_ratings = dataset["amount_of_ratings"]
                    self.new_amount_of_ratings = amount_of_ratings + 1
                    self.new_rating = ((rating * amount_of_ratings) + self.user_rating) / self.new_amount_of_ratings
                    data[data.index(dataset)]["rating"] = self.new_rating
                    data[data.index(dataset)]["amount_of_ratings"] = self.new_amount_of_ratings
                    Util.save_data(food_path, data)
                    break
