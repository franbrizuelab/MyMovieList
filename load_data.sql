USE FilmCatalog;

-- 1. Create a temporary table to hold the imported data
CREATE TEMPORARY TABLE TempCovers (
    movieId INTEGER,
    coverUrl TEXT
);

-- 2. Load data from the CSV file
-- Note: You might need to enable LOCAL_INFILE on both client and server.
-- If using mysql command line: mysql --local-infile=1 -u ...
LOAD DATA LOCAL INFILE 'movie_covers2.csv'
INTO TABLE TempCovers
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
(movieId, coverUrl);

-- 3. Update the main Movies table using the temporary table
UPDATE Movies m
JOIN TempCovers t ON m.movieId = t.movieId
SET m.coverUrl = t.coverUrl;

-- 4. Clean up (Temporary tables drop automatically, but good practice)
DROP TEMPORARY TABLE TempCovers;

SELECT COUNT(*) as UpdatedMovies FROM Movies WHERE coverUrl IS NOT NULL;
