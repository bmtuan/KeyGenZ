# key_manager.py
import base64
import hashlib
import hmac
import sqlite3
import time
import uuid
from datetime import datetime, timedelta


class KeyManager:
    def __init__(self, db_path="activation_keys.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.create_table()

    def create_table(self):
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS activation_keys (
                id TEXT PRIMARY KEY,
                name TEXT,
                key TEXT UNIQUE,
                created_date TEXT,
                activate_expired_date TEXT,
                app_expired_date TEXT
            )
        """
        )
        self.conn.commit()

    def load_keys(self):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM activation_keys ORDER BY created_date DESC")
        return [dict(row) for row in cur.fetchall()]

    def close(self):
        try:
            self.conn.close()
        except Exception:
            pass

    @staticmethod
    def generate_key(secret_key: str, ttl_seconds: int, ttl_seconds_app: int) -> str:
        """
        Generate a key using a secret key, TTL, and app-specific TTL.
        """
        current_time = int(time.time())
        expiration_time = current_time + int(ttl_seconds)
        app_expiration_time = current_time + int(ttl_seconds_app)
        data = f"{current_time}:{expiration_time}:{app_expiration_time}"
        signature = hmac.new(
            secret_key.encode(), data.encode(), hashlib.sha256
        ).digest()

        encoded_data = base64.urlsafe_b64encode(data.encode()).decode()
        encoded_signature = base64.urlsafe_b64encode(signature).decode()
        return f"{encoded_data}:{encoded_signature}"

    def add_key_row(
        self, name: str, secret_key: str, ttl_seconds: int, validity_days: int
    ):
        if not name.strip() or not secret_key.strip():
            raise ValueError("All fields are required.")

        ttl_app_seconds = int(validity_days) * 24 * 60 * 60
        new_key = self.generate_key(secret_key, int(ttl_seconds), ttl_app_seconds)

        now = datetime.now()
        created_date = now.strftime("%Y-%m-%d %H:%M:%S")
        activate_expired_date = (now + timedelta(seconds=int(ttl_seconds))).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        app_expired_date = (now + timedelta(seconds=ttl_app_seconds)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        cur = self.conn.cursor()
        cur.execute(
            """INSERT INTO activation_keys
               (id, name, key, created_date, activate_expired_date, app_expired_date)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                str(uuid.uuid4()),
                name.strip(),
                new_key,
                created_date,
                activate_expired_date,
                app_expired_date,
            ),
        )
        self.conn.commit()

    def delete_key(self, key_id: str):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM activation_keys WHERE id = ?", (key_id,))
        self.conn.commit()