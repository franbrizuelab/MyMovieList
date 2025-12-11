USE FilmCatalog;

-- Create 3 admin users
INSERT INTO Users (userName, emailAddress, userRole)
VALUES
    ('Luis', 'luis@mail.com', 'admin'),
    ('Victor', 'victor@mail.com', 'admin'),
    ('Fran', 'fran@mail.com', 'admin');

-- Insert password hashes into UserPasswords
-- All three users share the password "password"

INSERT INTO UserPasswords (userId, passwordHash)
SELECT userId, SHA2('password', 256)
FROM Users
WHERE userName IN ('Luis', 'Victor', 'Fran');