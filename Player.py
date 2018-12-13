from nba_api.stats.endpoints.playerdashboardbylastngames import *
from nba_api.stats.endpoints.playergamelog import *
import cmd

class PlayerCmd(cmd.Cmd):
    def __init__(self, players):
        super().__init__()
        self.current_players = players
        if len(self.current_players) > 1:
            self.prompt = 'Player_Compare > '
        else:
            self.prompt = 'Player_Stats > '

        self.doc_header = ''
        self.undoc_header = ''

    def do_stats(self, line):
        dif = False
        try:
            if line[-1] == 'd':
                dif = True
        except Exception:
            pass  # Didn't want to see difference

        for player in self.current_players:
            player.display_stats(diff=dif)
            print()
            print()

    def do_back(self, line):
        return -1


class Player:
    def __init__(self, player, n_games):
        self.player_info = player
        self.player_id = player['PLAYER_ID']
        self.player_name = player['PLAYER']
        self.n_games = n_games

        self.overall = PlayerDashboardByLastNGames(self.player_id,
                                                   self.n_games).get_normalized_dict()
        self.keys = ["MIN", "FGM", "FGA", "FG_PCT", "FG3M",
                     "FG3A", "FG3_PCT", "FTM", "FTA", "FT_PCT",
                     "REB", "AST", "TOV", "STL", "BLK", "PTS", "PLUS_MINUS", ]

        self.games = PlayerGameLog(self.player_id).get_normalized_dict()['PlayerGameLog']

        self.wins = 0
        self.losses = 0

        self.games = self.games[0:int(self.n_games)]

        self.stats_w = {key: 0 for key in self.keys}
        self.stats_l = {key: 0 for key in self.keys}
        self.diff = dict()  # don't need to initialize, because odds are, everything else
                            # will have a value we can find the diff for.
        self.initialize_data()

    def initialize_data(self):
        for game in self.games:
            if game['WL'] == 'W':
                won = True
                self.wins += 1
            else:
                won = False
                self.losses += 1
            for key in self.keys:
                if won:
                    self.stats_w[key] += game[key]
                else:
                    self.stats_l[key] += game[key]

    def display_stats(self, diff=False):
        print(f"{self.player_name}: {self.wins} - {self.losses}")

        if diff:
            self.display_diff()
            return

        print("Wins: ", end="")
        for stats in self.keys:
            if self.wins:
                self.stats_w[stats] /= self.wins
            self.print(f"{stats}: {format(self.stats_w[stats], '.2f')}")
        print()
        print("Losses: ", end="")
        for stats in self.keys:
            if self.losses:
                self.stats_l[stats] /= self.losses
            self.print(f"{stats}: {format(self.stats_l[stats], '.2f')}")
        print()

        self.display_diff()

    def display_diff(self):
        for stat in self.keys:
            self.diff[stat] = self.stats_w[stat] - self.stats_l[stat]
            self.print(f"{stat}: {format(self.diff[stat], '.2f')}")

    def print(self, data):
        print(f"{data}|", end="")