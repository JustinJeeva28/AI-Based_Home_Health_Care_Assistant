import psycopg
from config.settings import DB_PARAMS

def connect_db(db_params=DB_PARAMS):
    """Connect to the database with the provided parameters."""
    return psycopg.connect(**db_params)

def create_reports_table():
    """Create the health_reports table if it does not exist."""
    conn = connect_db()
    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS health_reports (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                report TEXT
            )
        """)
        conn.commit()
    conn.close()
