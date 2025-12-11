import mysql.connector
import requests
import time
import csv
import os

# Configuration
API_KEY = '5ca996952123cb47fb3751f95b9d5a97'
BASE_IMAGE_URL = "https://image.tmdb.org/t/p/w500"
DB_CONFIG = {
    'host': 'localhost',
    'user': 'CVML',
    'password': '114DWP2025',
    'database': 'FilmCatalog'
}
OUTPUT_FILE = 'movie_covers.csv'

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

def main():
    print("--- Starting Full Cover Fetch ---")
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Fetch all movies
        print("Fetching movie list from database...")
        cursor.execute("SELECT movieId, title FROM Movies")
        movies = cursor.fetchall()
        total_movies = len(movies)
        print(f"Found {total_movies} movies.")
        
        # Open CSV file for writing
        with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            # No header needed for LOAD DATA usually, but let's keep it simple: ID, URL
            
            count = 0
            success_count = 0
            
            for movie_id, title in movies:
                count += 1
                print(f"[{count}/{total_movies}] Processing: {title}")
                
                cover_url = get_cover_url(title)
                
                if cover_url:
                    writer.writerow([movie_id, cover_url])
                    success_count += 1
                    print(f"  -> Found: {cover_url}")
                else:
                    # Write NULL or empty string? LOAD DATA handles \N as NULL usually.
                    # Or we just skip it and only update the ones we found.
                    # Let's skip rows with no cover to keep the CSV clean.
                    print(f"  -> No cover found.")
                
                # Flush every 10 records to ensure data is saved
                if count % 10 == 0:
                    csvfile.flush()
                    
                # Rate limiting: TMDB allows ~20-50 req/s, but let's be safe with 0.1s delay
                time.sleep(0.1)
                
        print(f"--- Complete. Found covers for {success_count}/{total_movies} movies. ---")
        print(f"Data saved to {os.path.abspath(OUTPUT_FILE)}")
        
        conn.close()
        
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
    except Exception as e:
        print(f"Unexpected Error: {e}")

if __name__ == "__main__":
    main()
