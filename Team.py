from nba_api.stats.static.teams import find_teams_by_nickname
from nba_api.stats.endpoints.boxscoretraditionalv2 import *
from nba_api.stats.endpoints.teamgamelog import *
from nba_api.stats.endpoints.commonteamroster import *
import cmd
from Player import *

class other(cmd.Cmd):
    prompt = "OTHER: "
    def do_goback(self, line):
        return -1

class Team:

    """Need to figure out a way to run the data once, then print it multiple times
    if it is called multiple times"""
    def __init__(self, team_nickname, n_games):
        if team_nickname is None and n_games is None:
            return

        self.team_nickname = team_nickname
        self.team_dict = find_teams_by_nickname(self.team_nickname)
        self.n_games = n_games
        self.team_id = 0
        self.gl = None
        self.game_ids = list()
        self.box_scores = list()
        self.n_games_found = False
        self.analyze_found = False
        self.totals = list()
        self.wins = 0
        self.losses = 0
        self.teams_beaten = list()
        self.teams_lost = list()
        self.team_found = False
        self.n_ids = list()
        self.roster = None

        self.keys = ["FGM", "FGA", "FG_PCT",
                     "FG3M", "FG3A", "FG3_PCT",
                     "FTM", "FTA", "FT_PCT",
                     "REB", "AST", "STL",
                     "BLK", "TO", "PTS"]  # Keys are used for BoxScoreTraditionalV2

        self.home_team_w = {key: 0 for key in self.keys}
        self.home_team_l = {key: 0 for key in self.keys}
        self.away_team_w = {key: 0 for key in self.keys}
        self.away_team_l = {key: 0 for key in self.keys}
        self.diff = {key: 0 for key in self.keys}

        if not len(self.team_dict):
            raise Exception
        else:
            self.team_id = self.team_dict[0]['id']
            self.team_nickname = self.team_dict[0]['nickname']
            self.gl = TeamGameLog(self.team_id).get_normalized_dict()['TeamGameLog']
            self.gl = self.gl[0:int(self.n_games)]

            for l in self.gl:
                tmp = l['Game_ID'], l['MATCHUP'], l['WL']
                self.game_ids.append(tmp)

            for game in self.game_ids:
                self.box_scores.append(BoxScoreTraditionalV2(game).get_normalized_dict()['TeamStats'])
                if self.box_scores[len(self.box_scores) -1][0]['TEAM_NAME'] != self.team_nickname:
                    self.box_scores[0].append(self.box_scores[len(self.box_scores) - 1][0])
                    del self.box_scores[0][0]

            self.initialize_data()
            self.team_found = True

    def found_team(self):
        return self.team_found

    def initialize_data(self):
        i = 0
        for game in self.box_scores:
            home_won = None
            t = 0
            if self.game_ids[i][2] == 'W':
                self.wins += 1
                home_won = True
                self.teams_beaten.append(self.game_ids[i][1])
            else:
                self.losses += 1
                home_won = False
                self.teams_lost.append(self.game_ids[i][1])
            try:
                for team in game:
                    for key in self.keys:
                        if t == 0:
                            if home_won:
                                self.home_team_w[key] += team[key]
                            else:
                                self.home_team_l[key] += team[key]
                        else:
                            if home_won:
                                self.away_team_l[key] += team[key]
                            else:
                                self.away_team_w[key] += team[key]
                    t += 1
            except Exception:
                print(f"Stats have not been posted for {team['TEAM_NAME']} yet")
                raise ValueError("No Stats")
            i += 1
        self.n_games_found = True

        self.totals = [self.home_team_w,
                       self.away_team_l,
                       self.home_team_l,
                       self.away_team_w]

        for i in range(len(self.totals)):
            team_total = self.totals[i]
            for stats in team_total:
                if (i == 0 or i == 1) and self.wins > 1:
                    tmp = team_total[stats]
                    tmp = tmp / self.wins
                    team_total[stats] = tmp
                elif (i == 2 or i == 3) and self.losses > 1:
                    tmp = team_total[stats]
                    tmp = tmp / self.losses
                    team_total[stats] = tmp
            i += 1
        self.analyze_found = True

    def print_analysis(self, diff=False):
        if diff:
            self.difference(self.home_team_w, self.away_team_l, won=True)
            self.difference(self.home_team_l, self.away_team_w, won=False)
            return
        # When jazz won:
        won = self.totals[0:2]
        lost = self.totals[2:4]

        i = 0
        st = ""
        if self.wins:
            for w in self.teams_beaten:
                st += w + ", "
            print(f"{self.wins} games won: {st}")
            for games in won:
                if i == 0:
                    print(f"{self.team_nickname} -> ", end="")
                else:
                    print("Opponent -> ", end="")
                for stats in games:
                    self.print(f"{stats}: {format(games[stats], '.2f')}")
                i += 1
                print()
            print()
            self.difference(self.home_team_w, self.away_team_l, won=True)
            print()  # space it out

        i = 0
        st = ""
        if self.losses:
            for w in self.teams_lost:
                st += w + ", "
            print(f"{self.losses} games lost: {st}")
            for games in lost:
                if i == 0:
                    print(f"{self.team_nickname} -> ", end="")
                else:
                    print("Opponent -> ", end="")

                for stats in games:
                    self.print(f"{stats}: {format(games[stats], '.2f')}")
                i += 1  # Used to increment the team
                print()
            print()
            self.difference(self.home_team_l, self.away_team_w)
        print(f"Record: {self.wins}-{self.losses}")
        print()


    def print_last_n_games(self):
        i = 0
        for game in self.box_scores:
            home_won = None
            print(f"{self.game_ids[i][1]}: {self.game_ids[i][2]}")
            t = 0
            for team in game:
                self.print(team['TEAM_ABBREVIATION'] + ": ")
                for key in self.keys:
                    self.print(f"{key}: {format(team[key],'.2f')}|")
                print()
            print()
            i += 1

    def get_roster(self):
        return CommonTeamRoster(self.team_id).get_normalized_dict()['CommonTeamRoster']

    def get_team_id(self):
        return self.team_id

    def get_team_nickname(self):
        return self.team_nickname

    def get_n_games(self):
        return self.n_games

    def print(self, data):
        print(f"{data}", end="|")

    def difference(self, first, second, won=False):
        if won:
            print("Difference (W) -> ", end="")
        else:
            print("Difference (L) -> ", end="")

        for key in self.keys:
            self.diff[key] = first[key] - second[key]
            self.print(f"{key}: {format(self.diff[key], '.2f')}")
        print()  # new line

    def game_ids(self):
        return self.n_ids


