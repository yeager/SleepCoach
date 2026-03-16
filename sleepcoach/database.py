"""SQLite database for sleep logs."""
import sqlite3
import os
from datetime import datetime, date

class SleepDatabase:
    def __init__(self):
        data_dir = os.path.join(os.path.expanduser("~"), ".local", "share", "sleepcoach")
        os.makedirs(data_dir, exist_ok=True)
        self.db_path = os.path.join(data_dir, "sleep.db")
        self.conn = sqlite3.connect(self.db_path)
        self._create_tables()

    def _create_tables(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS sleep_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                bedtime TEXT,
                waketime TEXT,
                quality INTEGER CHECK(quality BETWEEN 1 AND 5),
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS routine_steps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                step_order INTEGER NOT NULL,
                title TEXT NOT NULL,
                duration_minutes INTEGER DEFAULT 10,
                enabled INTEGER DEFAULT 1
            )
        """)
        self.conn.commit()
        # Default routine if empty
        count = self.conn.execute("SELECT COUNT(*) FROM routine_steps").fetchone()[0]
        if count == 0:
            defaults = [
                (1, "Turn off screens", 30),
                (2, "Dim the lights", 15),
                (3, "Brush teeth", 5),
                (4, "Read or listen to calm music", 20),
                (5, "Deep breathing exercises", 10),
                (6, "Lights out", 0),
            ]
            self.conn.executemany(
                "INSERT INTO routine_steps (step_order, title, duration_minutes) VALUES (?, ?, ?)",
                defaults
            )
            self.conn.commit()

    def log_sleep(self, bedtime, waketime, quality, notes=""):
        self.conn.execute(
            "INSERT INTO sleep_log (date, bedtime, waketime, quality, notes) VALUES (?, ?, ?, ?, ?)",
            (date.today().isoformat(), bedtime, waketime, quality, notes)
        )
        self.conn.commit()

    def get_logs(self, limit=30):
        return self.conn.execute(
            "SELECT date, bedtime, waketime, quality, notes FROM sleep_log ORDER BY date DESC LIMIT ?",
            (limit,)
        ).fetchall()

    def get_routine(self):
        return self.conn.execute(
            "SELECT id, step_order, title, duration_minutes, enabled FROM routine_steps ORDER BY step_order"
        ).fetchall()

    def close(self):
        self.conn.close()
