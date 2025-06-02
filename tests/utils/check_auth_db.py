#!/usr/bin/env python3
import json
import os

import psycopg2
from psycopg2.extras import RealDictCursor

# Connect to Auth PostgreSQL database
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://smileadventureuser:smileadventurepass@localhost:5433/smileadventure")

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Get all tables
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    tables = cursor.fetchall()
    print("Tables in auth database:", [table['table_name'] for table in tables])

    # Check users table
    try:
        cursor.execute("SELECT * FROM auth_users")
        users = cursor.fetchall()
        print(f"\nFound {len(users)} users in auth database:")
        for user in users:
            print(f"  {dict(user)}")
    except psycopg2.Error as e:
        print(f"Error reading auth_users table: {e}")

    # Get column information for auth_users table
    try:
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'auth_users'
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        print("\nAuth users table structure:")
        for col in columns:
            print(f"  {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
    except psycopg2.Error as e:
        print(f"Error reading table structure: {e}")

except psycopg2.Error as e:
    print(f"Database connection error: {e}")
finally:
    if 'conn' in locals():
        conn.close()
