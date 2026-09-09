import sqlite3
import os
from flask import g
from werkzeug.security import generate_password_hash
from config import Config

def get_db():
    """Opens a new database connection if there is none yet for the current application context."""
    if 'db' not in g:
        db_path = Config.DATABASE
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        g.db = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
    return g.db

def get_db_connection():
    """Returns a standalone database connection for background or training scripts."""
    db_path = Config.DATABASE
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    return conn

def close_db(e=None):
    """Closes the database again at the end of the request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Initializes the database using schema.sql and creates default admin."""
    conn = get_db_connection()
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    with open(schema_path, 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
    
    # Check if demo admin exists
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", (Config.DEMO_ADMIN_EMAIL,))
    user = cursor.fetchone()
    if not user:
        pwd_hash = generate_password_hash(Config.DEMO_ADMIN_PASSWORD)
        cursor.execute(
            "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
            ("QuaNet Administrator", Config.DEMO_ADMIN_EMAIL, pwd_hash, "Admin")
        )
        conn.commit()
    conn.close()

def query_db(query, args=(), one=False):
    """Helper to query database and return dictionary rows."""
    db = get_db()
    cur = db.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (dict(rv[0]) if rv else None) if one else [dict(row) for row in rv]

def execute_db(query, args=()):
    """Helper to execute INSERT/UPDATE/DELETE and commit."""
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    last_id = cur.lastrowid
    cur.close()
    return last_id
