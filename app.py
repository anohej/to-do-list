from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import hashlib

app = Flask(__name__)
app.secret_key = "supersecretkey"


def get_db_connection():
    return mysql.connector.connect(
        host="10.200.14.28",
        user="anohej",
        password="Ih8Fags",
        database="todolist_db",
    )


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        db = get_db_connection()
        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                (username, hashed_password)
            )
            db.commit()
        except mysql.connector.IntegrityError:
            return "USERNAME ALREADY EXISTS"
        finally:
            cursor.close()
            db.close()

        return redirect(url_for('login'))
    return render_template("register.html")


@app.route('/login', methods=["GET", "POST"])
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM users WHERE username = %s AND password = %s",
            (username, hashed_password)
        )
        user = cursor.fetchone()
        cursor.close()
        db.close()

        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']  
            return redirect(url_for('index'))
        else:
            return "Invalid username or password"

    return render_template("login.html")


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
    tasks = cursor.fetchall()
    cursor.close()
    db.close()

    return render_template('index.html', tasks=tasks, username=session['username'])


@app.route('/add', methods=['POST'])
def add_task():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    title = request.form.get('title')
    description = request.form.get('description')

    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, description) VALUES (%s, %s)",
        (title, description)
    )
    db.commit()
    cursor.close()
    db.close()

    return redirect(url_for('index'))


@app.route('/done/<int:task_id>')
def mark_done(task_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE tasks SET is_done = TRUE WHERE id = %s",
        (task_id,)
    )
    db.commit()
    cursor.close()
    db.close()
    return redirect(url_for('index'))


@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute(
        "DELETE FROM tasks WHERE id = %s",
        (task_id,)
    )
    db.commit()
    cursor.close()
    db.close()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
