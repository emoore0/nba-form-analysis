# nba-form-analysis

Can a player's recent 3-point shooting actually predict their next few games? Or is the "hot hand" mostly noise?

This project compares two simple prediction approaches: **season-to-date shooting rate** vs **recent N-game rate** - to see which better estimates a player's 3-point makes over their next N games. Spoiler: the answer might not be what the fans want to hear.

## How It Works

1. **SQL view** (`player_game_features`) computes rolling window stats for every player-game: previous 5/10/20 game totals, season-to-date totals and next 5/10/20 game totals. All using window functions with the current game excluded.

2. **Python script** (`backtest.py`) loads the features, builds two predictions per row (baseline vs. recent form) and compares them using Mean Absolute Error.

## Quick Start

### Prerequisites

- Python 3.8+
- `pandas` (`pip install pandas`)
- SQLite database with NBA player game-level stats (table: `player_games`)
- DB Browser for SQLite (optional, for exploring the data)

### Setup

```bash
# Clone the repo
git clone https://github.com/yourusername/nba-form-analysis.git
cd nba-form-analysis

# Install dependencies
pip install pandas

# Make sure your database is at the expected path or update DB_PATH in the script
```

### Create the SQL View

Open your database in DB Browser for SQLite (or any SQLite client) and run the view creation query in `sql/create_features_view.sql`. This builds the `player_game_features` view with all the rolling window columns.

### Run the Analysis

```bash
python backtest.py
```

This will output Mean Absolute Error (MAE) comparisons for window sizes 5, 10 and 20 and give us a comparison of using recent form vs season to date.

## How We Measure Accuracy

To compare the two prediction methods we use MAE. 
MAE tells us, on average, how many 3-pointers the model was off by.
Lower MAE = better prediction.

## Project Structure

```
nba-form-analysis/
├── python/
│   ├── backtest.py   # Main prediction & evaluation script
├── sql/
│   ├── raw_player_games_nba.db   # SQLite database 
│   └── raw_player_games_nba.sql  # SQL to create player_game_features view
├── PROJECT.md                # Detailed project writeup & methodology
└── README.md                 # You're here
```

## Key Concepts

- **Season-to-date rate**: A player's cumulative 3P% heading into a game - the "who they are" estimate
- **Recent-N rate**: Their 3P% over the last N games - the "hot hand" estimate
- **Both predictions use known future attempt volume**, so the comparison is purely about which *rate* is more predictive
