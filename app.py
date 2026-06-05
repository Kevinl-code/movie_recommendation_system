from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
CORS(app)
import sqlite3

def get_db():
    conn = sqlite3.connect("movies.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/movies")
def get_movies():

    conn = get_db()

    movies = conn.execute("""
        SELECT *
        FROM movies
    """).fetchall()

    conn.close()

    return jsonify([dict(row) for row in movies])
@app.route("/movies/search")
def search_movies():

    q = request.args.get("q","")

    conn = get_db()

    rows = conn.execute("""
    SELECT *
    FROM movies
    WHERE title LIKE ?
    """,(f"%{q}%",)).fetchall()

    conn.close()

    return jsonify(
        [dict(r) for r in rows]
    )

@app.route("/top-rated")
def top_rated():

    conn = get_db()

    rows = conn.execute("""
    SELECT m.*,
           AVG(r.rating) avg_rating
    FROM movies m
    JOIN ratings r
      ON m.id=r.movie_id
    GROUP BY m.id
    ORDER BY avg_rating DESC
    LIMIT 8
    """).fetchall()

    conn.close()

    return jsonify(
        [dict(r) for r in rows]
    )

@app.route("/user/create", methods=["POST"])
def create_user():

    conn = get_db()

    cur = conn.cursor()

    cur.execute("""
        INSERT INTO users(username)
        VALUES(?)
    """, ("Guest",))

    conn.commit()

    user_id = cur.lastrowid

    conn.close()

    return jsonify({
        "user_id": user_id
    })
@app.route("/user/<int:uid>/rate", methods=["POST"])
def rate_movie(uid):

    body = request.get_json()

    movie_id = body["movie_id"]
    rating = body["rating"]

    conn = get_db()

    conn.execute("""
        INSERT INTO ratings(
            user_id,
            movie_id,
            rating
        )
        VALUES(?,?,?)
    """,(uid,movie_id,rating))

    conn.commit()

    conn.close()

    return jsonify({
        "status":"ok"
    })

def load_ratings():

    conn = get_db()

    rows = conn.execute("""
        SELECT user_id,movie_id,rating
        FROM ratings
    """).fetchall()

    conn.close()

    return rows

def build_matrix():

    ratings = load_ratings()

    users = sorted(set(r["user_id"] for r in ratings))
    movies = sorted(set(r["movie_id"] for r in ratings))

    user_map = {
        u:i
        for i,u in enumerate(users)
    }

    movie_map = {
        m:i
        for i,m in enumerate(movies)
    }

    rows=[]
    cols=[]
    data=[]

    for r in ratings:

        rows.append(
            user_map[r["user_id"]]
        )

        cols.append(
            movie_map[r["movie_id"]]
        )

        data.append(
            float(r["rating"])
        )

    matrix = csr_matrix(
        (data,(rows,cols)),
        shape=(len(users),len(movies))
    )

    return matrix,users,movies

if __name__ == "__main__":
    app.run(debug=True, port=5000)
