import googlemaps
import json
from datetime import datetime
import os

google_maps = googlemaps.Client(key=os.environ.get('GOOGLE_API_TOKEN'))

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
    def __init__(self, date: datetime, place: str, return_journey=False, is_departure_time=False):
        """
        @param date: return_journey==True -> time of end of last lecture; else -> time of start of first lecture
        @param place: home of student
        @param return_journey: boolean whether its the return journey or not
        """
        self.date = date
        self.arrival_time = date.timestamp()
        print(("Arrival time: {}").format(self.arrival_time))

        if return_journey:
            self.directions_result = google_maps.directions("Erzbergerstraße 121, 76133 Karlsruhe, Germany",
                                                            place,
                                                            mode="transit",
                                                            departure_time=self.date)
        else:
            if is_departure_time:
                self.directions_result = google_maps.directions(place,
                                                                "Erzbergerstraße 121, 76133 Karlsruhe, Germany",
                                                                mode="transit",
                                                                departure_time=self.arrival_time)
            else:
                self.directions_result = google_maps.directions(place,
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
        string = "🌱 <b>Your ride starts at "
        string += create_time_string(trip_json['departure_time'])
        string += "</b>\n"
        for leg in trip_json['legs']:
            try:
                if leg['train']['type'] == "Tram":
                    string += "🚋 <i>"
                elif leg['train']['type'] == "Bus":
                    string += "🚌 <i>"
                else:
                    string += "🚅 <i>"
            except:
                string += "🚅 <i>"
            string += leg['departure']['station']
            string += " ("
            string += create_time_string(leg['departure']['scheduled'])
            string += ") → "
            string += leg['arrival']['station']
            string += " ("
            string += create_time_string(leg['arrival']['scheduled'])
            string += ") with "
            string += leg['train']['name']
            string += "</i>\n"
        string += "🏫 <b>You reach your target at "
        string += create_time_string(trip_json['arrival_time'])
        string += "</b>"
        return string
