#!/usr/bin/python3

# Modified and inspired by:
# https://kyle-stahl.com/draftkings

import pandas as pd
import json, os, pulp, sys
from datetime import datetime

rawdata = {}

def open_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def fetch_title(rawdata, g_id):
    title = g_id
    homeTeam = ''
    awayTeam = ''
    if g_id != 'multigame':
        found = False
        while found == False:
            for player in rawdata['players']['result']:
                if player['gameCode'] == g_id:
                    homeTeam = player['homeTeam']
                    awayTeam = player['awayTeam']
                    title = homeTeam + 'v' + awayTeam
                    found = True
                    break
    return title, homeTeam, awayTeam

def solve(rawdata, g_id,salary, numplayers):
    title, homeTeam, awayTeam = fetch_title(rawdata, g_id)
    players = pd.DataFrame(rawdata['players']['result'])
    if g_id != 'multigame':
        players = players[players.gameCode == g_id].reset_index()

    players["LW"] = (players["position"] == "LW").astype(float)
    players["C"] = (players["position"] == "C").astype(float)
    players["RW"] = (players["position"] == "RW").astype(float)
    players["D"] = (players["position"] == "D").astype(float)
    players["G"] = (players["position"] == "G").astype(float)
    players["salary"] = players["salary"].astype(float)
    if g_id != 'mutligame':
        # must have at least one player from each team (excluding goalies)
        players["t1"] = (players["team"] == homeTeam).astype(float)
        players["t2"] = (players["team"] == awayTeam).astype(float)

    model = pulp.LpProblem("DFS", pulp.LpMaximize)

    total_points = {}
    cost = {}
    lw = {}
    c = {}
    rw = {}
    d = {}
    g = {}
    num_players = {}
    t1 = {}
    t2 = {}

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
        if g_id != 'mutligame':
            t1[decision_var] = player["t1"]
            t2[decision_var] = player["t2"]
    
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
        t1_constraint = pulp.LpAffineExpression(t1)
        t2_constraint = pulp.LpAffineExpression(t2)
        # FIXME: I don't think this is quite right .. but it works?
        model += ((t1_constraint - G_constraint) >= 1)
        model += ((t2_constraint - G_constraint) >= 1)
        model += (G_constraint <= 2)
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
    if not os.path.exists('./results'):
        os.makedirs('./results')
    my_team.to_json('./results/' + retrieve_date(rawdata) + '-' + title + '.json', indent=2, orient='table')

    print('--- Completed ---')

def retrieve_date(data):
    timestamp = data['currentTime'] / 1000 # Yahoo lists in ms, datetime uses seconds
    return datetime.fromtimestamp(timestamp).strftime('%Y%m%dT%H%M%S')

def main():
    if len(sys.argv) == 2:
        rawdata = open_json(sys.argv[1])
    else:
        rawdata = json.loads(sys.stdin.read())
    # Create lineup for the multigame slate
    solve(rawdata, 'multigame', rawdata['salaryCapInfo']['result'][0]['multiGameSalaryCap'], 9)
    # Create lineups for individual games
    for g_id in rawdata['salaryCapInfo']['result'][0]['singleGameSalaryCapMap'].keys():
        salary = rawdata['salaryCapInfo']['result'][0]['singleGameSalaryCapMap'][g_id]
        solve(rawdata, g_id, salary, 5)

if __name__ == "__main__":
    main()
