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
            print("Datum außerhalb des möglichen Bereiches! (max. die aktuelle Woche)")
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
        return str(self.day.day) + "." + str(self.day.month) + "." + str(self.day.year)

    def create_string(self):
        string = ""
        return_string = "Am " + self.create_date_string() + " gibt es folgendes zum Essen: \n\n"
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
        for i in range(1, 4):
            return_string += "%i%"
            return_string += string[string.find("Wahlessen " + str(i)):string.find("Wahlessen " + (str(i + 1)))] + "\n"
        return re.sub("\n\n+", "\n\n", return_string)
