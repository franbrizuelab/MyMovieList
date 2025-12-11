from flask import Flask, request, session, jsonify
import mysql.connector
import hashlib  # for SHA-256 hashing
from datetime import datetime, timedelta #Get current time


app = Flask(__name__)
app.secret_key = "your_secret_key"

# ----------------------------------
# DATABASE CONNECTION
# ----------------------------------
# List of database configurations:
db_configs = [
    {   #Configuration 1
        'host': 'localhost',     # Fallback host
        'user': 'CVML',  # Fallback username
        'password': '114DWP2025',   # Fallback password
        'database': 'FilmCatalog'# Fallback database name
    }
]
# Helper function to get a DB connection
def get_db_connection():
    for config in db_configs:
        try:
            connection = mysql.connector.connect(**config)
            print(f"Connected to database using {config['user']}@{config['host']}")
            return connection
        except mysql.connector.Error as err:
            print(f"Failed to connect using {config['user']}@{config['host']}: {err}")
    raise Exception("All database connection attempts failed.")

# ----------------------------------
# ADMIN API ROUTES
# ----------------------------------

@app.route("/api/admin/movies")
def api_admin_movies():
    if 'user_role' not in session or session['user_role'] != 'admin':
        return jsonify({"error": "Access denied"}), 403

    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('query', '').strip()
    items_per_page = 30
    offset = (page - 1) * items_per_page

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if search_query:
        cursor.execute("""
            SELECT * FROM Movies
            WHERE title LIKE %s OR overview LIKE %s
            ORDER BY movieId ASC
            LIMIT %s OFFSET %s;
        """, (f"%{search_query}%", f"%{search_query}%", items_per_page, offset))
        movies = cursor.fetchall()

        cursor.execute("""
            SELECT COUNT(*) AS total FROM Movies
            WHERE title LIKE %s OR overview LIKE %s;
        """, (f"%{search_query}%", f"%{search_query}%"))
        total_movies = cursor.fetchone()['total']
    else:
        cursor.execute("""
            SELECT * FROM Movies
            ORDER BY movieId ASC
            LIMIT %s OFFSET %s;
        """, (items_per_page, offset))
        movies = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) AS total FROM Movies;")
        total_movies = cursor.fetchone()['total']

    cursor.close()
    conn.close()

    total_pages = (total_movies + items_per_page - 1) // items_per_page

    return jsonify({
        "movies": movies,
        "total_pages": total_pages,
        "current_page": page,
        "total_movies": total_movies
    })

