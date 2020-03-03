import googlemaps
import json
from datetime import datetime
from security import google

google_maps = googlemaps.Client(key=google.google_API)

'''
    arrival_date: has to be a datetime object
    initial_departure_place: has to be place where student lives as String (like "Postcode Place, Street")
'''


def create_time_string(time):
    time_string = time.replace("am", "").replace("pm", "")
    time_hour = int(time_string[:time_string.find(":")])
    if time_hour == 12:
        time_hour -= 12 if "am" in time else 0
    else:
        time_hour += 12 if "pm" in time else 0
    time_minute = time_string[time_string.find(":"):]
    time_string = str(time_hour) + time_minute
    return time_string


class Direction(object):
    def __init__(self, arrival_date, initial_departure_place):
        self.arrival_time = arrival_date.timestamp()

        self.directions_result = google_maps.directions(initial_departure_place,
                                                        "Erzbergerstraße 121, 76133 Karlsruhe, Germany",
                                                        mode="transit",
                                                        arrival_time=self.arrival_time)

        self.result_as_json = json.dumps(self.directions_result, indent=4)
        self.result_as_json = json.loads(self.result_as_json)

        self.trips = []
        for step in self.result_as_json[0]['legs'][0]['steps']:
            try:
                self.trips.append(step['transit_details'])
            except:
                pass

    def get_as_json(self):
        legs = []
        for trip in self.trips:
            departure = {
                "station": trip['departure_stop']['name'],
                "scheduled": trip['departure_time']['text']
            }
            arrival = {
                "scheduled": trip['arrival_time']['text'],
                "station": trip['arrival_stop']['name']
            }
            try:
                train = {
                    "name": trip['trip_short_name'],
                    "destination": trip['headsign']
                }
            except:
                try:
                    train = {
                        "name": trip['line']['short_name'],
                        "type": trip['line']['vehicle']['name'],
                        "destination": trip['headsign']
                    }
                except:
                    if trip['line']['short_name'] not in trip['headsign']:
                        train = {
                            "name": trip['line']['short_name'],
                            # "type": trip['line']['name'],
                            "destination": trip['headsign']
                        }
                    else:
                        train = {
                            "name": trip['headsign'],
                            "destination": trip['arrival_stop']['name']
                        }
            leg = {
                "departure": departure,
                "arrival": arrival,
                "train": train
            }
            legs.append(leg)

        trip_as_json = {
            "departure_time": self.trips[0]['departure_time']['text'],
            "arrival_time": self.trips[len(self.trips) - 1]['arrival_time']['text'],
            "legs": legs
        }
        return json.dumps(trip_as_json, indent=4)

    def save_json_to_file(self):
        with open("savedDirections.json", "w") as file:
            file.write(self.get_as_json())
        file.close()

    def create_message(self):
        trip_json = json.loads(self.get_as_json())
        string = "🌱 **Your ride starts at "
        string += create_time_string(trip_json['departure_time'])
        string += "**\n"
        for leg in trip_json['legs']:
            try:
                if leg['train']['type'] == "Tram":
                    string += "🚋 __"
                elif leg['train']['type'] == "Bus":
                    string += "🚌 __"
                else:
                    string += "🚅 __"
            except:
                string += "🚅 __"
            string += leg['departure']['station']
            string += " ("
            string += create_time_string(leg['departure']['scheduled'])
            string += ") → "
            string += leg['arrival']['station']
            string += " ("
            string += create_time_string(leg['arrival']['scheduled'])
            string += ") with "
            string += leg['train']['name']
            string += "__\n"
        string += "🏫 **You're at DHBW at "
        string += create_time_string(trip_json['arrival_time'])
        string += "**"
        return string
