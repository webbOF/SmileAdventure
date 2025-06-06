#!/usr/bin/env python3
"""
Database Export Script for SmileAdventure PostgreSQL Database
Exports all tables structure and data to various formats
"""

import csv
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor

# Database configuration from .env
DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 5433,  # External port from docker-compose.yml
    'database': 'smileadventure',
    'user': 'smileadventureuser', 
    'password': 'smileadventurepass'
}

def create_export_directory():
    """Create timestamped export directory"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_dir = Path(f"database_exports_{timestamp}")
    export_dir.mkdir(exist_ok=True)
    return export_dir

def connect_to_database():
    """Establish PostgreSQL connection"""
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        print(f"✅ Connected to PostgreSQL database: {DATABASE_CONFIG['database']}")
        return conn
    except psycopg2.Error as e:
        print(f"❌ Error connecting to database: {e}")
        print("Make sure the database is running with: docker-compose up -d postgres-db")
        return None

def get_all_tables(cursor):
    """Get list of all tables in the database"""
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    tables = [row[0] for row in cursor.fetchall()]
    return tables

def get_table_structure(cursor, table_name):
    """Get table structure information"""
    cursor.execute("""
        SELECT 
            column_name,
            data_type,
            is_nullable,
            column_default,
            character_maximum_length
        FROM information_schema.columns 
        WHERE table_name = %s 
        ORDER BY ordinal_position
    """, (table_name,))
    
    columns = cursor.fetchall()
    structure = {
        'table_name': table_name,
        'columns': []
    }
    
    for col in columns:
        structure['columns'].append({
            'name': col[0],
            'type': col[1],
            'nullable': col[2] == 'YES',
            'default': col[3],
            'max_length': col[4]
        })
    
    return structure

def export_table_to_csv(cursor, table_name, export_dir):
    """Export table data to CSV"""
    try:
        cursor.execute(f"SELECT * FROM {table_name}")
        data = cursor.fetchall()
        
        if not data:
            print(f"  📝 Table {table_name} is empty")
            return 0
        
        # Get column names
        columns = [desc[0] for desc in cursor.description]
        
        # Write to CSV
        csv_file = export_dir / f"{table_name}.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(columns)  # Header
            writer.writerows(data)
        
        print(f"  📄 CSV: {table_name}.csv ({len(data)} rows)")
        return len(data)
        
    except Exception as e:
        print(f"  ❌ Error exporting {table_name} to CSV: {e}")
        return 0

def export_table_to_json(cursor, table_name, export_dir):
    """Export table data to JSON"""
    try:
        cursor.execute(f"SELECT * FROM {table_name}")
        data = cursor.fetchall()
        
        if not data:
            return 0
        
        # Convert to list of dictionaries
        columns = [desc[0] for desc in cursor.description]
        json_data = []
        
        for row in data:
            row_dict = {}
            for i, value in enumerate(row):
                # Handle datetime objects
                if hasattr(value, 'isoformat'):
                    row_dict[columns[i]] = value.isoformat()
                else:
                    row_dict[columns[i]] = value
            json_data.append(row_dict)
        
        # Write to JSON
        json_file = export_dir / f"{table_name}.json"
        with open(json_file, 'w', encoding='utf-8') as jsonfile:
            json.dump(json_data, jsonfile, indent=2, ensure_ascii=False)
        
        print(f"  📄 JSON: {table_name}.json ({len(data)} rows)")
        return len(data)
        
    except Exception as e:
        print(f"  ❌ Error exporting {table_name} to JSON: {e}")
        return 0

def export_table_to_sql(cursor, table_name, export_dir):
    """Export table data to SQL INSERT statements"""
    try:
        cursor.execute(f"SELECT * FROM {table_name}")
        data = cursor.fetchall()
        
        if not data:
            return 0
        
        # Get column names
        columns = [desc[0] for desc in cursor.description]
        
        sql_file = export_dir / f"{table_name}.sql"
        with open(sql_file, 'w', encoding='utf-8') as sqlfile:
            # Write table creation statement (simplified)
            sqlfile.write(f"-- Data dump for table: {table_name}\n")
            sqlfile.write(f"-- Generated on: {datetime.now().isoformat()}\n\n")
            
            # Write INSERT statements
            for row in data:
                values = []
                for value in row:
                    if value is None:
                        values.append('NULL')
                    elif isinstance(value, str):
                        # Escape single quotes
                        escaped_value = value.replace("'", "''")
                        values.append(f"'{escaped_value}'")
                    elif hasattr(value, 'isoformat'):
                        values.append(f"'{value.isoformat()}'")
                    else:
                        values.append(str(value))
                
                values_str = ', '.join(values)
                columns_str = ', '.join(columns)
                sqlfile.write(f"INSERT INTO {table_name} ({columns_str}) VALUES ({values_str});\n")
        
        print(f"  📄 SQL: {table_name}.sql ({len(data)} rows)")
        return len(data)
        
    except Exception as e:
        print(f"  ❌ Error exporting {table_name} to SQL: {e}")
        return 0

def export_database_schema(cursor, export_dir):
    """Export complete database schema"""
    try:
        # Get all table creation statements
        schema_file = export_dir / "schema.sql"
        with open(schema_file, 'w', encoding='utf-8') as f:
            f.write(f"-- SmileAdventure Database Schema\n")
            f.write(f"-- Generated on: {datetime.now().isoformat()}\n\n")
            
            # Get all tables
            tables = get_all_tables(cursor)
            
            for table_name in tables:
                f.write(f"\n-- Table: {table_name}\n")
                
                # Get table definition (simplified)
                cursor.execute("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name = %s 
                    ORDER BY ordinal_position
                """, (table_name,))
                
                columns = cursor.fetchall()
                f.write(f"CREATE TABLE {table_name} (\n")
                
                column_defs = []
                for col in columns:
                    col_def = f"    {col[0]} {col[1]}"
                    if col[2] == 'NO':
                        col_def += " NOT NULL"
                    if col[3]:
                        col_def += f" DEFAULT {col[3]}"
                    column_defs.append(col_def)
                
                f.write(",\n".join(column_defs))
                f.write("\n);\n")
        
        print(f"  📄 Schema exported to: schema.sql")
        
    except Exception as e:
        print(f"  ❌ Error exporting schema: {e}")

