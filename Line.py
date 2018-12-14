from Team import *
import cmd

"""
    This class emulates the command line. It uses the function
    get() to get the input from the line. It uses the command 
    where it is needed. I tried to make this like bash, it will
    stay in the 'section' with the options each section has. The
    class uses recursion to keep repeating the menu. '..' will go 
    back one 'menu step'. This in turn will exit the program
"""



class LineCmd(cmd.Cmd):
    prompt = 'Stats > '

    def __init__(self):
        cmd.Cmd.__init__(self)
        cmd.Cmd.prompt = 'Stats > '
        self.doc_header = ''
        self.undoc_header = ''


    def do_t(self, line):
        teams = dict()  # Name of team, then data
        line = line.split(' ')

        n_games = line[-1][1:]

        try:
            n_games = int(n_games)
            line = line[0:-1]
        except Exception:
            self.default(f'team {line}')
            self.cmdloop()

        found_teams = True
        for team_nickname in line:
            try:
                tmp = Team(team_nickname, n_games)
                teams[team_nickname] = tmp
                print(f"Loaded {team_nickname} stats")
            except Exception:
                print(f"Unable to load {team_nickname} stats")
                found_teams = False

        if found_teams:
            TeamCmd(teams).cmdloop()
        else:
            self.cmdloop()

    def default(self, line):
        print(f'{line}. Not a recognized command')

    def do_exit(self, line):
        self.postloop()

    def postloop(self):
        exit("Thanks!")
