#!/usr/bin/env python3

import os
import sys

sys.path.append('.')

# Set the DATABASE_URL
os.environ["DATABASE_URL"] = "postgresql://smileadventureuser:smileadventurepass@localhost:5433/smileadventure"

try:
    import sqlalchemy as sa
    from src.db.session import engine

    inspector = sa.inspect(engine)
    tables = inspector.get_table_names()
    print('Tables:', tables)

    if 'users' in tables:
        columns = inspector.get_columns('users')
        print('Users table columns:')
        for col in columns:
            print(f'  - {col["name"]}: {col["type"]}')
    else:
        print('Users table does not exist')

    if 'specialties' in tables:
        columns = inspector.get_columns('specialties')
        print('Specialties table columns:')
        for col in columns:
            print(f'  - {col["name"]}: {col["type"]}')
            
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
