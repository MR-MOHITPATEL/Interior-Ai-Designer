import mysql.connector
import bcrypt

# Sample user data


# Database connection configuration (no database specified initially)
db_config = {
    "host": "localhost",
    "user": "root",
    "password": ""  # Default XAMPP root has no password
}

try:
    # Connect to MySQL without a specific database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Create the database if it doesn’t exist
    cursor.execute("CREATE DATABASE IF NOT EXISTS interior_design")
    
    # Switch to the database
    conn.database = "interior_design"

    # Create users table if it doesn’t exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL,
            password VARCHAR(100) NOT NULL,
            gmail VARCHAR(100),
            phone VARCHAR(20)
        )
    """)

    # Insert users with hashed passwords
    for user in users:
        # Hash the password
        hashed_pw = bcrypt.hashpw(user["password"].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Check if user already exists to avoid duplicates
        cursor.execute("SELECT id FROM users WHERE username = %s", (user["username"],))
        if cursor.fetchone() is None:
            # Insert new user
            cursor.execute("""
                INSERT INTO users (username, password, gmail, phone)
                VALUES (%s, %s, %s, %s)
            """, (user["username"], hashed_pw, user["gmail"], user["phone"]))
            print(f"Added user: {user['username']}")
        else:
            print(f"User {user['username']} already exists, skipping...")

    # Commit changes
    conn.commit()
    print("Data successfully integrated into MySQL!")

except mysql.connector.Error as err:
    print(f"Error: {err}")
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals() and conn.is_connected():
        conn.close()
        print("Database connection closed.")