@app.route("/api/admin/movie", methods=["POST"])
def api_admin_add_movie():
    if 'user_role' not in session or session['user_role'] != 'admin':
        return jsonify({"error": "Access denied"}), 403

    data = request.get_json()
    title = data.get("title", "").strip()
    tagline = data.get("tagline", "").strip()
    overview = data.get("overview", "").strip()
    release_date = data.get("releaseDate") or data.get("release_date")
    runtime = data.get("runtime")
    budget = data.get("budget", 0)
    language = data.get("language", "").strip()
    cover_url = data.get("coverUrl", "").strip()
    vote_average = data.get("voteAverage", 0)
    vote_count = data.get("voteCount", 0)

    if not title:
        return jsonify({"error": "Title is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO Movies (title, tagline, overview, releaseDate, runtime, budget, language, coverUrl, voteAverage, voteCount)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (title, tagline, overview, release_date, runtime, budget, language, cover_url, vote_average, vote_count))
        conn.commit()
        return jsonify({"success": True})
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route("/api/admin/movie/<int:movie_id>", methods=["PUT"])
def api_admin_update_movie(movie_id):
    if 'user_role' not in session or session['user_role'] != 'admin':
        return jsonify({"error": "Access denied"}), 403
    
    data = request.get_json()
    title = data.get("title")
    tagline = data.get("tagline")
    overview = data.get("overview")
    release_date = data.get("releaseDate") or data.get("release_date")
    runtime = data.get("runtime")
    budget = data.get("budget")
    language = data.get("language")
    cover_url = data.get("coverUrl")
    vote_average = data.get("voteAverage")
    vote_count = data.get("voteCount")

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE Movies
            SET title = %s, tagline = %s, overview = %s, releaseDate = %s, runtime = %s, budget = %s, language = %s, coverUrl = %s, voteAverage = %s, voteCount = %s
            WHERE movieId = %s
        """, (title, tagline, overview, release_date, runtime, budget, language, cover_url, vote_average, vote_count, movie_id))
        conn.commit()
        return jsonify({"success": True})
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route("/api/admin/movie/<int:movie_id>", methods=["DELETE"])
def api_admin_delete_movie(movie_id):
    if 'user_role' not in session or session['user_role'] != 'admin':
        return jsonify({"error": "Access denied"}), 403
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Movies WHERE movieId = %s", (movie_id,))
        conn.commit()
        return jsonify({"success": True})
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

# ----------------------------------
# API ROUTES (React Frontend)
# ----------------------------------

@app.route("/api/me")
def api_me():
    if 'user_id' in session:
        return jsonify({
            "authenticated": True,
            "user": {
                "id": session['user_id'],
                "username": session['username'],
                "role": session.get('user_role', 'normal')
            }
        })
    return jsonify({"authenticated": False})

@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json()
    username_or_email = data.get('username_or_email')
    password = data.get('password')
    
    if not username_or_email or not password:
        return jsonify({"error": "Missing credentials"}), 400

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT userId, userName, userRole
        FROM Users 
        WHERE userName = %s OR emailAddress = %s
    """, (username_or_email, username_or_email))
    user_row = cursor.fetchone()

    if not user_row:
        cursor.close()
        conn.close()
        return jsonify({"error": "Invalid credentials"}), 401

    cursor.execute("SELECT passwordHash FROM UserPasswords WHERE userId = %s", (user_row["userId"],))
    pass_row = cursor.fetchone()
    
    cursor.close()
    conn.close()

    if pass_row and pass_row["passwordHash"] == hashed_password:
        session['user_id'] = user_row["userId"]
        session['username'] = user_row["userName"]
        session['user_role'] = user_row["userRole"]
        session.permanent = True
        return jsonify({
            "success": True,
            "user": {
                "id": user_row["userId"],
                "username": user_row["userName"],
                "role": user_row["userRole"]
            }
        })
    
    return jsonify({"error": "Invalid credentials"}), 401

@app.route("/api/logout", methods=["POST"])
def api_logout():
    session.clear()
    return jsonify({"success": True})

@app.route("/api/home")
def api_home():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Tab 1: Ratings
    cursor.execute("""
        SELECT movieId, title, voteAverage, voteCount, overview, coverUrl
        FROM Movies
        WHERE voteAverage IS NOT NULL
        ORDER BY voteAverage DESC, voteCount DESC
        LIMIT 30;
    """)
    rating_table = cursor.fetchall()

    # Tab 2: Random Movies
    cursor.execute("""
        SELECT movieId, title, overview, coverUrl
        FROM Movies 
        ORDER BY RAND(UNIX_TIMESTAMP()) 
        LIMIT 30;
    """)
    random_table = cursor.fetchall()

     # Tab 3: Trending Movies
    one_week_ago = datetime.now() - timedelta(days=7)
    cursor.execute("""
        SELECT YEAR(releaseDate) AS releaseYear, m.movieId, m.title, m.overview, m.coverUrl, COUNT(c.commentId) AS commentCount
        FROM Movies m
        JOIN Comments c ON m.movieId = c.movieId
        WHERE c.timeStamp >= %s
        GROUP BY m.movieId, m.title, m.overview, m.coverUrl
        ORDER BY commentCount DESC
        LIMIT 30;
    """, (one_week_ago,))
    trending_table = cursor.fetchall()

    # Tab 4: Popular Movies
    cursor.execute("""
        SELECT m.movieId, m.title, m.overview, m.coverUrl, COUNT(c.commentId) AS totalComments
        FROM Movies m
        LEFT JOIN Comments c ON m.movieId = c.movieId
        GROUP BY m.movieId, m.title, m.overview, m.coverUrl
        ORDER BY totalComments DESC
        LIMIT 30;
    """)
    popular_table = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify({
        "top_rated": rating_table,
        "random": random_table,
        "trending": trending_table,
        "popular": popular_table
    })

@app.route("/api/movie/<int:movie_id>")
def api_movie_detail(movie_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT voteAverage, movieId, title, tagline, overview, releaseDate, language, runtime, budget, coverUrl
        FROM Movies
        WHERE movieId = %s
    """, (movie_id,))
    movie = cursor.fetchone()

    if not movie:
        cursor.close()
        conn.close()
        return jsonify({"error": "Movie not found"}), 404

    cursor.execute("""
        SELECT AVG(rating) as user_rating_average
        FROM Ratings
        WHERE movieId = %s
    """, (movie_id,))
    user_ratings = cursor.fetchone()
    user_rating_average = round(user_ratings['user_rating_average'], 2) if user_ratings and user_ratings['user_rating_average'] else 0

    user_rating = None
    if 'user_id' in session:
        cursor.execute("""
            SELECT rating FROM Ratings WHERE movieId = %s AND userId = %s
        """, (movie_id, session['user_id']))
        result = cursor.fetchone()
        user_rating = result['rating'] if result else None

    cursor.execute("""
        SELECT c.commentId, c.commentText, c.timeStamp, u.userName
        FROM Comments c
        JOIN Users u ON c.userId = u.userId
        WHERE c.movieId = %s
        ORDER BY c.timeStamp DESC
    """, (movie_id,))
    comments = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify({
        "movie": movie,
        "user_rating_average": user_rating_average,
        "user_rating": user_rating,
        "comments": comments
    })

@app.route("/api/search")
def api_search():
    query = request.args.get("query", "").strip()
    if not query:
        return jsonify([])

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    search_query = f"%{query}%"
    cursor.execute("""
        SELECT DISTINCT Movies.movieId, Movies.title, Movies.overview, Movies.releaseDate, Movies.voteAverage, Movies.coverUrl
        FROM Movies
        WHERE Movies.title LIKE %s
    """, (search_query,))
    title_matches = cursor.fetchall()

    cursor.execute("""
        SELECT DISTINCT Movies.movieId, Movies.title, Movies.overview, Movies.releaseDate, Movies.voteAverage, Movies.coverUrl
        FROM Movies
        JOIN MovieKeywords ON Movies.movieId = MovieKeywords.movieId
        JOIN Keywords ON MovieKeywords.keywordId = Keywords.keywordId
        WHERE Keywords.name LIKE %s
    """, (search_query,))
    keyword_matches = cursor.fetchall()

    cursor.close()
    conn.close()

    movie_ids = set()
    combined_results = []
    for movie in title_matches + keyword_matches:
        if movie["movieId"] not in movie_ids:
            movie_ids.add(movie["movieId"])
            combined_results.append(movie)
            
    return jsonify(combined_results)

@app.route("/api/signup", methods=["POST"])
def api_signup():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({"error": "Missing required fields"}), 400

    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT userName, emailAddress FROM Users WHERE userName = %s OR emailAddress = %s
        """, (username, email))
        existing_user = cursor.fetchall()

        if existing_user:
            for user in existing_user:
                if user['userName'] == username and user['emailAddress'] == email:
                    return jsonify({"error": "Username and email already exist"}), 400
                elif user['userName'] == username:
                    return jsonify({"error": "Username already exists"}), 400
                elif user['emailAddress'] == email:
                    return jsonify({"error": "Email already exists"}), 400

        cursor.execute("""
            INSERT INTO Users (userName, emailAddress, userRole)
            VALUES (%s, %s, %s)
        """, (username, email, 'normal'))

        new_user_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO UserPasswords (userId, passwordHash)
            VALUES (%s, %s)
        """, (new_user_id, hashed_password))

        conn.commit()
        return jsonify({"success": True})

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route("/api/movie/<int:movie_id>/rate", methods=["POST"])
def api_rate_movie(movie_id):
    if 'user_id' not in session:
        return jsonify({"error": "Login required"}), 401

    data = request.get_json()
    rating = data.get('rating')

    if rating is None or not (0 <= rating <= 5):
        return jsonify({"error": "Invalid rating"}), 400

    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT rating FROM Ratings WHERE movieId = %s AND userId = %s
        """, (movie_id, user_id))
        existing = cursor.fetchone()

        if existing:
            cursor.execute("""
                UPDATE Ratings SET rating = %s WHERE movieId = %s AND userId = %s
            """, (rating, movie_id, user_id))
        else:
            cursor.execute("""
                INSERT INTO Ratings (movieId, userId, rating) VALUES (%s, %s, %s)
            """, (movie_id, user_id, rating))

        conn.commit()
        return jsonify({"success": True})
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route("/api/movie/<int:movie_id>/comment", methods=["POST"])
def api_add_comment(movie_id):
    if 'user_id' not in session:
        return jsonify({"error": "Login required"}), 401

    data = request.get_json()
    comment_text = data.get('comment', '').strip()

    if not comment_text:
        return jsonify({"error": "Comment cannot be empty"}), 400

    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO Comments (movieId, userId, commentText)
            VALUES (%s, %s, %s)
        """, (movie_id, user_id, comment_text))
        conn.commit()
        return jsonify({"success": True})
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route("/api/delete_comment/<int:comment_id>", methods=["POST"])
def api_delete_comment(comment_id):
    if 'user_id' not in session:
        return jsonify({"error": "Login required"}), 401

    user_id = session['user_id']
    user_role = session.get('user_role', 'normal')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT userId FROM Comments WHERE commentId = %s", (comment_id,))
        comment = cursor.fetchone()

        if not comment:
            return jsonify({"error": "Comment not found"}), 404

        if comment['userId'] != user_id and user_role != 'admin':
            return jsonify({"error": "Permission denied"}), 403

        cursor.execute("DELETE FROM Comments WHERE commentId = %s", (comment_id,))
        conn.commit()
        return jsonify({"success": True})
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

# ----------------------------------
# MAIN
# ----------------------------------
if __name__ == "__main__":
    app.run(debug=True)
