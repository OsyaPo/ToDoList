"""
Routes and views for the flask application.
"""

from datetime import datetime,date
from ToDoList import app, helpers
from flask import Flask, render_template, redirect, request, url_for, g, jsonify, session
from flask_session import Session
import sqlite3 as sql
from ToDoList.helpers import apology, login_required
#https://pythonhosted.org/passlib/narr/quickstart.html
import passlib
from passlib.context import CryptContext
#from flask_api import status
#https://www.flaskapi.org/api-guide/status-codes/
from werkzeug.exceptions import HTTPException
#http://stackoverflow.com/questions/29332056/global-error-handler-for-any-exception


pwd_context = CryptContext(schemes=["pbkdf2_sha256", "des_crypt"],deprecated="auto")


#https://pythonhosted.org/Flask-Session/
#https://www.tutorialspoint.com/flask/flask_sessions.htm
SESSION_TYPE = 'filesystem'
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RThjhlkjhklLK78vghh/nm'

#http://stackoverflow.com/questions/29332056/global-error-handler-for-any-exception
@app.errorhandler(Exception)
def handle_error(e):
    code = 500
    if isinstance(e, HTTPException):
        code = e.code
    return jsonify(error=str(e)), code


#http://opentechschool.github.io/python-flask/extras/databases.html //how to create db
#https://www.syncano.io/blog/intro-flask-pt-2-creating-writing-databases/ //examples

def insert_user(email,username,password):    
        con = sql.connect("ToDo.db")
        cur = con.cursor()
        cur.execute("INSERT INTO users (email,username,password) VALUES (?,?,?)", (email,username,password))
        con.commit()
        con.close()

def insert_task(user_id,date, time, task, priority, label_color, label_text):    
        con = sql.connect("ToDo.db")
        cur = con.cursor()
        cur.execute("INSERT INTO list (user_id,date, time, task, priority, label_color, label_text) VALUES (?,?,?,?,?,?,?)", (user_id,date, time, task, priority, label_color, label_text))
        con.commit()
        con.close()

#to get dictionaries instead of tuples
#http://stackoverflow.com/questions/3300464/how-can-i-get-dict-from-sqlite-query
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response


#http://jinja.pocoo.org/docs/2.9/api/#custom-filters
def datetimeformat(value, format='%Y/%m/%d'):
    return value.strftime(format)

def dateformat(value, format='%d/%m/%y'):
    return value.strftime(format)


@app.route('/', methods=["GET", "POST"])
@login_required
def index():
    """Renders the home page."""
    date = datetime.now()
    weekday = date.strftime("%A")
    user = session["user_name"]
    
   
    return render_template('index.html', weekday= weekday, date=dateformat(date), user=user)
 
@app.route('/addTask', methods=["POST"])
@login_required
def addTask():
    today_date = datetimeformat(datetime.utcnow())

    if request.form["task"] =="":
        return apology("You forgot to add a task")
    user_id = session["user_id"]
    time = request.form["time"]
    date = request.form["date"]
    task=request.form["task"]
    priority = request.form["priority"]
    label_color = request.form["label_color"]
    label_text = request.form["label_text"]

    if request.form["date"]== "":
        date = today_date

    insert_task(user_id,date, time, task, priority, label_color, label_text)
    #return status.HTTP_200_OK
    return '200 OK' 

# gets tasks for todaytasks list
@app.route("/getTasks")
@login_required
def getTasks():
    if request.method == "GET":
        today_date = datetimeformat(datetime.utcnow())
        con = sql.connect("ToDo.db")
        con.row_factory = dict_factory
        cur = con.cursor()
        #http://stackoverflow.com/questions/398468/ordering-sql-query-by-specific-field-values
        cur.execute("SELECT * FROM list WHERE user_id = (?) AND date <= (?) ORDER BY Case priority WHEN 'High' THEN 1 WHEN 'Avarage' THEN 2 ELSE 3 END", (session["user_id"], today_date,))
        #cur.fetchall fetches(select, pick,) all (or all remaining) rows of a query result
        tasks = cur.fetchall()
        con.close()
        
    return jsonify(tasks)


@app.route("/getLtTasks")
@login_required
def getLtTasks():
    if request.method == "GET":
        today_date = datetimeformat(datetime.utcnow())
        con = sql.connect("ToDo.db")
        con.row_factory = dict_factory
        cur = con.cursor()
        cur.execute("SELECT * FROM list WHERE user_id = (?) AND date > (?) ORDER BY Case priority WHEN 'High' THEN 1 WHEN 'Avarage' THEN 2 ELSE 3 END", (session["user_id"],today_date,))
        tasks = cur.fetchall()
        con.close()
        
    return jsonify(tasks)


