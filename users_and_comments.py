#!/usr/bin/env python3
# users_and_comments.py
#
# Seed the FilmCatalog database with:
# - 50 random users (common English names, excluding Luis, Victor, Fran)
# - For each user, 50 comments:
#     * 25 comments on a common set of movies, dated in the past 2 years
#       (2023-12-06 to 2025-12-05)
#     * 25 comments on random movies, dated in the last week
#       (2025-12-06 to 2025-12-12)
#
# All users have password "password" (SHA-256 hashed) stored in UserPasswords.

import random
import hashlib
from datetime import date, datetime, timedelta

import mysql.connector


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "CVML",
    "password": "114DWP2025",
    "database": "FilmCatalog",  # We will still issue USE FilmCatalog for clarity
}

NUM_USERS = 50
COMMON_COMMENTS_PER_USER = 25
RANDOM_COMMENTS_PER_USER = 25

# Recent week range: 2025-12-06 to 2025-12-12
RECENT_START = date(2025, 12, 6)
RECENT_END = date(2025, 12, 12)

# Previous 2 years range: 2023-12-06 to 2025-12-05
OLD_START = date(2023, 12, 6)
OLD_END = date(2025, 12, 5)

# All users share this plain-text password
PLAIN_PASSWORD = "password"


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def random_datetime_between(start_date: date, end_date: date) -> datetime:
    """Return a random datetime between start_date and end_date (inclusive)."""
    if start_date > end_date:
        raise ValueError("start_date must be <= end_date")

    delta_days = (end_date - start_date).days
    random_day = start_date + timedelta(days=random.randint(0, delta_days))

    seconds_in_day = 24 * 60 * 60
    random_seconds = random.randint(0, seconds_in_day - 1)

    dt = datetime.combine(random_day, datetime.min.time()) + timedelta(seconds=random_seconds)
    return dt


def get_connection():
    conn = mysql.connector.connect(**DB_CONFIG)
    return conn


# ---------------------------------------------------------------------------
# Main seeding logic
# ---------------------------------------------------------------------------

