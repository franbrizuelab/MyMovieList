import mysql.connector
import requests
import time

# Configuration
API_KEY = '5ca996952123cb47fb3751f95b9d5a97'
BASE_IMAGE_URL = "https://image.tmdb.org/t/p/w500"
DB_CONFIG = {
    'host': 'localhost',
    'user': 'CVML',
    'password': '114DWP2025',
    'database': 'FilmCatalog'
}

def get_cover_url(title):
    url = "https://api.themoviedb.org/3/search/movie"
    params = {
        'api_key': API_KEY,
        'query': title,
        'language': 'en-US'
    }
    try:
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data['results']:
                first_match = data['results'][0]
                poster_path = first_match.get('poster_path')
                if poster_path:
                    return f"{BASE_IMAGE_URL}{poster_path}"
    except Exception as e:
        print(f"Error fetching {title}: {e}")
    return None

def test_run():
    print("--- Starting Test Run (Fetching 5 movies) ---")
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Fetch 5 movies
        cursor.execute("SELECT movieId, title FROM Movies LIMIT 5")
        movies = cursor.fetchall()
        
        print(f"Found {len(movies)} movies to test.")
        
        for movie_id, title in movies:
            print(f"Processing ID: {movie_id}, Title: {title}")
            cover_url = get_cover_url(title)
            if cover_url:
                print(f"  -> Found Cover: {cover_url}")
            else:
                print(f"  -> No cover found.")
            time.sleep(0.2) # Be nice to the API
            
        conn.close()
        print("--- Test Run Complete ---")
        
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")

if __name__ == "__main__":
    test_run()
