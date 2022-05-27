import fetch_data as fd
import dfs_solver as dfss
import os

HEADER = """\
   ___  ________  __ __    __                     _  ____ ____ 
  / _ \/ __/ __/ / // /__ / /__  ___ ____  ____  / |/ / // / / 
 / // / _/_\ \  / _  / -_) / _ \/ -_) __/ /___/ /    / _  / /__
/____/_/ /___/ /_//_/\__/_/ .__/\__/_/         /_/|_/_//_/____/
                         /_/                                                                        
Optimizing Daily Fantasy Hockey lineups for Yahoo DFS
DFS Helper (NHL) Version 0.0.0, May 2022
https://github.com/aptmac/dfs-helper-nhl
"""

SETUP_OPTIONS="""\
    1. Fetch and load new data
    2. Import existing data
    3. Exit
"""

MAIN_OPTIONS="""\
    1. Fetch and load new data
    2. Import existing data
    3. Multi-game solver
    4. Single-game solver
    5. Exit
"""

SOLVER_SETTINGS="""\
Current Settings:
- Number of rosters: {}
- Players to include: {}
- Players to exclude: {}
- Print results to: {}
"""

SOLVER_OPTIONS="""\
    1. Run
    2. Include player from roster
    3. Exclude player from roster
    4. Set number of solutions
    5. Set output location
    6. Back
"""
CURRENT_FILE = 'Current data file loaded: {}'
OPTION_SELECTION = 'Select your option: '
ERROR_INVALID_OPTION = 'ERROR: You have selected an invalid option. Please try again.'

settings = {
    'rosters': 0,
    'include': [],
    'exclude': [],
    'results': 'console'
}

# global setter functions
def set_shutdown(b):
    global shutdown
    shutdown = b

def set_file(path):
    global file
    file = path

def set_rawdata(data):
    global rawdata
    rawdata = data

def cls():
    print("\033c", end='') # https://stackoverflow.com/a/50560686

def setup():
    print(SETUP_OPTIONS)
    option = input(OPTION_SELECTION)
    if option == '1':
        fetch_data()
    elif option == '2':
        return import_data()
    elif option == '3':
        set_shutdown(True)
    else:
        cls()
        print(HEADER)
        print(ERROR_INVALID_OPTION)
        return False
    return True

def fetch_data():
    data = fd.fetch_data()
    set_rawdata(data)
    path = fd.write_data(data, fd.retrieve_date(data))
    set_file(path)

# TODO: maybe this just parses all the files in rawdata with the option of selecting which file you want to use instead of having to type
def import_data():
    path = input('Please type the path to the file: ')
    if os.path.exists(path):
        data = dfss.open_json(path)
        set_rawdata(data)
        set_file(path)
        return True
    else:
        print('\nERROR: "' + path + '" is not a valid file. Please try again.\n')
        return False

def game_selection():
    return None

def solver():
    while 1:
        cls()
        print(HEADER)
        print(SOLVER_SETTINGS.format('1', 'None', 'None', 'console'))
        print(SOLVER_OPTIONS)
        option = input(OPTION_SELECTION)
        if option == '1':
            solve()
        elif option == '2':
            include_player(1)
        elif option == '3':
            exclude_player(1)
        elif option == '4':
            set_num_solutions(1)
        elif option == '5':
            set_output_location(1)
        elif option == '6':
            break

def solve():
    return None

def include_player(player):
    player = input('Functionality coming soon(tm) .. press any key to continue..')
    return None

def exclude_player(player):
    player = input('Functionality coming soon(tm) .. press any key to continue..')
    return None

def set_num_solutions(num):
    player = input('Functionality coming soon(tm) .. press any key to continue..')
    return None

def set_output_location(location):
    player = input('Functionality coming soon(tm) .. press any key to continue..')
    return None

def init():
    set_shutdown(False)
    set_file('None')
    cls()
    print(HEADER)

def main():
    global shutdown
    global file
    global rawdata
    setup_complete = False
    while setup_complete == False:
        setup_complete = setup()
    while (shutdown == False):
        cls()
        print(HEADER)
        print (CURRENT_FILE.format(file))
        print(MAIN_OPTIONS)
        option = input(OPTION_SELECTION)
        if option == '1':
           fetch_data()
        elif option == '2':
            import_data()
        elif option == '3':
            dfss.solve(rawdata, 'multigame', 200, 9)
            option = input ('Press any key to continue ..')
        elif option == '4':
            g_id = game_selection()
            solver()
            option = input ('Press any key to continue ..')
        elif option == '5':
            set_shutdown(True)
            break

if __name__ == "__main__":
    init()
    main()
