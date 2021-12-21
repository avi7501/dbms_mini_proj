from flask import *
import sqlite3

app = Flask(__name__, static_folder='static')
id = 1
conn = sqlite3.connect('login.db')
conn.execute('''
    CREATE TABLE IF NOT EXISTS LOGIN(
    U_NAME VARCHAR2(10) PRIMARY KEY,
    PWD VARCHAR2(10) NOT NULL,
    TYPE  VARCHAR2(10) NOT NULL);    
         ''')
conn.execute('''
    CREATE TABLE IF NOT EXISTS PATIENT(
    PAT_ID NUMBER(10) PRIMARY KEY,
    PAT_NAME VARCHAR2(10) NOT NULL,
    U_NAME VARCHAR2(10) NOT NULL,
    PWD VARCHAR2(10) NOT NULL,
    PAT_DOB DATE NOT NULL,
    PAT_ADDRESS VARCHAR2(50) NOT NULL,
    PAT_PHONE NUMBER(10) NOT NULL,
    PAT_EMAIL VARCHAR2(20) NOT NULL);

''')
conn.close()


@app.route('/')
@app.route('/home')
def home_page():
    return render_template('index.html')


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/signup/', methods=['POST'])
def register():
     global id
     id =id+1
     PAT_ID = str(id)
     PAT_NAME=request.form["name"]
     PAT_DOB=request.form["dob"]
     U_NAME=request.form["uname"]
     PAT_EMAIL=request.form["email"]
     PAT_PHONE=request.form["phone"]
     PAT_ADDRESS=request.form["address"]
     PWD=request.form["pwd"]
    #  return PAT_ID+PAT_NAME+PAT_DOB+U_NAME+PAT_EMAIL+PAT_PHONE+PAT_ADDRESS+PAT_PWD,render_template('login.html')
     conn = sqlite3.connect('login.db')
     conn.execute('INSERT INTO LOGIN(U_NAME,PWD,TYPE) VALUES("'+U_NAME+'","'+PWD+'","PATIENT");')
     conn.execute('INSERT INTO PATIENT VALUES("'+PAT_ID+'","'+PAT_NAME+'","'+U_NAME+'","'+PWD+'","'+PAT_DOB+'","'+PAT_ADDRESS+'","'+PAT_PHONE+'","'+PAT_EMAIL+'");')
     conn.commit()
     conn.close()
     return render_template('login.html')

@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/login/',methods=['POST'])
def signin():
    con=sqlite3.connect("login.db")
    uname=request.form["uname"]
    pwd=request.form["pwd"]
    cur=con.cursor()
    row=cur.execute("SELECT U_NAME,PWD FROM LOGIN WHERE U_NAME='{un}' AND PWD='{pw}'".format(un=uname,pw=pwd))
    row=row.fetchall()
    if len(row)==1:
        return ("loggedin")
    else:
        return ("error")
   

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/profile', methods=['GET','POST'])
def pprof():
    con=sqlite3.connect("login.db")
    uname=request.form["uname"]
    pwd=request.form["pwd"]
    cur=con.cursor()
    row=cur.execute("SELECT * FROM PATIENT WHERE U_NAME='{un}' AND PWD='{pw}'".format(un=uname,pw=pwd))
    row=row.fetchall()
    return render_template('profile.html',un=uname)

app.run(debug=True)
