# init_db.py

import sqlite3

conn = sqlite3.connect("movies.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS movies(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    genres TEXT,
    year INTEGER,
    poster TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS ratings(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    movie_id INTEGER,
    rating REAL
)
""")

movies = [
("The Shawshank Redemption","Drama",1994,"🏛️"),
("The Godfather","Crime,Drama",1972,"🤌"),
("The Dark Knight","Action,Thriller",2008,"🦇"),
("Pulp Fiction","Crime,Drama",1994,"💼"),
("Schindler's List","Drama,History",1993,"📋"),
("Inception","Sci-Fi,Thriller",2010,"🌀"),
("The Matrix","Sci-Fi,Action",1999,"💊"),
("Goodfellas","Crime,Drama",1990,"🔫"),
("Fight Club","Drama,Thriller",1999,"🥊"),
("Forrest Gump","Drama,Romance",1994,"🍫")
]

cur.executemany("""
INSERT INTO movies(title,genres,year,poster)
VALUES(?,?,?,?)
""", movies)

conn.commit()
conn.close()

print("Database created successfully")