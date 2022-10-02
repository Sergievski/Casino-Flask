from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import random
from app.upload import upload_file, UPLOAD_FOLDER, ALLOWED_EXTENSIONS


db = sqlite3.connect("database.db", check_same_thread=False) 
cursor = db.cursor()
    
query = """ 
    CREATE TABLE IF NOT EXISTS users (
    name VARCHAR(30),  
    login VARCHAR(30),
    id INTEGER PRIMARY KEY,
    balance INTEGER NOT NULL DEFAULT 5000,
    password VARCHAR(20),
    filename VARCHAR 
    );
    CREATE TABLE IF NOT EXISTS casino (
    name VARCHAR(50),
    description TEXT(300),
    balance BIGINT NOT NULL DEFAULT 1000000)
    """
cursor.executescript(query)


app = Flask(__name__)
app.secret_key = "shuki" # FOR SESSION
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER # UPLOAD CONFIG

@app.route("/")
def home ():
    if cursor.execute("SELECT * FROM casino").fetchone() is None:
        cursor.execute("INSERT INTO casino VALUES ('Dragon', 'You always win', 1000000)") 
        db.commit()
    return render_template ("home.html")

@app.route("/registr")
def registr ():
    return render_template("reg.html")

@app.route("/registrindb", methods=['POST'])
def regindb ():
    name = request.form.get('name')
    login = request.form.get('login')
    password = request.form.get('password')
    filename = upload_file()
    cursor.execute(f"SELECT * FROM users WHERE login=?",[login])
    if cursor.fetchone() is None:
        cursor.execute(f"INSERT INTO users (name, login, password, filename) VALUES ('{name}','{login}','{password}','{filename}')")
        db.commit()
        return redirect (f"/?message={name} Registered Succesfully ") 
    else:
        return redirect ("/registr?message=Login already exists, choose another one")
    
@app.route("/players") 
def players_list ():
    p_list = cursor.execute("SELECT * FROM users")
    return render_template ("players.html", players = p_list)
    
    
@app.route("/deleteplayer")
def deletebook():
    delid = request.args.get('delid')
    cursor.execute(f"DELETE FROM users WHERE id={delid}")
    db.commit()
    return redirect("/players?message=Player Deleted")


@app.route("/play")
def play_game():  
    if 'user' in session :
        user = session['user']
        return render_template("play.html", user=user)
    else:
        return redirect(url_for("log_in"))  
    

@app.route("/login")
def log_in():
    if 'user' in session:
        return redirect(url_for("play_game"))
    else:
        return render_template("login.html")
    

@app.route("/logcheck", methods=['POST'])
def log_check ():
    login=request.form.get('login')
    password=request.form.get('password')
    cursor.execute(f"SELECT * FROM users  WHERE login=? AND password=?",[login, password])
    if cursor.fetchone() is None :
        return redirect("/login?message=Incorrect Login/User")
    else:
        user=cursor.execute(f"SELECT * FROM users  WHERE login=? AND password=?",[login, password]).fetchone()
        session["user"] = user  # insert user to session
        return redirect(url_for("play_game"))


@app.route("/bet50", methods=['POST','GET'])
def bet_50():
    bet = request.form.get('bet')
    user=session['user']
    number = random.randint(1,100)
    
    if number < 50: #player loose
        cursor.execute(f"UPDATE users SET balance = balance-? WHERE login = ?",[bet, user[1]])  #update player balance
        cursor.execute(f"UPDATE casino SET balance = balance+?",[bet])
        db.commit() 
        user=cursor.execute(f"SELECT * FROM users  WHERE login=?",[user[1]]).fetchone()
        session["user"] = user  
        return redirect(f"/play?message=You lost {bet} $")     
    else:
        cursor.execute(f"UPDATE users SET balance = balance + ? WHERE login = ?",[bet, user[1]]) #update player balance
        cursor.execute(f"UPDATE casino SET balance = balance -?",[bet])
        db.commit() 
        user=cursor.execute(f"SELECT * FROM users  WHERE login=?",[user[1]]).fetchone()
        session["user"] = user         
        return redirect(f"/play?message=You won {bet} $") 


@app.route("/casinobalance")
def casino_balance():
    balance = cursor.execute("SELECT balance FROM casino WHERE name = 'Dragon'").fetchone()[0]
    return render_template("casinobalance.html", balance = balance)


@app.route("/logout")
def log_out():
    if 'user' in session:
        session.pop("user", None)
        return redirect(url_for("log_in"))
    else:
        return redirect(url_for("home"))



#app.run(debug=True)

 
            
        