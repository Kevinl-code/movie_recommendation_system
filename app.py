from flask import Flask, render_template, request, jsonify
import sqlite3
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
import sqlite3
import os

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DB_PATH = os.path.join(
    BASE_DIR,
    "movies.db"
)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS movies(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        genre TEXT,
        description TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS ratings(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        movie_id INTEGER,
        rating INTEGER,
        review TEXT
    )
    """)

    cur.execute("SELECT COUNT(*) FROM movies")
    count = cur.fetchone()[0]

    if count == 0:
        sample_movies = [
            ("Inception","Sci-Fi","Dreams inside dreams"),
            ("Interstellar","Sci-Fi","Space exploration and time"),
            ("The Dark Knight","Action","Batman vs Joker"),
            ("Avatar","Adventure","Pandora world"),
            ("Titanic","Romance","Love story on ship"),
            ("Joker","Drama","Origin of Joker"),
            ("Avengers Endgame","Action","Marvel heroes unite"),
            ("Doctor Strange","Fantasy","Mystic arts"),
            ("The Matrix","Sci-Fi","Virtual reality"),
            ("John Wick","Action","Revenge thriller")
        ]

        cur.executemany(
            "INSERT INTO movies(title,genre,description) VALUES(?,?,?)",
            sample_movies
        )

    conn.commit()
    conn.close()


def recommend(movie_title):

    conn = get_connection()

    df = pd.read_sql_query(
        "SELECT * FROM movies",
        conn
    )

    conn.close()

    df["features"] = df["genre"] + " " + df["description"]

    vectorizer = TfidfVectorizer(stop_words="english")

    matrix = vectorizer.fit_transform(df["features"])

    similarity = cosine_similarity(matrix)

    if movie_title not in df["title"].values:
        return []

    index = df[df["title"] == movie_title].index[0]

    scores = list(enumerate(similarity[index]))

    scores = sorted(
        scores,
        key=lambda x: x[1],
        reverse=True
    )

    recommendations = []

    for i in scores[1:6]:
        recommendations.append(df.iloc[i[0]]["title"])

    return recommendations


@app.route("/")
def home():

    conn = get_connection()

    movies = conn.execute(
        "SELECT * FROM movies"
    ).fetchall()

    trending = conn.execute("""
        SELECT movies.title,
       AVG(ratings.rating) avg_rating
FROM ratings
JOIN movies
ON movies.title = ratings.movie
GROUP BY movies.title
ORDER BY avg_rating DESC
LIMIT 5
    """).fetchall()

    conn.close()

    return render_template(
        "index.html",
        movies=movies,
        trending=trending
    )


@app.route("/search")
def search():

    query = request.args.get("query","")

    conn = get_connection()

    movies = conn.execute(
        "SELECT * FROM movies WHERE title LIKE ?",
        ('%' + query + '%',)
    ).fetchall()

    conn.close()

    return jsonify(
        [dict(movie) for movie in movies]
    )


@app.route("/recommend", methods=["POST"])
def get_recommendation():

    movie = request.form["movie"]

    recommendations = recommend(movie)

    return jsonify(recommendations)


@app.route("/rate", methods=["POST"])
def rate():

    movie_id = request.form["movie_id"]
    rating = request.form["rating"]
    review = request.form["review"]

    conn = get_connection()

    conn.execute("""
        INSERT INTO ratings(
        movie_id,
        rating,
        review
        )
        VALUES(?,?,?)
    """,(movie_id,rating,review))

    conn.commit()
    conn.close()

    return jsonify({"status":"success"})


if __name__ == "__main__":
    initialize_database()
    import os
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
