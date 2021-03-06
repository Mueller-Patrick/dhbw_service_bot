"""
 Request class, used to perform the requests http requests for the daily menu etc.
"""

# IMPORTS
import datetime
import re
from datetime import timedelta
from requests_html import HTMLSession


class Menu(object):
    def __init__(self, day):
        self.valid = True
        if not self.check_if_valid(day):
            self.valid = False

        if self.valid:
            self.create_session(day)

    def create_session(self, day):
        self.session = HTMLSession()
        self.resp = self.session.get("https://www.sw-ka.de/de/essen/")
        self.menu = self.resp.html.find("#fragment-c3-" + str(day), first=True).text

        self.day = datetime.datetime.today() + timedelta(days=day - 1)
        self.day = self.day.date()

    def check_if_valid(self, day):
        self.day = day
        self.today = datetime.datetime.today()
        return (self.today.weekday() + self.day) <= 5

    def create_date_string(self):
        return self.day.strftime("%Y-%m-%d")

    def create_string(self):
        string = ""
        return_string = ""
        y = 0
        remove_first = 0
        remove_second = 0
        for x in range(len(self.menu)):
            if self.menu[x] == '[':
                remove_first = x

            if self.menu[x] == ']':
                remove_second = x + 1

            if self.menu[x] == '€':
                if len(self.menu[y:x + 1]) > 10:
                    if remove_first != 0 and remove_second != 0:
                        string += (self.menu[y:remove_first] + self.menu[remove_second:x + 1])
                    else:
                        string += (self.menu[y:x + 1])
                y = x + 1
                remove_first = 0
                remove_second = 0

        x = 0
        for i in range(1, 4):  # Wahlessen 1 - 3
            return_string += "_"
            return_string += string[string.find("Wahlessen " + str(i)):string.find("Wahlessen " + (str(i + 1)))] + "\n"
            return_string = return_string.replace("Wahlessen " + str(i), "Wahlessen " + str(i) + "_")
            return_string += "%i%"
        return_string = return_string[:-5]
        return_string = re.sub("\n", "*\n", return_string)
        return_string = return_string.replace("*\n*\n*\n", "\n\n")
        return_string = return_string.replace("*\n*\n", "\n\n")
        return re.sub("\n\n+", "\n\n*", return_string).replace("*%i%", "%i%")

    def create_foods(self):
        menu_string = self.create_string()
        foods = []
        while menu_string.find("Wahlessen") != -1:
            start = menu_string.find("Wahlessen")
            menu_string = menu_string[start:]
            start = menu_string.find("*") + 1
            menu_string = menu_string[start:]
            end = menu_string.find("*")
            foods.append(menu_string[:end])
            menu_string = menu_string[end + 1:]
        return foods
