import sqlite3

# Connect to (or create) the database file
conn = sqlite3.connect('prototype.db')
cursor = conn.cursor()

# Create the table with the updated columns

cursor.execute('''
    DELETE FROM QUESTIONS
''')
# Commit changes and close
conn.commit()
conn.close()

print("Database and table created successfully.")