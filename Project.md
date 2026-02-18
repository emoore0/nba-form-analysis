# NBA 3-Point Form Analysis

## The Question

This project aims to explore the question: **"How does a player's recent 3-point makes and attempts over the last N games relate to their next N games' 3-point makes?"**

This matters. It matters differently depending on who's asking.

Fans mainly care about who's hot. A fan might say, "Steph is averaging 7 3PM over his last 5 games, he'll surely get at least 6 next game." Teams may care more about shot volume and player roles. A coach might wonder, "Reaves has been on a hot streak with 3PM but how much is Luka's absence inflating his volume?"

We'll dive deep into the data and see how closely tethered recent form actually is to short-term and long-term output. The approach: use game-level player data, create useful features using SQL window functions and conduct evaluations in Python.

---

## What We're Really Testing

Here's the core hypothesis, stated plainly:

> "Given we already know the next N games' attempt volume, which rate estimate, season-to-date vs last-N-games — better predicts the next N 3-point makes?"

In other words: if we could peek into the future and see how many threes a player *attempts*, does their recent shooting percentage or their season-long percentage give us a better guess at how many they'll *make*?

That's a meaningful distinction. It separates the "hot hand" narrative from the steady baseline.

---

## Data

The raw data lives in a SQLite database (`raw_player_games_nba.db`) with a `player_games` table containing game-level stats for NBA players. Each row is part of one player's stat line from one game: points, rebounds, assists and critically for us, `FG3M` (3-pointers made) and `FG3A` (3-pointers attempted).

---

## Feature Engineering (SQL)

This is where the project gets interesting. We created a SQL view called `player_game_features` that adds rolling window stats onto every player-game row.

### The Windows

For each player-game, the view computes:

- **Previous N games**: `prev5_3pm`, `prev5_3pa`, `prev10_3pm`, `prev10_3pa`, `prev20_3pm`, `prev20_3pa` - the sum of 3-point makes and attempts over the 5, 10 and 20 games *before* the current game. The current game is always excluded. This uses `ROWS BETWEEN N PRECEDING AND 1 PRECEDING`.

- **Season-to-date**: `std_3pm`, `std_3pa` - cumulative 3PM and 3PA from the start of the player's record up to (but not including) the current game. Uses `ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING`.

- **Next N games**: `next5_3pm`, `next5_3pa`, `next10_3pm`, `next10_3pa`, `next20_3pm`, `next20_3pa` - the sum of 3-point makes and attempts over the next 5, 10 and 20 games *after* the current game. This is the "future" we're trying to predict. Uses `ROWS BETWEEN 1 FOLLOWING AND N FOLLOWING`.

All windows are partitioned by `PLAYER_ID` and ordered by `GAME_DATE, GAME_ID` - so we never leak data across players or mess up the timeline.

### Why Exclude the Current Game?

A subtle but important choice. If we included the current game in "previous" stats, we'd be using today's result to predict today's result. Same deal with the "next" window - including the current game would inflate accuracy artificially. The 1 PRECEDING / 1 FOLLOWING boundary keeps things clean.

### The View SQL (Simplified)

```sql
CREATE VIEW player_game_features AS
WITH base AS (
  SELECT
    PLAYER_ID, PLAYER_NAME, GAME_DATE, GAME_ID, FG3M, FG3A,

    -- Previous windows
    SUM(FG3M) OVER prev5  AS prev5_3pm,
    SUM(FG3A) OVER prev5  AS prev5_3pa,
    SUM(FG3M) OVER prev10 AS prev10_3pm,
    -- ... (same pattern for prev20, next5, next10, next20)

    -- Season-to-date
    SUM(FG3M) OVER seasontodate AS std_3pm,
    SUM(FG3A) OVER seasontodate AS std_3pa

  FROM player_games
  WINDOW
    prev5 AS (
      PARTITION BY PLAYER_ID ORDER BY GAME_DATE, GAME_ID
      ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING
    ),
    -- ... (similar named windows for all lookback/lookahead periods)
    seasontodate AS (
      PARTITION BY PLAYER_ID ORDER BY GAME_DATE, GAME_ID
      ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
    )
)
SELECT * FROM base;
```

The named `WINDOW` clause in SQLite keeps things readable = you define the window once and reuse it. Way better than repeating the partition logic six times.

---

## Prediction & Evaluation (Python)

### The Two Models

Neither of these is fancy. That's kind of the point.

1. **Baseline (Season-to-Date Rate)**: Take the player's season-to-date 3P% (`std_3pm / std_3pa`) and multiply it by the known next-N attempts (`next{n}_3pa`). This represents the "steady state" assumption. A player is who their season says they are.

2. **Recent Form (Last-N Rate)**: Take the player's 3P% over the previous N games (`prev{n}_3pm / prev{n}_3pa`) and multiply by the same next-N attempts. This represents the "hot hand" assumption. Recent performance is more informative.

Both predictions use the same future attempt volume, so the only thing that differs is the *rate* estimate. That's what makes the comparison fair.

### Filtering

Rows are dropped if any of the following are true - you can't divide by zero and you can't evaluate without a target:

- The target (`next{n}_3pm`) is null
- Next-N attempts are null or zero
- Season-to-date attempts are null or zero
- Previous-N attempts are null or zero

This naturally removes early-season games (not enough history) and end-of-season games (not enough future data). It's a necessary tradeoff.

### Error Metric

We use **Mean Absolute Error (MAE)** — the average of `|predicted - actual|` across all valid player-game rows.

```python
df["err_baseline"] = (df["pred_baseline"] - df[target]).abs()
df["err_recent"]   = (df["pred_recent"]   - df[target]).abs()
```

We also compute `recent_minus_baseline` — if this is positive, the baseline wins. If negative, recent form wins.

### Rolling Windows Tested

We run the entire pipeline for N = 5, 10 and 20. So we're asking:

- Does last-5-game form predict the next 5 better than the season average?
- What about last 10 -> next 10?
- What about last 20 -> next 20?

---

## How to Interpret Results

The summary table will show something like:

| window | rows    | mae_baseline | mae_recent | recent_minus_baseline |
|--------|---------|--------------|------------|-----------------------|
| 5      | ...     | ...          | ...        | ...                   |
| 10     | ...     | ...          | ...        | ...                   |
| 20     | ...     | ...          | ...        | ...                   |

- The **higher** `recent_minus_baseline` is, the more accurate season-to-date rate is. Recent form is noise, more or less.
- The **lower** it is, the more recent form is actually carrying predictive signal beyond the seasonal average.
- If it's near **zero**, they're roughly equivalent - which is itself an interesting finding.

---

## Reflections & Next Steps

This is a V1 - intentionally simple. Some natural extensions:

- **Minutes filtering**: Should we exclude games where a player only played 5 minutes? Low-minute games might add noise. The SQL is set up to support this but we haven't enforced a threshold yet.
- **Player-level breakdowns**: The current analysis is aggregate. It'd be interesting to see *which players* are more predictable by recent form vs. baseline. Volume shooters might behave differently than role players.
- **Opponent-adjusted rates**: Some defenses are just better at contesting threes. Factoring in opponent defensive rating could sharpen predictions.

---

## Tools Used

- **SQLite** for data storage and feature engineering (window functions are underrated)
- **Python 3** with `pandas` and `sqlite3` for prediction and evaluation
- **DB Browser for SQLite** for exploratory SQL development