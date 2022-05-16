#!/usr/bin/python3

import json, os
from datetime import datetime
from urllib.request import urlopen

YAHOO_API_ENDPOINT = 'https://dfyql-ro.sports.yahoo.com/v2/external/playersFeed/nhl'

def fetch_data():
    jsonurl = urlopen(YAHOO_API_ENDPOINT)
    data = json.loads(jsonurl.read())
    return data

def retrieve_date(data):
    timestamp = data['currentTime'] / 1000 # Yahoo lists in ms, datetime uses seconds
    return datetime.fromtimestamp(timestamp).strftime('%Y%m%dT%H%M%S')

def write_data(data, date):
    print(date)
    if not os.path.exists('./rawdata'):
        os.makedirs('./rawdata')
    with open('./rawdata/' + date + '.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def main():
    data = fetch_data()
    date = retrieve_date(data)
    write_data(data, date)

if __name__ == "__main__":
    main()
