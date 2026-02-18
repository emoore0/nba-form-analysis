import sqlite3
import pandas as pd


DB_PATH = "/home/emoore0/nba_project/sql/raw_player_games_nba.db"
FEATURES_TABLE = "player_game_features"  # change if yours is different
WINDOWS = [5, 10, 20] # Rolling windows of games


# -> is documentation for what should actually be returned by the function
def load_features(db_path: str, table: str, n: int) -> pd.DataFrame: # takes in the database, and the virtual table we want
    conn = sqlite3.connect(db_path) # python connects to the SQL database

    query = f"""
    SELECT
      PLAYER_ID,
      PLAYER_NAME,
      GAME_DATE,
      GAME_ID,
      FG3M,
      FG3A,
      prev{n}_3pm, prev{n}_3pa,
      std_3pm, std_3pa,
      next{n}_3pm, next{n}_3pa
    FROM {table}
    """
    df = pd.read_sql_query(query, conn)
    conn.close() # closes the connection

    # Ensure correct types
    df["GAME_DATE"] = pd.to_datetime(df["GAME_DATE"]) # changes string value to datetime
    numeric_cols = [
        "FG3M", "FG3A",
        f"prev{n}_3pm", f"prev{n}_3pa",
        "std_3pm", "std_3pa",
        f"next{n}_3pm", f"next{n}_3pa"
    ]
    for c in numeric_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce") # makes all the string values into numeric ones

    return df


def make_predictions(df: pd.DataFrame, n: int) -> pd.DataFrame:
    df = df.copy() # takes a copy of the dataframe to use

    # We want to predict NEXT n games 3PM.

    target = f"next{n}_3pm" # how many 3's were actually made. 

    # Inputs for rates
    prev_m = f"prev{n}_3pm"
    prev_a = f"prev{n}_3pa"

    # 1) Baseline: season-to-date rate * next n attempts
    # std_* already excludes current game in SQL, which is correct.
    df["std_rate"] = df["std_3pm"] / df["std_3pa"] # season to date 3 point estimated make rate
    df["pred_baseline"] = df["std_rate"] * df[f"next{n}_3pa"]#  season to date 3 point estimated make rate multiplied by the next N amount of attempts. gives you estimate for expected 3's made

    # 2) Recent form: previous n rate * next n attempts
    df["prev_rate"] = df[prev_m] / df[prev_a] # 3 point estimated make rate over the last N games
    df["pred_recent"] = df["prev_rate"] * df[f"next{n}_3pa"] # 3 point estimated make rate over the last N games multiplied by the next N amount of attempts. gives you estimate for expected 3's made

    # Clean invalid rows:
    # We need target, next attempts, and denominators to exist and be > 0
    valid = ( # Build a boolean filter
        df[target].notna() # detects any non-nulls as True depending on existence
        & df[f"next{n}_3pa"].notna() 
        & (df[f"next{n}_3pa"] > 0)
        & df["std_3pa"].notna()
        & (df["std_3pa"] > 0)
        & df[prev_a].notna()
        & (df[prev_a] > 0)
    ) # this helps to remove all the values where it is shows as false meaning it has a null or is less then 0 
    df = df.loc[valid].copy()  # gives all the rows where Valid == true

    # Errors (absolute)
    df["err_baseline"] = (df["pred_baseline"] - df[target]).abs() # Difference between season to date preciction and how many threes were actually made 
    df["err_recent"] = (df["pred_recent"] - df[target]).abs() #  Difference between last N games preciction and how many threes were actually made  

    return df


def summarize(df: pd.DataFrame, n: int) -> None:
    target = f"next{n}_3pm" # actual 3's made over N games

    overall = {
        "rows": len(df), # number of rows
        "players": df["PLAYER_ID"].nunique(), # number of players
        "mae_baseline": df["err_baseline"].mean(), # average of all errors season to date
        "mae_recent": df["err_recent"].mean(), # average of all errors based on last N games
        "recent_minus_baseline": df["err_recent"].mean() - df["err_baseline"].mean(),
    }

    print("\n=== OVERALL ===")
    for k, v in overall.items(): 
        if isinstance(v, float): # checks if object is the desired type
            print(f"{k}: {v:.4f}") # prints float with 4 decimal places
        else:
            print(f"{k}: {v}") # just print the dictionary normally


def main():

    results = []

    for n in WINDOWS:
        df = load_features(DB_PATH, FEATURES_TABLE,n)
        print(f"Loaded rows: {len(df):,} from {FEATURES_TABLE}")

        df = df.sort_values(["PLAYER_ID", "GAME_DATE", "GAME_ID"])
        print(f"\n\n######## WINDOW = {n} ########")

        scored = make_predictions(df, n)
        summarize(scored, n)

        results.append({
            "window": n,
            "rows": len(scored),
            "mae_baseline": scored["err_baseline"].mean(),
            "mae_recent": scored["err_recent"].mean()
        })

    summary_df = pd.DataFrame(results)
    summary_df["recent_minus_baseline"] = (
        summary_df["mae_recent"] - summary_df["mae_baseline"]
    )

    print("\n\n=== SUMMARY TABLE ===")
    print(summary_df.to_string(index=False))



if __name__ == "__main__":
    main()