class TeamCmd(cmd.Cmd):
    def __init__(self, teams):
        cmd.Cmd.__init__(self)
        prompt = 'Teams'
        for i in teams.keys():
            prompt += '_'
            prompt += i
            self.last_team = i
        prompt += ' > '
        cmd.Cmd.prompt = prompt
        self.doc_header = ''
        self.teams = teams
        self.undoc_header = ''

    def do_stats(self, line):
        dif = False
        try:
            if line[-1] == 'd':
                dif = True
        except Exception:
            pass  # Didn't want to see difference

        for i in self.teams.keys():
            print(self.teams[i].get_team_nickname())
            self.teams[i].print_analysis(diff=dif)

    def do_players(self, line):
        rosters = list()
        n_games = self.teams[self.last_team].get_n_games()  # Doesn't matter which team, both will have the same n games
        for i in self.teams.keys():
            rosters.append(self.teams[i].get_roster())
        num = 1


        for roster in rosters:
            for players in roster:
                print(f"{num}: {players['PLAYER']} ({players['NUM']})")
                num += 1
            print("--------------------")
        print("Enter players")
        selections = list()

        while True:
            print(f"Enter players - Enter 0 when done")

            current = int(input()) - 1
            if current == -1:
                break
            else:
                selections.append(current)

        players = list()

        for selection in selections:
            i = 0
            while True:
                if selection > len(rosters[i]):
                    selection -= len(rosters[i])
                    i += 1
                else:
                    break
            players.append(Player(rosters[i][selection], n_games))

        PlayerCmd(players).cmdloop()

    def do_else(self, line):
        other().cmdloop()

    def do_back(self, line):
        return -1

    def default(self, line):
        print(f"{line}. Invalid syntax")
