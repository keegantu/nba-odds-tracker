# NBA Odds Tracker

A Flask web app that pulls live NBA moneyline odds from multiple sportsbooks,
stores them in a normalized PostgreSQL database, and displays them so you can
compare prices across books for each game (line shopping).

## What it does

- Fetches current NBA head-to-head odds from The Odds API across US sportsbooks
- Stores games, sportsbooks, and odds in a normalized relational schema
- Lists upcoming games with tip-off times converted from UTC to Eastern
- For each game, shows every sportsbook's odds side by side, converted from
  decimal to American format so different books are directly comparable

The point is line shopping: the same bet is priced differently across books, and
seeing them together shows which book offers the best price on a given side.

## Routes

| Route | Purpose |
|---|---|
| `/odds` | Fetch fresh odds from The Odds API and refresh the database |
| `/games` | List all games with tip-off times in Eastern |
| `/game/<id>` | Show every sportsbook's odds for one game, in American format |

## The interesting parts

**Normalized schema.** Instead of one flat table, data is split across three:
`games`, `sportsbooks`, and an `odds` table that links a game to a sportsbook
with that book's home and away moneyline. This avoids repeating team and book
names on every odds row, and makes cross-book comparison a clean join.

**Decimal to American conversion.** The Odds API returns decimal odds; American
odds are what most US bettors read. The `/game/<id>` route converts them: for
decimal odds under 2.0 (a favorite) the American price is `-100 / (decimal - 1)`,
and for 2.0 or above (an underdog) it's `(decimal - 1) * 100`, shown with a
leading `+`. Division-by-zero is guarded so a bad value can't crash the page.

**UTC to Eastern conversion.** The API returns game times in UTC. The `/games`
route converts each to US/Eastern with `pytz` and formats it for display, so
times read correctly for a US audience.

**Refresh on fetch.** Hitting `/odds` pulls the latest odds and rewrites the
current data, so the board reflects what the books are showing now rather than
stale lines.

## Database

```
games                          sportsbooks           odds
-----                          -----------           ----
id            (PK)             id     (PK)           id             (PK)
game_id       (API's id)       name                  game_id        (FK -> games.id)
home_team                      website_url           sportsbook_id  (FK -> sportsbooks.id)
away_team                                            home_ml
game_datetime                                        away_ml
game_status                                          scraped_at
home_score
away_score
```

`odds` is the bridge table: each row is one book's price for one game.

## Stack

Flask, PostgreSQL, psycopg2, requests, pytz, Jinja2 templates

## Setup

You need Python 3, a running PostgreSQL server, and a free API key from
[The Odds API](https://the-odds-api.com/).

1. Create the database and tables:

```bash
createdb nba_odds_tracker
psql -d nba_odds_tracker -f schema.sql
```

2. Seed the `sportsbooks` table with the books you want to track (the app looks
   up books by name and only stores odds for books already in that table).

3. Install dependencies:

```bash
pip install flask psycopg2-binary requests pytz
```

4. Set your API key as an environment variable:

```bash
export ODDS_API_KEY=your_key_here
```

5. Run the app:

```bash
python app.py
```

It starts on `http://localhost:5001`. Visit `/odds` to pull fresh data, then
`/games` to browse.

## Notes and next steps

- The API key should be read from an environment variable, not hardcoded. See the
  security note below.
- Database credentials are currently repeated in each route; a shared connection
  helper would be cleaner.
- A natural next feature is storing odds history over time (the schema already
  has `scraped_at`) to chart how a line moves as tip-off approaches.
