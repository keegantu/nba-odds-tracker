import psycopg2
import requests


from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route("/")
def home():
    return redirect(url_for('odds'))


@app.route("/odds")
def odds():
    conn = None
    cursor = None
    url = "https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?apiKey=859d56909fb14d5a3b972879e7e58b22&regions=us&markets=h2h"
    
    try:
        conn = psycopg2.connect(
            dbname="nba_odds_tracker",
            user="keegantu",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()
        
        response = requests.get(url)
        data = response.json()

        response = requests.get(url)
        data = response.json()

    
        cursor.execute("DELETE FROM odds")
        cursor.execute("DELETE FROM games")
        
        for game in data:
            home_team = game["home_team"]
            away_team = game["away_team"]
            api_game_id = game["id"]
            game_datetime = game["commence_time"]

            # Check if game already exists
            cursor.execute("SELECT id FROM games WHERE game_id = %s", (api_game_id,))
            existing_game = cursor.fetchone()
            
            if existing_game:
                db_game_id = existing_game[0]
                # Delete old odds for this game
                cursor.execute("DELETE FROM odds WHERE game_id = %s", (db_game_id,))
            else:
                # Insert new game
                cursor.execute(    
                    "INSERT INTO games(game_id, home_team, away_team, game_datetime, game_status) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                    (api_game_id, home_team, away_team, game_datetime, 'upcoming')
                )
                db_game_id = cursor.fetchone()[0]
            
            # Insert fresh odds for all bookmakers
            for bookmaker in game['bookmakers']:
                book_name = bookmaker['title']
                cursor.execute("SELECT id FROM sportsbooks WHERE name = %s", (book_name,))
                result = cursor.fetchone()
                
                if result:
                    sportsbook_id = result[0]
                    home_price = bookmaker['markets'][0]['outcomes'][0]['price']
                    away_price = bookmaker['markets'][0]['outcomes'][1]['price']
                    last_update = bookmaker['markets'][0]['last_update']
                    cursor.execute(
                        "INSERT INTO odds(game_id, sportsbook_id, home_ml, away_ml, scraped_at) VALUES (%s, %s, %s, %s, %s)",
                        (db_game_id, sportsbook_id, home_price, away_price, last_update)
                    )
            
        conn.commit()
        return redirect(url_for('games'))
    except Exception as error:
        return f"Error: {error}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route("/games")
def games():
        conn = None
        cursor = None

        try:
            conn = psycopg2.connect(
                dbname="nba_odds_tracker",
                user="keegantu",
                host="localhost",
                port="5432"
            )
            cursor = conn.cursor()

            cursor.execute(
                "SELECT * FROM games"
            )
            rows = cursor.fetchall()

            return render_template("games.html", games = rows)
        except Exception as error:
            return f"Error: {error}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

@app.route("/game/<int:id>")
def game_odds(id):
    conn = None
    cursor = None
    
    try:
        conn = psycopg2.connect(
            dbname="nba_odds_tracker",
            user="keegantu",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()

        cursor.execute(
            "SELECT home_team, away_team FROM games WHERE id = %s", (id,))
        game = cursor.fetchone()

        cursor.execute(
            "SELECT odds.*, sportsbooks.name FROM odds JOIN sportsbooks ON odds.sportsbook_id = sportsbooks.id WHERE odds.game_id = %s", 
            (id,)
        )
        odds_rows = cursor.fetchall()
        
        return render_template("game_odds.html", game=game, odds=odds_rows)
    except Exception as error:
        return f"Error: {error}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    app.run(debug=True, port=5001)

    


     