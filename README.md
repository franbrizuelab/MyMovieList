# Film-Cataloging-System-DWP
Dynamic web Programming Final Project

![Alt Text](static/nycuflix.png)

## How to run the Application


1. Activate the environment 
```
source venv/bin/activate
```
2. Requirements:
Install mysql connector (ubuntu)
```
python3 -m pip install flask mysql-connector-python
```
3. Set up the database
open MySQL:
```
pyton3 setup_db.py
```

```
4. Run the python script
```
python3 main.py
```
5. Go to the link provided in the console (Backend API runs on http://localhost:5000)

6. Set up the Frontend (React + Vite)
Open a new terminal window and navigate to the frontend folder:
```
cd frontend
```
Install dependencies:
```
npm install
```
Start the development server:
```
npm run dev
```
The application will be available at http://localhost:5173. Ensure the backend is running for API requests to work.

### main.py
The primary backend script for the application, built using Flask. It manages routes, user authentication, movie data retrieval, and CRUD operations. Also handles database connections using MySQL.
- Key Features:
	- User login and signup functionalities.
	- Movie listing, search, and rating features.
	- Admin dashboard for managing movie data.

### Queries Folder
- DBcreation.sql
SQL script to create the database schema for the Film Cataloging System. Defines tables such as `Movies`, `Users`, `Comments`, `Ratings`, and others required for the system.

-  DBpopulation.sql
 SQL script to populate the database with initial data for testing and development. Includes sample movies, users, and other necessary records.

### Frontend Folder
Contains the React application source code, including components, pages, and API integration logic.

### Static Folder
Folder which contains images to display in the design of the page

### Templates folder
- admin_dashboard.html
- login.html
- signup.html
- search.html
- movie.html

### myenv folder
Environment folder containing dependencies and configurations for running the Flask app.

## Observation:
In case of errors due to not allowing the script to run from local files, proceed with the following steps for troubleshooting.
You need root access to modify the MySQL configuration file, which is typically one of these locations on Debian/Ubuntu systems: '/etc/mysql/my.cnf or a file within /etc/mysql/conf.d/'.
````
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf  # (Debian/Ubuntu)
```

Locate the [mysqld] section.
Add or modify the local-infile variable to enable it:
```
[mysqld]
# ... other settings ...
local-infile  =  1
```

You must restart the MySQL service for the configuration change to take effect:
```
sudo systemctl restart mysql
sudo mysql --local-infile=1 -u root -p FilmCatalog
````

