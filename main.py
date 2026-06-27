import sqlite3
import os
from flask import Flask, request, jsonify, session
from groq import Groq # (or whatever your Groq import looks like)

# 1. INITIALIZE THE FLASK APP FIRST!
app = Flask(__name__)
app.secret_key = "devil_secret_key_here" # Required for session management

DB_FILE = "database.db"

# 2. DATABASE INITIALIZATION
def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                max_win_streak INTEGER DEFAULT 0
            )
        ''')
        conn.commit()

init_db()

# 3. NOW YOUR APP ROUTES CAN SAFELY RUN Below
@app.route('/api/auth', methods=['POST'])
def handle_auth():
    # ... (rest of your handle_auth code) ...