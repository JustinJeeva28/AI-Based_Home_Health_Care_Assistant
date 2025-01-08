from datetime import datetime, timedelta
from database.database import connect_db
from memory.ConversationMemory import recall, store_conversations
from health.vitals import fetch_vitals_in_range
from emergency.EmergencyHandler import send_message
from config.settings import DB_PARAMS
from memory.ConversationMemory import stream_response
import ollama
import time

def generate_health_report(vitals):
    """Generate a health report based on the past vitals and medical history."""
    vitals_str = '\n'.join([f"Timestamp: {v[3]}, Heart Rate: {v[0]}, Blood Oxygen: {v[1]}, Temperature: {v[2]}" for v in vitals])
    prompt = f"Based on the following vitals data and the user's medical history, create a detailed health report and predict potential health conditions:\n\n{vitals_str}"
    
    recall(prompt)
    report = stream_response(prompt)
    
    conn_reports = connect_db()
    with conn_reports.cursor() as cursor:
        cursor.execute(
            'INSERT INTO health_reports(report) VALUES (%s)',
            (report,)
        )
        conn_reports.commit()
    conn_reports.close()

    print("Generated Health Report:", report)
    send_message(report)
    return report

def report_generation():
    """Generate a health report every 6 hours."""
    while True:
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=1)

        conn = connect_db()
        past_vitals = fetch_vitals_in_range(conn, start_time, end_time)
        conn.close()

        if past_vitals:
            generate_health_report(past_vitals)

        time.sleep(60)

def create_reports_table():
    """Create the health_reports table if it does not exist."""
    conn = connect_db(DB_PARAMS)
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