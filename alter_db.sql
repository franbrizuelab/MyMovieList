USE FilmCatalog;

-- Add the coverUrl column if it doesn't exist
-- We use TEXT to be safe with URL lengths, though VARCHAR(255) is usually enough.
ALTER TABLE Movies ADD COLUMN coverUrl TEXT;
