from Team import *
from Player import *

from nba_api.stats.endpoints.commonteamroster import *
"""
    This class emulates the command line. It uses the function
    get() to get the input from the line. It uses the command 
    where it is needed. I tried to make this like bash, it will
    stay in the 'section' with the options each section has. The
    class uses recursion to keep repeating the menu. '..' will go 
    back one 'menu step'. This in turn will exit the program
"""


class Line:
    def __init__(self):
        self.current_team = Team(None, None)
        current_command = self.get()
        self.run(current_command)
    """
            This class emulates the starting point in the program. It takes the teams nickname
            as the first paramter, followed by -n, where n is the number of games the user would 
            like to see stats for the team or player. 
            Commands:
                    'nickname -n': Starts the program and loads the stats for the specified team.
                    '..':          Exits the program.           
    """

    def run(self, current_command):
        invalid_command = current_command
        current_command = current_command.split(' ')

        if current_command[0] == "..":
            exit("Thank you for using this excellent software")
        elif len(current_command) < 2:
            print(f"{invalid_command} is not a valid command")
            self.run(self.get())
        elif not current_command[1][0].__contains__('-'):
            print(f"{invalid_command} is not a valid command")
            self.run(self.get())
        else:
            n_games = current_command[1][1:]
            nick_name = current_command[0]
            self.current_team = Team(nick_name, n_games)
            if not self.current_team.found_team():
                self.run(self.get(team_options=False))
            self.team_options()
            self.run(self.get(team_options=False))
    """
            This class emulates the team options. It will display the corresponding teams stats
            over the last n games.
            Commands:
                    'show last':   This will display the collection of stats for the last 
                                   n games for team. 
                    'analyze -d':  This will just display the difference in the stats when
                                   when the team wins in games.
                    'players':     This will load the player options menu.
                    '..':          Goes back one menu option to the main menu           
    """

    def team_options(self):
        command = self.get(True)
        if command == "show last":
            self.current_team.print_last_n_games()
        elif command == 'analyze':
            self.current_team.print_analysis()
        elif command == 'analyze -d':
            self.current_team.print_analysis(diff=True)
        elif command == 'players':
            self.player_options()
        elif command == 'players -c':
            self.player_options(True)
        elif command == '..':
            return
        else:
            print("invalid command")

        # Finished the process, now repeat team options
        self.team_options()
    """
            This class emulates the player options. It will print out the entire roster of the
            team and wait for a corresponding number to the player the user wants to see.
            Commands:
                    '#":           Passes the corresponding player to the player stats 
                                   option menu
                    '..':          Goes back one menu option to the team options menu           
    """

    def player_options(self, compare=False):
        roster = CommonTeamRoster(self.current_team.get_team_id()).get_normalized_dict()
        players = roster['CommonTeamRoster']
        i = 1  # used to number
        for player in players:
            print(f"{i} - {player['PLAYER']}({player['NUM']})")
            i += 1
        command = self.get(player_options=True)
        if command == '..':
            return
        else:
            command = int(command) - 1

        if int(command) < 0 or int(command) > len(players):
            print(f"{command} is an invalid command")
            self.player_options()
        elif command == '..':
            return

        player1 = Player(players[int(command)], self.current_team.n_games)
        player1_name = players[command]['PLAYER']

        player2_name = None
        player2 = None

        if compare:
            command = self.get(player_options=True)
            command = int(command) - 1
            if int(command) < 0 or int(command) > len(players):
                print(f"{command} is an invalid command")
                self.player_options()
            player2 = Player(players[int(command)], self.current_team.n_games)
            player2_name = players[int(command)]['PLAYER']

        self.player_stats(player1, player1_name, player2, player2_name)
        if compare:
            self.player_options(True)
        else:
            self.player_options()
    """
        This class emulates the player stats options. 
        Commands:
                'display':     This will display the last n games for the players stats,
                               it will also show the difference.
                'display -d':  This will just display the difference in the stats when
                               when the players team wins in games.
                '..':          Goes back one menu option to the player options menu           
    """

    def player_stats(self, player1, player1_name, player2=None, player2_name=None):
        if player2 is None:
            command = self.get(player_stats=(True, player1_name))
            if command == 'display':
                player1.display_stats()
            elif command == 'display -d':
                player1.display_diff()
            elif command == "..":
                return
            else:
                print(f"{command} is not a valid command")

            self.player_stats(player1, player1_name)
        else:
            command = self.get(player_compare=(True, player1_name, player2_name))
            if command == 'display':
                print()
                player1.display_stats()
                player2.display_stats()
                print()
            elif command == 'display -d':
                print()
                print(player1_name)
                player1.display_diff()
                print()
                print(player2_name)
                player2.display_diff()
                print()
            elif command == "..":
                return
            else:
                print(f"{command} is not a valid command")

            self.player_stats(player1, player1_name, player2, player2_name)
    """
        This function will print out the correct layout for the menu which the user is in. 
        It will return the input, to the function where the input will be evaluated.
    """

    def get(self, team_options=False, player_options=False, player_stats=(False, None),
            player_compare=(False, None, None)):
        if team_options:
            print(self, end=f'_{self.current_team.get_team_nickname()} > ')
        elif player_options:
            print(self, end=f'_{self.current_team.get_team_nickname()}_Players > ')
        elif player_stats[0]:
            print(self, end=f'_{self.current_team.get_team_nickname()}_Players_{player_stats[1]} > ')
        elif player_compare[0] is True:
            if player_compare[1] is None:
                print(self, end=f'_{self.current_team.get_team_nickname()}_Players_Compare > ')
            else:
                print(self, end=f'_{self.current_team.get_team_nickname()}'
                                f'_Players_{player_compare[1]} vs {player_compare[2]} > ')
        else:
            print(self, end="> ")
        return input()

    """
        Starting output of the program
    """
    def __str__(self):
        return "Stat finder"
