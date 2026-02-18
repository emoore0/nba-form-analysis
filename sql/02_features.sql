DROP VIEW IF EXISTS player_game_features;

CREATE VIEW player_game_features AS
WITH base AS (
  SELECT
    PLAYER_ID,
    PLAYER_NAME,
    GAME_DATE,
    GAME_ID,
    FG3M,
    FG3A,

    -- Previous windows (exclude current game)
    SUM(FG3M) OVER prev5  AS prev5_3pm,
    SUM(FG3A) OVER prev5  AS prev5_3pa,
    SUM(FG3M) OVER prev10 AS prev10_3pm,
    SUM(FG3A) OVER prev10 AS prev10_3pa,
    SUM(FG3M) OVER prev20 AS prev20_3pm,
    SUM(FG3A) OVER prev20 AS prev20_3pa,
	SUM(FG3M) OVER seasontodate  AS std_3pm,
    SUM(FG3A) OVER seasontodate  AS std_3pa,

    -- Next windows (exclude current game, look forward)
    SUM(FG3M) OVER next5  AS next5_3pm,
    SUM(FG3A) OVER next5  AS next5_3pa,
    SUM(FG3M) OVER next10 AS next10_3pm,
    SUM(FG3A) OVER next10 AS next10_3pa,
    SUM(FG3M) OVER next20 AS next20_3pm,
    SUM(FG3A) OVER next20 AS next20_3pa

  FROM player_games

  WINDOW
   prev5 AS (
      PARTITION BY PLAYER_ID
      ORDER BY GAME_DATE, GAME_ID
      ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING
    ),
    prev10 AS (
      PARTITION BY PLAYER_ID
      ORDER BY GAME_DATE, GAME_ID
      ROWS BETWEEN 10 PRECEDING AND 1 PRECEDING
    ),
    prev20 AS (
      PARTITION BY PLAYER_ID
      ORDER BY GAME_DATE, GAME_ID
      ROWS BETWEEN 20 PRECEDING AND 1 PRECEDING
    ),
    next5 AS (
      PARTITION BY PLAYER_ID
      ORDER BY GAME_DATE, GAME_ID
      ROWS BETWEEN 1 FOLLOWING AND 5 FOLLOWING
    ),
    next10 AS (
      PARTITION BY PLAYER_ID
      ORDER BY GAME_DATE, GAME_ID
      ROWS BETWEEN 1 FOLLOWING AND 10 FOLLOWING
    ),
    next20 AS (
      PARTITION BY PLAYER_ID
      ORDER BY GAME_DATE, GAME_ID
      ROWS BETWEEN 1 FOLLOWING AND 20 FOLLOWING
    ),
	seasontodate AS (
	  PARTITION BY PLAYER_ID
      ORDER BY GAME_DATE, GAME_ID
      ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
	)
)
SELECT * FROM base;