from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import mysql.connector
from dotenv import load_dotenv
import os

# Configure application
app = Flask(__name__)

# Database config (Aiven)
def create_connection():
    connection = mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        ssl_ca=os.getenv('SSL_CA_PATH')
    )
    return connection 

@app.route('/')
def index():

    connection = create_connection()
    cursor = connection.cursor()
    
    cursor.execute("""
        SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = 'defaultdb';
    """)
    
    schema_data = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template('index.html', schema_data=schema_data)

# Remove for deployment
if __name__ == '__main__':
    app.run(port=5002)