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
