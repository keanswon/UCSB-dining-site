# file to convert csv to sql database

import sqlite3, csv

def col_def(h):
    if h == 'Iron_mg':
        return f'"{h}" REAL'
    # add more rules here, or default to REAL
    return f'"{h}" INTEGER'

def csv_to_sqlite(csv_path, db_path, table_name):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)

        # create table with all TEXT columns

        cols = ', '.join(col_def(h) for h in headers)
        cur.execute(f'CREATE TABLE IF NOT EXISTS "{table_name}" ({cols});')

        placeholders = ','.join('?' for _ in headers)
        cols_quoted = ','.join(f'"{h}"' for h in headers)
        sql = f'INSERT INTO "{table_name}" ({cols_quoted}) VALUES ({placeholders});'

        for row in reader:
            cur.execute(sql, row)

    conn.commit()
    conn.close()

# usage
csv_to_sqlite('full_export.csv', 'nutrition.db', 'nutrition')