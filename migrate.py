import sqlite3
import os

DB_PATH = 'backend/clipping_platform.db'
if not os.path.exists(DB_PATH):
    print('DB not found, no migration needed.')
else:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    columns_to_add = [
        ('filename', 'VARCHAR DEFAULT ""'),
        ('original_filename', 'VARCHAR DEFAULT ""'),
        ('file_extension', 'VARCHAR DEFAULT ""'),
        ('mime_type', 'VARCHAR DEFAULT ""'),
        ('file_size_bytes', 'INTEGER DEFAULT 0'),
        ('fps', 'FLOAT DEFAULT NULL'),
        ('storage_path', 'VARCHAR DEFAULT ""'),
    ]
    for col_name, col_type in columns_to_add:
        try:
            cursor.execute(f'ALTER TABLE video_assets ADD COLUMN {col_name} {col_type}')
            print(f'Added {col_name}')
        except sqlite3.OperationalError as e:
            if 'duplicate column name' in str(e):
                print(f'Column {col_name} already exists')
            else:
                print(f'Error adding {col_name}: {e}')
                
    # Add campaigns table
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS campaigns (
                id VARCHAR PRIMARY KEY,
                title VARCHAR DEFAULT "Untitled Campaign",
                source VARCHAR DEFAULT "",
                brand VARCHAR DEFAULT "",
                campaign_url VARCHAR DEFAULT "",
                platforms JSON DEFAULT "[]",
                deadline DATETIME,
                payout VARCHAR DEFAULT "",
                reward_type VARCHAR DEFAULT "",
                rules_json JSON,
                summary_json JSON,
                worth_it_score_json JSON,
                raw_content VARCHAR DEFAULT "",
                confidence_score FLOAT DEFAULT 0.0,
                created_at DATETIME,
                status VARCHAR DEFAULT "imported"
            )
        ''')
        print("Ensured campaigns table exists")
    except sqlite3.OperationalError as e:
        print(f"Error creating campaigns table: {e}")
        
    conn.commit()
    conn.close()
