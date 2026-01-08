# import pandas as pd
# from nba_api.stats.static import teams,players

# nba_players = players.get_active_players()



# player_data = {
#     "id" : [],
#     "full_name" : [],
#     "is_active" : []
# }

# # df = pd.DataFrame(player_data)

# df = pd.DataFrame.from_dict(nba_players)   
# # print(nba_players[0])
# df.pop("first_name")
# df.pop("last_name")
# df.pop("is_active") # Only looking at active players in 25/26
# print(df.to_string(index=False))

# # print("Number of players fetched: {}".format(len(nba_players)))

# # list_of_players = []
# # for player in nba_players:
# #      list_of_players.append(player)

# # print(list_of_players)

import time
import pandas as pd
from nba_api.stats.endpoints import leaguegamelog

def fetch_player_game_logs(season="2024-25", season_type="Regular Season"):
    # player_or_team_abbreviation can be "P" for player logs
    lg = leaguegamelog.LeagueGameLog(
        season=season,
        season_type_all_star=season_type,
        player_or_team_abbreviation="P"
    )
    df = lg.get_data_frames()[0]
    return df

def main():
    df = fetch_player_game_logs(season="2024-25", season_type="Regular Season")
    print(df.head().to_string(index=False))
    print(f"Rows: {len(df):,}")

    # Save raw
    df.to_csv("../data/raw/nba_player_game_2024_25_regular.csv", index=False)

if __name__ == "__main__":
    main()
