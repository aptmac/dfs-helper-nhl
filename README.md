# Daily Fantasy Helper (NHL)

## What is it?

This repository contains a couple of Python scripts that automate the creation of daily fantasy hockey rosters. It currently uses the Yahoo projected scores (which aren't nearly as bad as their NFL ones..), and scrapes `https://goaliepost.com/` to determine starting goaltenders.

## Installing dependencies

We'll need a handful of dependencies (`beautifulsoup`, `pandas`, and `PuLP`) for these scripts to work. If you don't already have them installed on your machine, you can install them using the provided `requirments.txt` file 

`> pip3 install -r requirements.txt`

Another dependency that is (optionally) required for the fetch script is `geckodriver`. This dependency must be set up manually, and is as simple as downloading the latest release of `geckodriver` and extracting the file into this project's directory. There is a check in `fetch_data.py` that looks for `./geckodriver`, so if you place the driver anywhere else then there will be some edits involved. `geckodriver` allows us to use Selenium to scrape websites that might otherwise force `requests` to solve a captcha, or sites that load their information on a delay using JavaScript to avoid bots from scraping all their juicy information.

## How to use:

First you need to fetch the data (salary, DFS game information, and projected scores).

`> python fetch_data.py (-p | -f)`

Supplying the `-p` will only print the raw data to the console (which can be piped into the solver script), and `-f` will only write the raw data to a local json file. Supplying neither will default to both.

Next, the data will need to be supplied to the solver. This can be done by:

`> python dfs-solver.py <path-to-file>`

or all-in-one by:

`> python fetch_data.py -p | python dfs-solver.py`

At the moment there's no built-in way to manipulate the json data, so if there's a player you want removed from the solutions (either due to being not active, or personal preference) it's easiest to have the data written to file, remove their entry using a text editor, and then feed the file into the solver.

## Initial Thoughts (2022)

I'm a bit late to the party here, I decided to take a look into NHL DFS for the second round of the 2022 Stanley Cup playoffs. Despite that, I was able to play my 5 free placement matches and join a couple of free DFS leagues. At the moment, DFS has been placed into the illegal gambling category in Ontario and all major DFS providers won't allow us to play in paid contests (BOO, and not boo-urns). As a result, I'll be able to play the free leagues, but no more placement matches for me .. :(

![diamond](https://user-images.githubusercontent.com/10425301/169357241-3cc3b236-ec6e-470c-8f55-f91f534b9811.png)

Placement matches I went 4-1, getting a Gold ranking and placing into the 73rd percentile. So far so good, and I hope to revisit this once Ontario (hopefully) reverses the ban on DFS.
