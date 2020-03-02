import googlemaps
import time
import json
from datetime import datetime
from security import google

google_maps = googlemaps.Client(key=google.google_API)

'''
    arrival_date: has to be a datetime object
    initial_departure_place: has to be place where student lives as String (like "Postcode Place, Street")
'''


class Direction(object):
    def __init__(self, arrival_date, initial_departure_place):
        self.arrival_time = arrival_date.timestamp()

        self.directions_result = google_maps.directions("77815 Bühl Weitenung, Germany",
                                                        "Erzbergerstraße 121, 76133 Karlsruhe, Germany",
                                                        mode="transit",
                                                        arrival_time=arrival_time)

        self.result_as_json = json.dumps(self.directions_result, indent=4)
        self.result_as_json = json.loads(self.result_as_json)

        trips = []
        for step in self.result_as_json[0]['legs'][0]['steps']:
            try:
                trips.append(step['transit_details'])
            except:
                0

        legs = []
        for trip in trips:
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
                if trip['line']['short_name'] not in trip['headsign']:
                    train = {
                        "name": trip['line']['short_name'],
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

        self.trip_as_json = {
            "now": trips[0]['departure_time']['text'],
            "legs": legs
        }

    def get_as_json(self):
        return json.dumps(self.trip_as_json, indent=4)
