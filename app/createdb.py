import sqlite3

# Connect to the database (creates the file if it doesn't exist)
connection = sqlite3.connect('users.db')

# Create a cursor object to execute SQL commands
cursor = connection.cursor()

# Create a table named 'User' with columns
cursor.execute('''
    CREATE TABLE User (
        id INTEGER PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password VARCHAR(100) NOT NULL
    )
''')

# Commit the changes and close the connection
connection.commit()
connection.close()
