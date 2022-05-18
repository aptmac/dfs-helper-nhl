#!/usr/bin/python3

# Modified and inspired by:
# https://kyle-stahl.com/draftkings

import pandas as pd
import json, os, pulp, sys
from datetime import datetime

rawdata = {}

def open_json():
    with open(sys.argv[1], 'r') as f:
        return json.load(f)

def fetch_title(rawdata, g_id):
    title = g_id
    if g_id != 'multigame':
        found = False
        while found == False:
            for player in rawdata['players']['result']:
                if player['gameCode'] == g_id:
                    title = player['homeTeam'] + 'v' + player['awayTeam']
                    found = True
                    break
    return title

def solve(rawdata, g_id, salary, numplayers):
    players = pd.DataFrame(rawdata['players']['result'])
    if g_id != 'multigame':
        players = players[players.gameCode == g_id].reset_index()

    players["LW"] = (players["position"] == "LW").astype(float)
    players["C"] = (players["position"] == "C").astype(float)
    players["RW"] = (players["position"] == "RW").astype(float)
    players["D"] = (players["position"] == "D").astype(float)
    players["G"] = (players["position"] == "G").astype(float)
    players["salary"] = players["salary"].astype(float)

    model = pulp.LpProblem("DFS", pulp.LpMaximize)

    total_points = {}
    cost = {}
    lw = {}
    c = {}
    rw = {}
    d = {}
    g = {}
    num_players = {}

    vars = []

    for i, player in players.iterrows():
        var_name = 'x' + str(i)
        decision_var = pulp.LpVariable(var_name, cat='Binary')
        vars.append(decision_var)

        total_points[decision_var] = player["fppg"]
        cost[decision_var] = player["salary"]

        lw[decision_var] = player["LW"]
        c[decision_var] = player["C"]
        rw[decision_var] = player["RW"]
        d[decision_var] = player["D"]
        g[decision_var] = player["G"]
        num_players[decision_var] = 1.0
    
    objective_function = pulp.LpAffineExpression(total_points)
    model += objective_function

    total_cost = pulp.LpAffineExpression(cost)
    model += (total_cost <= salary)

    print('--- (2/4) Defining the constraints ---')
    LW_constraint = pulp.LpAffineExpression(lw)
    C_constraint = pulp.LpAffineExpression(c)
    RW_constraint = pulp.LpAffineExpression(rw)
    D_constraint = pulp.LpAffineExpression(d)
    G_constraint = pulp.LpAffineExpression(g)
    total_players_constraint = pulp.LpAffineExpression(num_players)

    if g_id == 'multigame':
        model += (LW_constraint <= 3)
        model += (C_constraint == 2)
        model += (RW_constraint <= 3)
        model += (D_constraint == 2)
        model += (G_constraint == 2)
    else:
        # TODO: add constraint that at least one player (excluding goalie) from each team must be in roster
        model += (G_constraint <= 1) 
    model += (total_players_constraint == numplayers)

    print('--- (3/4) Solving the problem ---')
    model.solve()

    print('--- (4/4) Formatting the results ---')
    players["is_drafted"] = 0.0

    for var in model.variables():
        players.iloc[int(var.name[1:]), players.columns.get_loc('is_drafted')] = var.varValue

    my_team = players[players["is_drafted"] == 1.0]
    my_team = my_team[["name", "position", "team", "salary", "fppg"]]

    print(my_team)
    print("Total used amount of salary cap: {}".format(my_team["salary"].sum()))
    print("Projected points: {}".format(my_team["fppg"].sum().round(1)))

    # write to json file
    title = fetch_title(rawdata, g_id)
    if not os.path.exists('./results'):
        os.makedirs('./results')
    my_team.to_json('./results/' + retrieve_date(rawdata) + '-' + title + '.json', indent=2, orient='table')

    print('--- Completed ---')

def retrieve_date(data):
    timestamp = data['currentTime'] / 1000 # Yahoo lists in ms, datetime uses seconds
    return datetime.fromtimestamp(timestamp).strftime('%Y%m%dT%H%M%S')

def main():
    if len(sys.argv) == 2:
        rawdata = open_json()
    else:
        rawdata = json.loads(sys.stdin.read())
    # Create lineup for the multigame slate
    solve(rawdata, 'multigame', rawdata['salaryCapInfo']['result'][0]['multiGameSalaryCap'], 9)
    # Create lineups for individual games
    for key in rawdata['salaryCapInfo']['result'][0]['singleGameSalaryCapMap'].keys():
        g_id, salary = key, rawdata['salaryCapInfo']['result'][0]['singleGameSalaryCapMap'][key]
        solve(rawdata, g_id, salary, 5)

if __name__ == "__main__":
    main()
