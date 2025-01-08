from database.database import connect_db
from emergency.EmergencyHandler import make_emergency_call 
from config.settings import *
import time

def get_latest_vitals(conn):
    """Fetch the latest vitals from the database."""
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT heart_rate, blood_oxygen_level, temperature, timestamp
            FROM vitals
            ORDER BY timestamp DESC
            LIMIT 1
        """)
        return cursor.fetchone()

def fetch_vitals_in_range(conn, start_time, end_time):
    """Fetch vitals recorded between start_time and end_time."""
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT heart_rate, blood_oxygen_level, temperature, timestamp
            FROM vitals
            WHERE timestamp BETWEEN %s AND %s
            ORDER BY timestamp ASC
        """, (start_time, end_time))
        return cursor.fetchall()

def check_vitals():
    """Check the latest vitals and trigger an emergency call if needed."""
    conn = connect_db()
    latest_vitals = get_latest_vitals(conn)
    conn.close()

    if latest_vitals:
        heart_rate, blood_oxygen_level, temperature, timestamp = latest_vitals

        if heart_rate < LOW_HEART_RATE_THRESHOLD or heart_rate > HIGH_HEART_RATE_THRESHOLD:
            make_emergency_call("Patient Heart rate is either Extremely low or higher than normal.")
            print(heart_rate)
        if blood_oxygen_level < LOW_OXYGEN_THRESHOLD:
            make_emergency_call("Patient feeling Breathlessness.")
            print(blood_oxygen_level)
        if temperature > HIGH_TEMPERATURE_THRESHOLD:
            make_emergency_call("Patient feeling cold. Patient is very Sick.")
            print(temperature)

def vitals_check_loop():
    """Loop to check vitals in a separate thread."""
    while True:
        check_vitals()
        time.sleep(10)