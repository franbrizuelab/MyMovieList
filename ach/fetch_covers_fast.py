import mysql.connector
import requests
import csv
import time
import threading
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

# --- Configuration ---
API_KEY = '5ca996952123cb47fb3751f95b9d5a97'
BASE_IMAGE_URL = "https://image.tmdb.org/t/p/w500"
DB_CONFIG = {
    'host': 'localhost',
    'user': 'CVML',
    'password': '114DWP2025',
    'database': 'FilmCatalog'
}
OUTPUT_FILE = 'movie_covers2.csv'
MAX_WORKERS = 50  # Number of parallel threads (Adjust if hitting 429 errors too often)

# Lock for writing to CSV safely from multiple threads
csv_lock = threading.Lock()

def get_cover_url(movie_id, title):
    """
    Fetches the cover URL for a single movie.
    Handles rate limiting (429) with retries.
    """
    url = "https://api.themoviedb.org/3/search/movie"
    params = {
        'api_key': API_KEY,
        'query': title,
        'language': 'en-US'
    }
    
    retries = 3
    backoff = 1  # Start with 1 second wait on error
    
    for attempt in range(retries):
        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data['results']:
                    # Get the first result's poster path
                    poster_path = data['results'][0].get('poster_path')
                    if poster_path:
                        return movie_id, f"{BASE_IMAGE_URL}{poster_path}"
                return movie_id, None # Movie found but no poster, or no results
            
            elif response.status_code == 429:
                # Rate limit exceeded
                retry_after = int(response.headers.get('Retry-After', backoff))
                # print(f"Rate limit hit for '{title}'. Sleeping {retry_after}s...")
                time.sleep(retry_after)
                backoff *= 2 # Exponential backoff for next try
                continue
                
            else:
                # Server error or other issue
                return movie_id, None

        except requests.RequestException:
            # Network timeout or connection error
            time.sleep(backoff)
            backoff *= 2
            
    return movie_id, None

def main():
    print(f"--- Starting Fast Cover Fetch (Threads: {MAX_WORKERS}) ---")
    
    # 1. Fetch all movies from Database
    try:
        print("Connecting to database...")
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT movieId, title FROM Movies")
        movies = cursor.fetchall() # Returns list of (id, title)
        conn.close()
    except Exception as e:
        print(f"Database Error: {e}")
        return

    total_movies = len(movies)
    print(f"Found {total_movies} movies. Starting workers...")

    # 2. Process in parallel
    found_count = 0
    processed_count = 0
    start_time = time.time()
    
    # Open CSV file for writing
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Use ThreadPoolExecutor to manage concurrent tasks
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            # Submit all tasks to the pool
            future_to_movie = {executor.submit(get_cover_url, m[0], m[1]): m for m in movies}
            
            # Process results as they complete
            for future in as_completed(future_to_movie):
                processed_count += 1
                movie_id, cover_url = future.result()
                
                if cover_url:
                    with csv_lock:
                        writer.writerow([movie_id, cover_url])
                        # Flush periodically to ensure data is written to disk
                        if found_count % 50 == 0:
                            csvfile.flush()
                    found_count += 1
                
                # Progress logging
                if processed_count % 100 == 0:
                    elapsed = time.time() - start_time
                    rate = processed_count / elapsed if elapsed > 0 else 0
                    
                    remaining = total_movies - processed_count
                    eta_seconds = remaining / rate if rate > 0 else 0
                    eta_str = time.strftime("%H:%M:%S", time.gmtime(eta_seconds))
                    
                    print(f"Progress: {processed_count}/{total_movies} ({rate:.1f} movies/sec) | Found: {found_count} | ETA: {eta_str}")

    print(f"\n--- Complete! ---")
    print(f"Total Found: {found_count}/{total_movies}")
    print(f"Data saved to: {os.path.abspath(OUTPUT_FILE)}")
    print(f"Next Step: Run 'mysql ... < load_data.sql' to import.")

if __name__ == "__main__":
    main()