def generate_export_summary(export_dir, table_stats):
    """Generate export summary report"""
    summary_file = export_dir / "export_summary.md"
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("# Database Export Summary\n\n")
        f.write(f"**Export Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Database:** {DATABASE_CONFIG['database']}\n")
        f.write(f"**Total Tables:** {len(table_stats)}\n\n")
        
        f.write("## Tables Exported\n\n")
        f.write("| Table Name | Rows | Status |\n")
        f.write("|------------|------|--------|\n")
        
        total_rows = 0
        for table_name, row_count in table_stats.items():
            status = "✅ Success" if row_count >= 0 else "❌ Error"
            f.write(f"| {table_name} | {row_count} | {status} |\n")
            if row_count > 0:
                total_rows += row_count
        
        f.write(f"\n**Total Rows Exported:** {total_rows}\n\n")
        
        f.write("## Export Formats\n\n")
        f.write("- **CSV**: Comma-separated values for spreadsheet applications\n")
        f.write("- **JSON**: JavaScript Object Notation for web applications\n")
        f.write("- **SQL**: INSERT statements for database restoration\n")
        f.write("- **Schema**: Database structure definition\n\n")
        
        f.write("## Usage Examples\n\n")
        f.write("```bash\n")
        f.write("# Import data back to PostgreSQL\n")
        f.write("psql -U smileadventureuser -d smileadventure -f schema.sql\n")
        f.write("psql -U smileadventureuser -d smileadventure -f users.sql\n\n")
        f.write("# Load CSV in Python pandas\n")
        f.write("import pandas as pd\n")
        f.write("df = pd.read_csv('users.csv')\n")
        f.write("```\n")
    
    print(f"  📋 Summary report: export_summary.md")

def main():
    """Main export function"""
    print("🗃️  SmileAdventure Database Export Tool")
    print("=" * 50)
    
    # Create export directory
    export_dir = create_export_directory()
    print(f"📁 Export directory: {export_dir}")
    
    # Connect to database
    conn = connect_to_database()
    if not conn:
        sys.exit(1)
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get all tables
        tables = get_all_tables(cursor)
        print(f"\n📊 Found {len(tables)} tables:")
        for table in tables:
            print(f"  - {table}")
        
        # Export schema
        print(f"\n📐 Exporting database schema...")
        export_database_schema(cursor, export_dir)
        
        # Export each table
        print(f"\n📤 Exporting table data...")
        table_stats = {}
        
        for table_name in tables:
            print(f"\n📋 Processing table: {table_name}")
            
            # Export in multiple formats
            csv_rows = export_table_to_csv(cursor, table_name, export_dir)
            json_rows = export_table_to_json(cursor, table_name, export_dir)
            sql_rows = export_table_to_sql(cursor, table_name, export_dir)
            
            table_stats[table_name] = max(csv_rows, json_rows, sql_rows)
        
        # Generate summary
        print(f"\n📋 Generating export summary...")
        generate_export_summary(export_dir, table_stats)
          print(f"\n🎉 Export completed successfully!")
        print(f"📁 All files saved to: {export_dir}")
        print(f"\n📊 Export Statistics:")
        
        total_rows = sum(count for count in table_stats.values() if count > 0)
        successful_tables = sum(1 for count in table_stats.values() if count >= 0)
        
        print(f"  ✅ Tables processed: {successful_tables}/{len(tables)}")
        print(f"  📄 Total rows exported: {total_rows}")
        print(f"  📁 Files created: {len(list(export_dir.glob('*')))}")
        
    except Exception as e:
        print(f"❌ Export failed: {e}")
        import traceback
        print("Full error details:")
        traceback.print_exc()
        
    finally:
        if conn:
            conn.close()
            print(f"\n🔌 Database connection closed")

if __name__ == "__main__":
    # Check dependencies
    try:
        import pandas as pd
        import psycopg2
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Install with: pip install psycopg2-binary pandas")
        sys.exit(1)
    
    main()
