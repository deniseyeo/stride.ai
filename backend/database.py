import os
import sqlite3
from pathlib import Path
from sqlite3 import Connection

project_root = Path(__file__).resolve().parents[1]
db_path = os.getenv("DATABASE_PATH", "backend/strava_app.db")
full_path = project_root / db_path


def get_db():
    conn = sqlite3.connect(full_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    _init_db(conn)
    try:
        yield conn
    finally:
        conn.close()


def _init_db(conn: Connection) -> None:
    """Initialize database tables if they don't exist"""
    cursor = conn.cursor()

    # Create strava_auth table
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS strava_auth (
        user_id TEXT PRIMARY KEY,
        access_token TEXT NOT NULL,
        refresh_token TEXT NOT NULL,
        expires_at INTEGER NOT NULL
    )
    """
    )

    # Create workouts table
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS workouts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        strava_id TEXT NOT NULL UNIQUE,
        user_id TEXT NOT NULL,
        name TEXT NOT NULL,    
        distance REAL NOT NULL,
        moving_time INTEGER NOT NULL,
        total_elevation_gain REAL NOT NULL,
        type TEXT NOT NULL,
        start_date TEXT NOT NULL,
        average_pace REAL NOT NULL,
        average_heartrate REAL,
        max_heartrate REAL
    )
    """
    )

    conn.commit()
