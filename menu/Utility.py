import json

from difflib import SequenceMatcher


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def load_data(path):
    with open(path) as infile:
        data = json.loads(infile.read())
    infile.close()
    return data


def save_data(path, data):
    with open(path, 'w') as outfile:
        outfile.write(json.dumps(data, indent=4))
    outfile.close()
