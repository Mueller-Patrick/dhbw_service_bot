"""
 Request class, used to perform the requests http requests for the daily menu etc.
"""

# IMPORTS
import datetime
import re
from datetime import timedelta
from requests_html import HTMLSession

# STARTUP
day = 1  # 1 equals today, 2 equals tomorrow, etc.
today = datetime.datetime.today()
if (today.weekday() + day) > 5:
    print("Datum außerhalb des möglichen Bereiches! (max. die aktuelle Woche)")
    exit()
session = HTMLSession()
resp = session.get("https://www.sw-ka.de/de/essen/")
table = resp.html.find("#fragment-c3-" + str(day), first=True)
day = today + timedelta(days=day - 1)
day = day.date()


# CREATION OF STRING
def create_string(menu):
    string = ""
    return_string = "Am " + str(day.day) + "." + str(day.month) + "." + str(
        day.year) + " gibt es folgendes zum Essen: \n\n"
    y = 0
    remove_first = 0
    remove_second = 0
    for x in range(len(menu)):
        if menu[x] == '[':
            remove_first = x

        if menu[x] == ']':
            remove_second = x + 1

        if menu[x] == '€':
            if len(menu[y:x + 1]) > 10:
                if remove_first != 0 and remove_second != 0:
                    string += (menu[y:remove_first] + menu[remove_second:x + 1])
                else:
                    string += (menu[y:x + 1])
            y = x + 1
            remove_first = 0
            remove_second = 0

    x = 0
    for i in range(1, 4):
        return_string += string[string.find("Wahlessen " + str(i)):string.find("Wahlessen " + (str(i + 1)))] + "\n"
    return re.sub("\n\n+", "\n\n", return_string)


# OUTPUT
final_string = create_string(table.text)
print(final_string)
