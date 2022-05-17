#!/usr/bin/python3

import json, os, sys
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
    if not os.path.exists('./rawdata'):
        os.makedirs('./rawdata')
    with open('./rawdata/' + date + '.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def print_data(data):
    json.dump(data, sys.stdout, indent=4)

def main():
    data = fetch_data()
    date = retrieve_date(data)
    if len(sys.argv) == 2:
        if sys.argv[1] == '-file' or sys.argv[1] == '-f':
            write_data(data, date)
        elif sys.argv[1] == '-print' or sys.argv[1] == '-p':
            print_data(data)
    else:
        write_data(data, date)
        print_data(data)

if __name__ == "__main__":
    main()
