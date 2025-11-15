"""Quick script to view database contents."""
import sqlite3
from pathlib import Path

# Connect to database
db_path = Path('instance/app.db')
if not db_path.exists():
    print(f"❌ Database not found at {db_path.absolute()}")
    exit(1)

print(f"✅ Database found: {db_path.absolute()}\n")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all tables
tables = cursor.execute(
    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
).fetchall()

print("=" * 60)
print("DATABASE TABLES")
print("=" * 60)
for table in tables:
    table_name = table[0]
    if table_name == 'sqlite_sequence':
        continue
    
    count = cursor.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
    print(f"📊 {table_name:<20} {count:>5} rows")

print("\n" + "=" * 60)
print("TABLE DETAILS")
print("=" * 60)

# Show sample data from each table
for table in tables:
    table_name = table[0]
    if table_name == 'sqlite_sequence':
        continue
    
    print(f"\n🔹 {table_name.upper()}")
    print("-" * 60)
    
    # Get column names
    columns = cursor.execute(f"PRAGMA table_info({table_name})").fetchall()
    col_names = [col[1] for col in columns]
    print("Columns:", ", ".join(col_names))
    
    # Get sample rows (first 3)
    rows = cursor.execute(f"SELECT * FROM {table_name} LIMIT 3").fetchall()
    if rows:
        print(f"\nSample data ({len(rows)} row(s)):")
        for i, row in enumerate(rows, 1):
            print(f"  Row {i}:")
            for col_name, value in zip(col_names, row):
                # Truncate long values
                str_value = str(value)
                if len(str_value) > 50:
                    str_value = str_value[:47] + "..."
                print(f"    {col_name}: {str_value}")
    else:
        print("  (No data)")

conn.close()

print("\n" + "=" * 60)
print("✅ Database inspection complete!")
print("=" * 60)
