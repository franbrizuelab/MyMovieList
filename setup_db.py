import os
import subprocess
import getpass
import sys

def run_sql_file(filename, user, password, db_name=None):
    """Executes a specific SQL file using mysql command line."""
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found.")
        return

    print(f"  -> Executing {filename}...")
    
    # Construct the command. 
    # We use string formatting for the shell command to handle the input redirection (<) easily.
    # Note: --local-infile=1 is crucial for your DBpopulation.sql
    cmd = f"mysql -u {user} -p'{password}' --local-infile=1"
    
    if db_name:
        cmd += f" {db_name}"
        
    cmd += f" < {filename}"

    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError:
        print(f"Failed to execute {filename}")
        sys.exit(1)

def main():
    print("--- FilmCatalog Database Setup Automation ---")

    # 1. Operations requiring ROOT access
    # We ask for the root password once so we don't have to hardcode it or enter it manually for sudo
    print("Please enter your MySQL ROOT password to initialize the 'CVML' user.")
    root_pass = getpass.getpass("MySQL Root Password: ")

    create_user_sql = """
    DROP USER IF EXISTS 'CVML'@'localhost';
    CREATE USER 'CVML'@'localhost' IDENTIFIED BY '114DWP2025';
    GRANT ALL PRIVILEGES ON *.* TO 'CVML'@'localhost' WITH GRANT OPTION;
    FLUSH PRIVILEGES;
    """

    print("\n[1/3] Creating User 'CVML'...")
    try:
        # We pass the SQL commands directly to the mysql process via stdin
        subprocess.run(
            ["mysql", "-u", "root", f"-p{root_pass}"], 
            input=create_user_sql, 
            text=True, 
            check=True
        )
    except subprocess.CalledProcessError:
        print("Error: Failed to create user. Check your root password.")
        sys.exit(1)

    # 2. Operations using the new CVML user
    print("\n[2/3] Building Database and Populating Tables...")
    cvml_user = "CVML"
    cvml_pass = "114DWP2025"

    # Define the order of execution
    scripts = [
        "queries/DBcreation.sql",   # Creates the DB and Tables
        "queries/DBpopulation.sql", # Loads CSV data
        "queries/admin.sql"         # Any admin specific setup
    ]

    for script in scripts:
        run_sql_file(script, cvml_user, cvml_pass)

# 3. Run the final Python script using the VENV
    print("\n[3/3] Running 'users_and_comments.py'...")
    
    # Path to the python executable inside the virtual environment
    # On Linux/MacOS, it is usually "venv/bin/python" or "venv/bin/python3"
    venv_python = "venv/bin/python3" 

    if os.path.exists("users_and_comments.py"):
        if os.path.exists(venv_python):
            try:
                # We call the venv python directly
                subprocess.run([venv_python, "users_and_comments.py"], check=True)
            except subprocess.CalledProcessError:
                print("Error running users_and_comments.py")
        else:
            print(f"Error: Virtual environment not found at '{venv_python}'.")
            print("Please create it with: python3 -m venv venv")
    else:
        print("Warning: 'users_and_comments.py' was not found in the current directory.")

    print("\n--- Setup Complete! ---")

if __name__ == "__main__":
    main()
