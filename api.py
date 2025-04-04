from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash


# Configure application
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

# Remove for deployment
if __name__ == '__main__':
    app.run(port=5002)