@app.route("/delTask", methods=["POST"])
@login_required
def delTask():
    if request.method == "POST":
        task_id = request.form["task_id"]

        con = sql.connect("ToDo.db")
        con.row_factory = dict_factory
        cur = con.cursor()
        cur.execute("DELETE FROM list WHERE Id = (?)", (task_id,))
        con.commit()
        con.close()
        
    return '200 OK'

@app.route("/updateTask", methods=["POST"])
@login_required
def updateTask():
    if request.method == "POST":
        task_id = request.form["task_id"]
        task = request.form["task"]

        con = sql.connect("ToDo.db")
        cur = con.cursor()
        cur.execute("UPDATE list SET task=(?) WHERE Id = (?)", (task, task_id,))
        con.commit()
        con.close()
        
    return '200 OK' 

@app.route("/changeStatus", methods=["POST"])
@login_required
def changeStatus():
    if request.method == "POST":
        task_id = request.form["task_id"]
        con = sql.connect("ToDo.db")
        con.row_factory = dict_factory
        cur = con.cursor()
        cur.execute("SELECT * FROM list WHERE Id = (?)", (task_id,))
        rows = cur.fetchall()
        con.close()

        if len(rows) == 0 :
            return apology ("Something went wrong")
           
        if rows[0]["status"] == "unchacked":
            con = sql.connect("ToDo.db")
            con.row_factory = dict_factory
            cur = con.cursor()
            cur.execute("UPDATE list SET status='checked' WHERE Id = (?)", (task_id,))
            con.commit()
            con.close()
        elif rows[0]["status"] == "checked":
            con = sql.connect("ToDo.db")
            con.row_factory = dict_factory
            cur = con.cursor()
            cur.execute("UPDATE list SET status='unchacked' WHERE Id = (?)", (task_id,))
            con.commit()
            con.close()
        
        
    return '200 OK'         
    

@app.route('/register', methods=["GET", "POST"])
def register ():
    """Register user."""
    
    if request.method == "POST":
    
        if request.form["username"] == "" or  request.form["email"] =="" or request.form["password"]=="" or request.form["confirm-password"]=="":
            return apology("Please, provide username and password")
       
        if request.form["password"] != request.form["confirm-password"]:
            return apology ("Passwords are not the same")
        elif len(request.form["password"]) <6:
            return apology ("Your password must be not less than 6 letters")

        email = request.form['email']
        username = request.form['username']
        hash = pwd_context.hash(request.form['password'])        

        # query database for email
        con = sql.connect("ToDo.db")
        con.row_factory = dict_factory
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE email = (?)", (email,))
        rows = cur.fetchall()
        con.close()

        # ensure email is unique
        if len(rows) != 0:
            return apology("This username is alredy exist")
            
        insert_user(email,username,hash)
        return redirect(url_for("login"))
            
    return render_template('register.html')


@app.route('/login', methods=["GET","POST"])
def login ():
    """Log user in."""

    # forget any user_id
    session.pop('user_id', None)
    session.pop('user_name', None)


    # for alert with invalid login
    invalid_log = False  

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form["email"]:
            return apology("Please provide email")

        # ensure password was submitted
        elif not request.form["password"]:
            return apology("Please provide password")

        # query database for username
        con = sql.connect("ToDo.db")
        con.row_factory = dict_factory
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE email = (?)", (request.form['email'],))
        rows = cur.fetchall()
        con.close()        

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form["password"], rows[0]["password"]):
            invalid_log = True
                    
            return render_template("login.html", log_message = invalid_log)

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["user_name"] = rows[0]["username"]

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html", log_message = invalid_log)

@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))

@app.route("/settings", methods=["GET","POST"])
@login_required
def settings():
    user = session["user_name"]
  
    return render_template("settings.html",  user=user)


@app.route("/changePas", methods=["POST"])
@login_required
def changePas():
    if request.method == "POST":
        if request.form['password']=="" or request.form['confirm_pas']=="" or request.form['new_password']=="":
            abort (500)
        if request.form['new_password'] != request.form['confirm_pas']:
            abort (500)

        # query database for user_id and password
        con = sql.connect("ToDo.db")
        con.row_factory = dict_factory
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE id = (?)", (session["user_id"],))
        rows = cur.fetchall()
        con.close()        

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form["password"], rows[0]["password"]):
          abort (500)
    
        password = pwd_context.hash(request.form['new_password'])

        # changes password in db
        con = sql.connect("ToDo.db")
        con.row_factory = dict_factory
        cur = con.cursor()
        cur.execute("UPDATE users SET password=(?) WHERE id = (?)", (password, session["user_id"],))
        con.commit()
        con.close()
        
        return '200 OK'    


"""

if __name__ == '__main__':
    app.debug = True
    app.run()
"""
   
