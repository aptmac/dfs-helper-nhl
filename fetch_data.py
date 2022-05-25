#!/usr/bin/python3

import json, os, requests, sys
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.request import urlopen

YAHOO_API_ENDPOINT = 'https://dfyql-ro.sports.yahoo.com/v2/external/playersFeed/nhl'
STARTING_GOALIES_URL = 'https://goaliepost.com/'
INJURY_REPORT_URL = 'https://www.cbssports.com/nhl/injuries/daily/'

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

def remove_nonstarting_goalies(data):
    goalies = []
    players = []

    req = requests.get(STARTING_GOALIES_URL)
    soup = BeautifulSoup(req.content, 'html.parser')
    starters = soup.find_all('span', {'class':'starterName'})

    for goalie in starters:
        goalies.append(goalie.get_text())
    for player in data['players']['result']:
        if player['position'] == 'G' and player['name'] not in goalies:
            pass
        else:
            players.append(player)
    data['players']['result'] = players
    return data

def remove_injured_players(data):
    injured = []
    players = []

    timestamp = data['currentTime'] / 1000 # Yahoo lists in ms, datetime uses seconds
    target_date = datetime.fromtimestamp(timestamp).strftime('%A, %B %d, %Y')
    soup = BeautifulSoup(requests.get(INJURY_REPORT_URL).content, 'html.parser')
    i = 0
    for date in soup.findAll('h4'): # each date is a separate h4 tag somewhere on the page
        if date.text.strip() == target_date:
            table = soup.findAll('h4')[i].findNext('tbody')
            for span in table.find_all('span', {'class': 'CellPlayerName--long'}):
                injured.append(span.text)
            break
        i = i + 1

    for player in data['players']['result']:
        if player['name'] not in injured:
            players.append(player)
    data['players']['result'] = players
    return data

def main():
    data = fetch_data()
    # TODO: remove redundancy in functions that remove players
    data = remove_injured_players(data)
    data = remove_nonstarting_goalies(data)
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
