#!/usr/bin/python3

import json, os, re, requests, sys
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.request import urlopen

from get_gecko_driver import GetGeckoDriver
from selenium import webdriver
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

YAHOO_API_ENDPOINT = 'https://dfyql-ro.sports.yahoo.com/v2/external/playersFeed/nhl'
STARTING_GOALIES_URL = 'https://goaliepost.com/'
INJURY_REPORT_URL = 'https://www.cbssports.com/nhl/injuries/daily/'
HEALTHY_SCRATCH_URL = 'https://www.dailyfaceoff.com/hockey-player-news/line-changes/'

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

# Given a URL, use Selenium to open a web browser, fiddle with the page to cause
# the JavaScript to run (and populate the table), then scrape the html
def scrape_html(url):
    options = FirefoxOptions()
    options.add_argument("--headless")

    driver = webdriver.Firefox(executable_path=('./geckodriver'), options=options)
    driver.get(url)
    html = driver.page_source
    driver.quit()
    return html

def remove_scratched_players(data):
    scratched = []
    players = []

    timestamp = data['currentTime'] / 1000 # Yahoo lists in ms, datetime uses seconds
    target_date = datetime.fromtimestamp(timestamp).strftime('%m/%d/%y')

    soup = BeautifulSoup(scrape_html(HEALTHY_SCRATCH_URL), 'html.parser')
    for article in soup.findAll('article'):
        # Make sure it's for a healthy scratch
        headline = article.find('div', {'class': 'news-headline-row'}).text
        if bool(re.search('healthy scratch', headline)):
            # Make sure it's for today's date
            content = article.find('div', {'class': 'news-content-row'}).text
            p = re.compile(r'\d{2}\/\d{1,2}\/\d{2}')
            # retrieve and format the date so it'll be consistent with the DFS date
            d = datetime.strptime(p.search(content).group(), '%m/%d/%y').strftime('%m/%d/%y')
            if d == target_date:
                scratched.append(article.find('h3', {'class': 'player-name'}).text)

    for player in data['players']['result']:
        if player['name'] not in scratched:
            players.append(player)
    data['players']['result'] = players
    return data

def main():
    data = fetch_data()
    # TODO: remove redundancy in functions that remove players
    if (os.path.exists('./geckodriver')):
        data = remove_scratched_players(data)
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
