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
    conn.commit()
    conn.close()
