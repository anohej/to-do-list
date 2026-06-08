
# Flask = rammeverk for nettside
# render_template = viser HTML-filer
# request = henter data fra skjema
# redirect = sender bruker til annen side
# url_for = lager URL til en funksjon
# session = lagrer info om innlogget bruker
from flask import Flask, render_template, request, redirect, url_for, session


import mysql.connector

# hashlib brukes for å gjøre passord om til hash (string)
import hashlib


# Lager Flask-appen (objekt)
app = Flask(__name__)

# Secret key brukes for å sikre session (string)
app.secret_key = "supersecretkey"


def get_db_connection():
    # return sender tilbake database-tilkoblingen
    # Når return kjøres, stopper funksjonen
    return mysql.connector.connect(
        host="10.200.14.28",      
        user="anohej",         
        password="Ih8Fags",     
        database="todolist_db",
    )


# Route for registrering
# methods betyr at siden kan ta imot både GET (vise side) og POST (sende skjema)
@app.route('/register', methods=["GET", "POST"])
def register():
    # Hvis brukeren sender inn skjema (POST)
    if request.method == "POST":

        # Henter input fra HTML-skjema
        username = request.form["username"]
        password = request.form["password"]

        # Gjør passordet om til hash 
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        db = get_db_connection()
        cursor = db.cursor()

        try:
            # SQL INSERT legger inn ny rad i users-tabellen
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                (username, hashed_password)
            )
            db.commit()  # lagrer endringer permanent
        except mysql.connector.IntegrityError:
            # Hvis brukernavnet allerede finnes
            return "USERNAME ALREADY EXISTS"  # returnerer en string
        finally:
            cursor.close()
            db.close()

        
        return redirect(url_for('login'))

    # Hvis GET → vis register.html
    return render_template("register.html")


# Route for login
@app.route('/login', methods=["GET", "POST"])
def login():

    # Hvis brukeren allerede er logget inn
    if 'user_id' in session:
        return redirect(url_for('index'))

    if request.method == "POST":

        # Henter input fra html siden
        username = request.form["username"]
        password = request.form["password"]

        # Hasher passordet igjen 
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        db = get_db_connection()

        
        cursor = db.cursor(dictionary=True) #objekt der vi kan hente verdier med navn

        # SELECT henter data fra database
        cursor.execute(
            "SELECT * FROM users WHERE username = %s AND password = %s",
            (username, hashed_password)
        )

        # fetchone returnerer en rad fra resultatet av SQL-spørringen
        user = cursor.fetchone()

        cursor.close()
        db.close()

        
        if user:
            # Lagrer brukerens id i session
            # user['id'] er int
            session['user_id'] = user['id'] #session er en måte Flask lagrer info om brukeren mens de er logget inn
            session['username'] = user['username']

            return redirect(url_for('index'))
        else:
            return "Invalid username or password"  

    return render_template("login.html")


# Logger ut bruker
@app.route('/logout')
def logout():
    # session.clear() fjerner all lagret session-data
    session.clear()
    return redirect(url_for('login'))



@app.route('/')
def index():

    
    if 'user_id' not in session:
        return redirect(url_for('login'))

    db = get_db_connection()

    # dictionary=True gjør at tasks blir liste av dictionaries
    cursor = db.cursor(dictionary=True)

    # ORDER BY created_at DESC = nyeste først
    cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")

    # fetchall returnerer liste (list) med oppgaver
    tasks = cursor.fetchall()

    cursor.close()
    db.close()

    # Sender tasks (liste) og username (string) til HTML
    return render_template('index.html', tasks=tasks, username=session['username'])


# Legger til ny oppgave
@app.route('/add', methods=['POST'])
def add_task():

    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Henter data fra skjema 
    title = request.form.get('title')
    description = request.form.get('description')

    db = get_db_connection()
    cursor = db.cursor()

    # INSERT legger inn ny oppgave
    cursor.execute(
        "INSERT INTO tasks (title, description) VALUES (%s, %s)",
        (title, description)
    )

    db.commit()
    cursor.close()
    db.close()

    return redirect(url_for('index'))


# Markerer oppgave som ferdig
# <int:task_id> betyr at task_id er et heltall (int)
@app.route('/done/<int:task_id>')
def mark_done(task_id):

    if 'user_id' not in session:
        return redirect(url_for('login'))

    db = get_db_connection()
    cursor = db.cursor()

    # UPDATE endrer verdi i databasen
    cursor.execute(
        "UPDATE tasks SET is_done = TRUE WHERE id = %s",
        (task_id,)
    )

    db.commit()
    cursor.close()
    db.close()

    return redirect(url_for('index'))


# Sletter oppgave
@app.route('/delete/<int:task_id>')
def delete_task(task_id):

    if 'user_id' not in session:
        return redirect(url_for('login'))

    db = get_db_connection()
    cursor = db.cursor()

    # DELETE fjerner rad fra database
    cursor.execute(
        "DELETE FROM tasks WHERE id = %s", 
        (task_id,)
    )

    db.commit()
    cursor.close()
    db.close()

    return redirect(url_for('index'))



if __name__ == '__main__':

    app.run(debug=True)  # debug=True gjør at vi får feilmeldinger i nettleseren




@app.route('/faq')
def faq():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db_connection()

    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM faq ORDER BY created_at DESC")

    faq_items = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('faq.html', faq_items=faq_items, username=session['username'])



@app.route('/faq/add', methods=['POST'])
def add_faq():

    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    question = request.form.get('question')
    answer = request.form.get('answer')

    if not question or not answer:
        return redirect(url_for('faq'))
    
    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute(
        "INSERT INTO faq(question, answer) VALUES (%s, %s)",
        (question, answer)
    )

    db.commit()
    cursor.close()
    db.close()

    return redirect(url_for('faq'))

