-- sportsbooks
CREATE TABLE IF NOT EXISTS sportsbooks (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    website_url VARCHAR(255)
);

-- games
CREATE TABLE IF NOT EXISTS games (
    id            SERIAL PRIMARY KEY,
    game_id       VARCHAR(255) NOT NULL,
    home_team     VARCHAR(50)  NOT NULL,
    away_team     VARCHAR(50)  NOT NULL,
    game_datetime TIMESTAMP    NOT NULL,
    game_status   VARCHAR(50)  NOT NULL,
    home_score    INTEGER,
    away_score    INTEGER,
    CONSTRAINT games_game_id_key UNIQUE (game_id)
);

-- odds
CREATE TABLE IF NOT EXISTS odds (
    id            SERIAL PRIMARY KEY,
    game_id       INTEGER      NOT NULL REFERENCES games(id),
    sportsbook_id INTEGER      NOT NULL REFERENCES sportsbooks(id),
    home_ml       NUMERIC(5,2) NOT NULL,
    away_ml       NUMERIC(5,2) NOT NULL,
    scraped_at    TIMESTAMP    NOT NULL
);

-- seed sportsbooks (skip if already present)
INSERT INTO sportsbooks (name, website_url) VALUES
    ('FanDuel',   'https://www.fanduel.com'),
    ('DraftKings','https://www.draftkings.com'),
    ('BetMGM',    'https://www.betmgm.com')
ON CONFLICT DO NOTHING;
