import sqlite3

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('data/webauthnnotes.sqlite3')

# Create a new SQLite cursor
cursor = conn.cursor()

# Create a new table with the name 'users'
cursor.execute('''
CREATE TABLE `users` (`username` TEXT PRIMARY KEY UNIQUE NOT NULL, `credential_id` TEXT NOT NULL, `public_key` TEXT NOT NULL)
''')

# Commit the changes and close the connection
conn.commit()
conn.close()
