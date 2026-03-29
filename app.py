import sqlite3
import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime

app = Flask(__name__)
app.secret_key = "farming_secret_key" # Needed for sessions

UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def get_db_connection():
    conn = sqlite3.connect('farming.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    # User Table
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT)''')
    # Chemical Table
    c.execute('''CREATE TABLE IF NOT EXISTS chemicals 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, category TEXT, name TEXT, target TEXT, dosage TEXT)''')
    
    # Add a default user if empty
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('admin', '1234'))

    # Add sample chemicals if empty
    c.execute("SELECT COUNT(*) FROM chemicals")
    if c.fetchone()[0] == 0:
        data = [('Pesticide', 'Neem Oil', 'Aphids', '5ml/L'), ('Fertilizer', 'Urea', 'Nitrogen', '50kg/Acre')]
        c.executemany("INSERT INTO chemicals (category, name, target, dosage) VALUES (?, ?, ?, ?)", data)
    
    conn.commit()
    conn.close()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
        conn.close()

        if user:
            session['user'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid Credentials")
    return render_template('login.html')

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))
# --- Add this route to your app.py ---

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db_connection()
        # Check if username already exists
        existing_user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        
        if existing_user:
            conn.close()
            return render_template('register.html', error="Username already taken!")
        
        # Insert new user
        conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        conn.close()
        
        # After registering, send them to login
        return redirect(url_for('login'))
    
    return render_template('register.html')
def init_db():
    conn = sqlite3.connect('farming.db')
    c = conn.cursor()
    # This creates the table ONLY if it's missing
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT)''')
    # Add a default admin so you can always log in
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('admin', '1234'))
    except sqlite3.IntegrityError:
        pass # Admin already exists
    conn.commit()
    conn.close()
# --- Update your init_db() slightly to ensure usernames are unique ---

# --- Keep existing /api/chemicals, /upload, and /chat routes here ---

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
