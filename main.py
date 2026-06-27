import sqlite3
from flask import Flask, request, jsonify, session

# ... (Keep your existing Flask app init and Groq chat API logic here) ...

DB_FILE = "database.db"

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        # Create users table with high score win streak tracking
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

# --- REAL REGISTRATION / LOGIN ENDPOINTS ---
@app.route('/api/auth', methods=['POST'])
def handle_auth():
    data = request.json or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    action = data.get('action') # 'login' or 'register'

    if not username or not password:
        return jsonify({"error": "Missing fields"}), 400

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        
        if action == 'register':
            try:
                cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                conn.commit()
                return jsonify({"message": "Account forged!"}), 201
            except sqlite3.IntegrityError:
                return jsonify({"error": "Username taken by another soul"}), 400
                
        elif action == 'login':
            cursor.execute("SELECT password, max_win_streak FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            if row and row[0] == password:
                return jsonify({"username": username, "max_win_streak": row[1]}), 200
            return jsonify({"error": "Invalid profile credentials"}), 401

# --- UPDATE WIN STREAK ENDPOINT ---
@app.route('/api/leaderboard/update', methods=['POST'])
def update_streak():
    data = request.json or {}
    username = data.get('username', '').strip()
    current_streak = int(data.get('streak', 0))

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        # Only update if the new streak breaks their historical record
        cursor.execute("SELECT max_win_streak FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        if row and current_streak > row[0]:
            cursor.execute("UPDATE users SET max_win_streak = ? WHERE username = ?", (current_streak, username))
            conn.commit()
            return jsonify({"message": "New Personal Record!"}), 200
    return jsonify({"message": "Streak acknowledged"}), 200

# --- GET LEADERBOARD ENDPOINT ---
@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        # Fetch top 5 players sorted by their highest win streaks
        cursor.execute("SELECT username, max_win_streak FROM users ORDER BY max_win_streak DESC LIMIT 5")
        rows = cursor.fetchall()
        leaderboard = [{"username": r[0], "streak": r[1]} for r in rows]
    return jsonify(leaderboard), 200