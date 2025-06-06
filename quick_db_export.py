#!/usr/bin/env python3
"""
Quick database export script
"""

import os
from datetime import datetime

import pandas as pd
import psycopg2


def export_db_tables():
    """Quick and dirty database export"""
      # Database connection
    conn_params = {
        'host': 'localhost',
        'port': 5433,
        'database': 'smileadventure',
        'user': 'smileadventureuser',
        'password': 'smileadventurepass'
    }
    
    try:
        # Connect to database
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        
        # Get all table names
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"Found {len(tables)} tables: {tables}")
        
        # Create export directory
        export_dir = f"db_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(export_dir, exist_ok=True)
        
        # Export each table
        for table in tables:
            print(f"Exporting {table}...")
            
            # Get data
            df = pd.read_sql(f"SELECT * FROM {table}", conn)
            
            # Save as CSV
            csv_file = os.path.join(export_dir, f"{table}.csv")
            df.to_csv(csv_file, index=False)
            
            # Print summary
            print(f"  → {table}: {len(df)} rows exported to {csv_file}")
            
            # Show first few rows
            if len(df) > 0:
                print(f"  → Sample data:")
                print(df.head(2).to_string())
                print()
        
        conn.close()
        print(f"\n✅ Export completed! Files saved in: {export_dir}")
        
    except Exception as e:
        print(f"❌ Export failed: {e}")

if __name__ == "__main__":
    export_db_tables()
