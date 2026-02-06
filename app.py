from flask import Flask, render_template, request
import mysql.connector
import hashlib

app= Flask(__name__)


def get_db_connection():
    return mysql.connector.connect(
        host= "10.200.14.28",
        user= "anohej",
        password= "Ih8Fags",
        database="flask_login",
    )




@app.route('/')
def index():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)#hva betyr dictunary
    cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
    tasks = cursor.fetchall()
    cursor.close()
    db.close()
