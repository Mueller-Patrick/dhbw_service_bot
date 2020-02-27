from menu import Requests
import json
import os
import datetime
from datetime import timedelta


class Saver(object):
    def __init__(self, day):
        self.menu = Requests.Menu(day)

        if self.menu.valid:
            self.unsaved_menu = {
                "day": str(self.menu.create_date_string()),
                "menu": str(self.menu.create_string())
            }

            self.menus = []

            if not self.check_if_in_file():
                self.menus.append(self.unsaved_menu)
                with open('menu/savedMenus.json', 'w') as outfile:
                    outfile.write(json.dumps(self.menus, indent=4))
                outfile.close()

    def check_if_in_file(self):
        if os.stat("menu/savedMenus.json").st_size == 0:
            return False
        with open('menu/savedMenus.json') as infile:
            self.data = json.loads(infile.read())
        infile.close()

        for saved_menu in self.data:
            if saved_menu == self.unsaved_menu:
                return True

        for dataset in self.data:
            self.menus.append(dataset)
        return False


class Reader(object):
    def __init__(self, day):
        Saver(day)
        with open('menu/savedMenus.json', 'r') as testfile:
            data = json.loads(testfile.read())
        testfile.close()
        self.day = datetime.datetime.today() + timedelta(days=day - 1)
        self.day = self.day.date()
        self.day = str(self.day.day) + "." + str(self.day.month) + "." + str(self.day.year)
        for x in data:
            if self.day == x['day']:
                self.menu = x['menu']

    def get_menu_as_str(self):
        return self.menu

    def get_menu_as_arr(self):
        menu = str(self.menu)
        array = menu.split("%i%")

        return array

    def get_day(self):
        return self.day

'''
def check_if_in_file():
    if os.stat("menu/savedMenus.json").st_size == 0:
        return False
    with open('menu/savedMenus.json') as infile:
        data = json.loads(infile.read())
    infile.close()

    for saved_menu in data:
        if saved_menu == unsaved_menu:
            return True

    for dataset in data:
        menus.append(dataset)
    return False


menu = Requests.Menu(2)

if menu.valid:
    unsaved_menu = {
        "day": str(menu.create_date_string()),
        "menu": str(menu.create_string())
    }

    menus = []

    if not check_if_in_file():
        menus.append(unsaved_menu)
        with open('menu/savedMenus.json', 'w') as outfile:
            outfile.write(json.dumps(menus, indent=4))
        outfile.close()
'''
