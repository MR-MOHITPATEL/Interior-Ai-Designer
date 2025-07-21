from flask import Flask, render_template, redirect, request, jsonify
import os
import subprocess
import mysql.connector
import bcrypt
import time

app = Flask(__name__, static_folder='static', template_folder='static')
app.secret_key = 'your_secret_key'

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="interior_design"
    )

@app.route('/', methods=['GET'])
def landing():
    return redirect('/auth')

@app.route('/auth', methods=['GET', 'POST'])
def auth():
    if request.method == 'GET':
        if not os.path.exists('static/auth.html'):
            return "Error: auth.html not found", 404
        return render_template('auth.html')

@app.route('/login.html', methods=['POST'])
def login():
    try:
        data = request.form
        gmail = data.get('gmail')
        password = data.get('password')
        print(f"Received login attempt: gmail={gmail}")

        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE gmail = %s", (gmail,))
        user = cursor.fetchone()
        conn.close()

        # Check if user exists and password matches
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            print("Login successful, redirecting to /app.py")
            return redirect('/app.py')  # Redirect to your main app
        else:
            print("Invalid credentials")
            return render_template('auth.html', error="Invalid email or password")  # Pass error to frontend
    except mysql.connector.Error as err:
        print(f"Database error during login: {err}")
        return render_template('auth.html', error="Database error. Please try again later.")  # Pass error to frontend
    except Exception as e:
        print(f"Unexpected error during login: {e}")
        return render_template('auth.html', error="An unexpected error occurred. Please try again.")  # Pass error to frontend
    

@app.route('/signup.html', methods=['POST'])
def signup():
    try:
        data = request.form
        username = data.get('username')
        password = data.get('password')
        gmail = data.get('gmail')
        phone = data.get('phone')

        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = %s OR gmail = %s", (username, gmail))
        if cursor.fetchone():
            conn.close()
            print(f"Signup failed: Username {username} or gmail {gmail} already exists")
            return render_template('auth.html', error="Username or email already exists")  # Pass error to frontend

        cursor.execute("""
            INSERT INTO users (username, password, gmail, phone)
            VALUES (%s, %s, %s, %s)
        """, (username, hashed_pw, gmail, phone))
        conn.commit()
        conn.close()
        print(f"Signup successful for {username}, redirecting to auth")
        return redirect('/auth')  # Redirect to login page after successful signup
    except mysql.connector.Error as err:
        print(f"Database error during signup: {err}")
        return render_template('auth.html', error="Database error. Please try again later.")  # Pass error to frontend
    except Exception as e:
        print(f"Unexpected error during signup: {e}")
        return render_template('auth.html', error="An unexpected error occurred. Please try again.")  # Pass error to frontend


@app.route('/app.py')
def streamlit_app():
    print("Attempting to launch Streamlit")
    if not os.path.exists('app.py'):
        print("Error: app.py not found")
        return "Error: Streamlit app file not found", 404
    try:
        # Launch Streamlit in the background
        subprocess.Popen(['streamlit', 'run', 'app.py'], 
                       stdout=subprocess.PIPE, 
                       stderr=subprocess.PIPE)
        # Give Streamlit a moment to start
        time.sleep(2)
        print("Streamlit launched, redirecting to https://0c7e-34-82-223-44.ngrok-free.app/")
        return redirect('https://6f96-34-169-108-156.ngrok-free.app/')  # Update the port if Streamlit runs on a different port
    except FileNotFoundError:
        print("Error: Streamlit not installed or not in PATH")
        return "Error: Streamlit not installed", 500
    except Exception as e:
        print(f"Error launching Streamlit: {e}")
        return f"Error launching Streamlit: {e}", 500

if __name__ == '__main__':
    print("Server running on http://localhost:5000")
    app.run(debug=True, port=5000)