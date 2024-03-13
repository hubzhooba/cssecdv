import sqlite3
from contextlib import closing

# Connection to SQLite3 database (creating if it doesn't exist)
conn = sqlite3.connect("database.db",check_same_thread=False)

# Create a cursor object to execute SQL queries
cursor = conn.cursor()

# Commit changes (if any) to the database
conn.commit()


