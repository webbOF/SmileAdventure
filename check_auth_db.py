#!/usr/bin/env python3
import json
import sqlite3

# Connect to Auth database
conn = sqlite3.connect('auth.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables in auth.db:", tables)

# Check users table
try:
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    print(f"\nFound {len(users)} users in auth.db:")
    for user in users:
        print(f"  {user}")
        
    # Get column names
    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()
    print("\nUsers table structure:")
    for col in columns:
        print(f"  {col}")
        
except Exception as e:
    print(f"Error accessing users table: {e}")

conn.close()
