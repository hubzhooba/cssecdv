import sqlite3

# Connection to SQLite database
conn = sqlite3.connect('database.db',check_same_thread=False)

# Create a cursor object to execute SQL queries
cursor = conn.cursor()


# Close the connection

