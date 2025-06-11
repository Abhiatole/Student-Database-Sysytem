from datetime import datetime
from app.db.database import get_db_connection

# Centralized logging configuration and helpers

def log_delivery(artefact_type, artefact_identifier, recipient, channel, status, error=''):
    """Logs a delivery attempt to the database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO delivery_logs (artefact_type, artefact_identifier, recipient_address, channel, delivery_status, timestamp, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (artefact_type, artefact_identifier, recipient, channel, status, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), error))
        conn.commit()
    except Exception as e:
        print(f"Failed to log delivery: {e}")
    finally:
        if 'conn' in locals():
            conn.close()
