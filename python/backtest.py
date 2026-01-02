import pandas as pd
from nba_api.stats.static import teams,players

nba_players = players.get_players()
print("Number of players fetched: {}".format(len(nba_players)))

# for player in nba_players:
#     print(player)

print(nba_players[0])