def main():
    # Common English names, at least 50, excluding Luis, Victor, Fran
    raw_names = [
        "Alice", "Bob", "Charlie", "David", "Emma", "Frank", "Grace", "Hannah",
        "Isabella", "Jack", "Karen", "Leo", "Mia", "Noah", "Olivia", "Paul",
        "Quinn", "Ryan", "Sophia", "Thomas", "Uma", "Wendy", "Xavier", "Yvonne",
        "Zach", "Adam", "Bella", "Chris", "Diana", "Ethan", "Fiona", "George",
        "Helena", "Ian", "Julia", "Kevin", "Lara", "Martin", "Nina", "Oscar",
        "Paula", "Robin", "Sara", "Tim", "Vera", "Will", "Zoe", "Aaron", "Brittany",
        "Carter", "Declan", "Eleanor", "Felix", "Gavin", "Hailey", "Iris", "Jasper",
        "Kylie", "Liam", "Mason", "Natalie"
    ]

    # Names to exclude (already admins)
    excluded = {"Luis", "Victor", "Fran"}

    # Filter and deduplicate while preserving order
    seen = set()
    names = []
    for n in raw_names:
        if n in excluded:
            continue
        if n not in seen:
            seen.add(n)
            names.append(n)

    if len(names) < NUM_USERS:
        raise RuntimeError(
            f"Not enough unique names after excluding {excluded}. "
            f"Have {len(names)}, need {NUM_USERS}."
        )

    # Take the first NUM_USERS names
    names = names[:NUM_USERS]

    print(f"Using {len(names)} names for users.")

    conn = get_connection()
    cursor = conn.cursor()

    # Make sure we are using the correct database
    cursor.execute("USE FilmCatalog;")

    # -----------------------------------------------------------------------
    # Fetch available movies
    # -----------------------------------------------------------------------
    cursor.execute("SELECT movieId FROM Movies;")
    movie_rows = cursor.fetchall()
    movie_ids = [row[0] for row in movie_rows]

    if len(movie_ids) == 0:
        raise RuntimeError("No movies found in Movies table. Seed movies first.")

    if len(movie_ids) < COMMON_COMMENTS_PER_USER + RANDOM_COMMENTS_PER_USER:
        print(
            "WARNING: Number of movies is less than COMMON + RANDOM per user. "
            "Random movie selection may contain overlaps."
        )

    # Choose common movies that all users will comment on
    common_count = min(COMMON_COMMENTS_PER_USER, len(movie_ids))
    common_movies = random.sample(movie_ids, common_count)
    print(f"Selected {len(common_movies)} common movies for all users.")

    # -----------------------------------------------------------------------
    # Insert / get users
    # -----------------------------------------------------------------------

    # Prepare password hash for all users (SHA-256 of "password")
    password_hash = hashlib.sha256(PLAIN_PASSWORD.encode("utf-8")).hexdigest()

    users = []  # list of (userId, userName)
    for name in names:
        username = name.lower()
        email = f"{username}@mail.com"

        # Check if this username already exists
        cursor.execute("SELECT userId FROM Users WHERE userName = %s;", (username,))
        row = cursor.fetchone()
        if row:
            # User already exists; reuse it
            user_id = row[0]
            print(f"User '{username}' already exists with userId={user_id}, reusing.")
        else:
            # Insert new user
            cursor.execute(
                """
                INSERT INTO Users (userName, emailAddress, userRole)
                VALUES (%s, %s, 'normal');
                """,
                (username, email),
            )
            user_id = cursor.lastrowid
            print(f"Inserted user '{username}' with userId={user_id}.")

        users.append((user_id, username))

        # Insert or update password in UserPasswords
        cursor.execute(
            """
            INSERT INTO UserPasswords (userId, passwordHash)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE passwordHash = VALUES(passwordHash);
            """,
            (user_id, password_hash),
        )

    conn.commit()
    print(f"Prepared {len(users)} users with password set.")

    # -----------------------------------------------------------------------
    # Generate comments
    # -----------------------------------------------------------------------

    comment_templates = [
        "Great movie!",
        "I liked this film.",
        "Not my favorite, but okay.",
        "Amazing acting and story.",
        "I would watch this again.",
        "Interesting concept but a bit slow.",
        "Loved the visuals.",
        "The ending was surprising.",
        "Solid movie overall.",
        "Could have been better.",
        "Excellent direction and acting.",
        "Storyline was engaging.",
        "The pacing felt off at times.",
        "Soundtrack was really good.",
        "I'd recommend this to friends."
    ]

    total_comments = 0

    for user_id, username in users:
        # Prepare random movies for this user
        # Prefer movies not in common_movies if enough exist
        available_for_random = [m for m in movie_ids if m not in common_movies]

        if len(available_for_random) >= RANDOM_COMMENTS_PER_USER:
            random_movies = random.sample(available_for_random, RANDOM_COMMENTS_PER_USER)
        else:
            # Not enough distinct movies, fall back to sampling from all
            random_movies = random.sample(movie_ids, RANDOM_COMMENTS_PER_USER)

        user_comments = []

        # 25 comments on common movies in the "old" range
        for movie_id in common_movies:
            ts = random_datetime_between(OLD_START, OLD_END)
            text = random.choice(comment_templates)
            user_comments.append((movie_id, user_id, text, ts))

        # 25 comments on random movies in the "recent" range
        for movie_id in random_movies:
            ts = random_datetime_between(RECENT_START, RECENT_END)
            text = random.choice(comment_templates)
            user_comments.append((movie_id, user_id, text, ts))

        # Optional: shuffle the comments for this user so timestamps/movies mix
        random.shuffle(user_comments)

        # Insert comments for this user
        cursor.executemany(
            """
            INSERT INTO Comments (movieId, userId, commentText, timeStamp)
            VALUES (%s, %s, %s, %s);
            """,
            user_comments,
        )

        total_comments += len(user_comments)
        print(f"Inserted {len(user_comments)} comments for user '{username}' (userId={user_id}).")

    conn.commit()
    print(f"Done. Inserted a total of {total_comments} comments for {len(users)} users.")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    main()
