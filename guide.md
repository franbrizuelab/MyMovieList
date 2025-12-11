First, we clone the GitHub repository with the command:
git clone git clone https://github.com/franbrizuelab/MyMovieList.git

Move into the newly cloned repository folder:
cd MyMovieList

Next, we need to run our virtual environment:
source venv/bin/activate

To install the connector:
pip install flask mysql-connector-python

Then open MySQL:
sudo mysql -u root -p


Step 1: Create a new user:
CREATE USER 'CVML'@'localhost' IDENTIFIED BY '114DWP2025';

If you don’t have any errors when executing the above command, skip this part. But if you get this error: Your password does not satisfy the current policy requirements, check the attached link. I’ve also run into this error because when I installed MySQL in a Virtual Machine, I did it in a “secure way”, so it asked me for a stronger password to perform modifications.


Grant privileges to the database:
GRANT ALL PRIVILEGES ON *.* TO 'CVML'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;

Verify the user:
SELECT user, host FROM mysql.user;
SHOW GRANTS FOR 'CVML'@'localhost';

Note: If you want to delete privileges on old databases, you can use:
REVOKE ALL PRIVILEGES ON `example_db`.* FROM 'CVML'@'localhost';

Step 2: Create the Database (The document is located in the folder /queries)
To run the script (go to the path on your computer)
cd ~/MyMovieList
Start MySQL from there (enable LOCAL INFILE just in case):
mysql -u CVML -p --local-infile=1
Remember, the password we used for this user is:
114DWP2025
Inside MySQL, run the scripts using a relative path to queries:
mysql> SOURCE queries/DBcreation.sql;
This will use the following script to create the database: DBcreation.sql
-- Create Database
CREATE DATABASE FilmCatalog;
-- #REST OF THE CODE...
To check if the database creation was successful, use:
SHOW DATABASES;
USE FilmCatalog;
SHOW TABLES;


Step 3: Database population
Inside MySQL, run the following script:
mysql> SOURCE queries/DBpopulation.sql;

Observation:
In case of errors due to not allowing the script to run from local files, proceed with the following steps for troubleshooting.
You need root access to modify the MySQL configuration file, which is typically one of these locations on Debian/Ubuntu systems: /etc/mysql/my.cnf or a file within /etc/mysql/conf.d/.
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf  # (Debian/Ubuntu)


Locate the [mysqld] section.
Add or modify the local-infile variable to enable it:
[mysqld]
# ... other settings ...
local-infile  =  1


You must restart the MySQL service for the configuration change to take effect:
sudo systemctl restart mysql
sudo mysql --local-infile=1 -u root -p FilmCatalog



Testing the connection to the database:
This is a small script to test the connection between the project and its database. It will use the user credentials created above, so it’s better if you just create the user, rather than modify each file that requires connections to the database. This will also be the credential used in the main.py file.

test.py:
import mysql.connector
db_config = {
	'host': 'localhost',
	'user': 'CVML',
	'password': '114DWP2025',
	'database': 'FilmCatalog'
}
try:
	conn = mysql.connector.connect(**db_config)
	print("Connection successful!")
	conn.close()
except mysql.connector.Error as err:
	print(f"Error: {err}")

Run the Python script:
cd ~/MyMovieList
python3 test.py
Remember, we need to run our virtual environment first:
source venv/bin/activate

Step 4: Frontend Setup (Vite + React)
The frontend is located in the `frontend` directory. You need Node.js installed.

Navigate to the frontend directory:
cd frontend

Install dependencies:
npm install

Start the development server:
npm run dev

The frontend will be available at http://localhost:5173 (or the port shown in the terminal).
Ensure the backend (Flask) is running on http://localhost:5000 for API requests to work.
