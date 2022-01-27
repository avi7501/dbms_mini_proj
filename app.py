import os
from re import T
from flask import *
import sqlite3
import pdfkit
import datetime
import uuid

app = Flask(__name__, static_folder='static')

app.config['SECRET_KEY'] = '28852c118493f8b9b2161e506f32d4c5'

con = sqlite3.connect('database.db')
con.execute('''
    CREATE TABLE IF NOT EXISTS LOGIN(
    U_NAME VARCHAR2(10) PRIMARY KEY,
    PWD VARCHAR2(10) NOT NULL,
    TYPE  VARCHAR2(10) NOT NULL,
    DPLOC VARCHAR2(50) NOT NULL);    
         ''')
con.execute('''
    CREATE TABLE IF NOT EXISTS PATIENT(
    PAT_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    PAT_NAME VARCHAR2(10) NOT NULL,
    U_NAME REFERENCES LOGIN(U_NAME),
    PAT_DOB DATE NOT NULL,
    PAT_GENDER VARCHAR2(6) NOT NULL,
    PAT_ADDRESS VARCHAR2(50) NOT NULL,
    PAT_PHONE NUMBER(10) NOT NULL,
    PAT_EMAIL VARCHAR2(20) NOT NULL);

''')
con.execute('''
    CREATE TABLE IF NOT EXISTS DOCTOR(
    DOC_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    DOC_NAME VARCHAR2(255) NOT NULL,
    U_NAME REFERENCES LOGIN(U_NAME),
    DEP VARCHAR2(20) NOT NULL,    
    DOC_GENDER VARCHAR2(6) NOT NULL,
    DOC_EXP VARCHAR2(50) NOT NULL,
    DOC_SALARY NUMBER(10,2) NOT NULL,
    DOC_PHONE NUMBER(10) NOT NULL,
    DOC_EMAIL VARCHAR2(20) NOT NULL);
''')
con.execute('''
    CREATE TABLE IF NOT EXISTS VISITS(
    TOKEN_NO INTEGER  PRIMARY KEY AUTOINCREMENT,
    VISIT_TIME DATETIME NOT NULL UNIQUE,
    VISIT_TYPE VARCHAR2(20) NOT NULL,
    PAT_ID REFERENCES PATIENT(PAT_ID),
    PAT_NAME REFERENCES PATIENT(PAT_NAME),
    DOC_ID REFERENCES DOCTOR(DOC_ID),
    DOC_NAME REFERENCES DOCTOR(DOC_NAME),
    DEP REFERENCES DOCTOR(DEP),
    VISIT_STATUS VARCHAR2(20),
    DIAGNOSIS  VARCHAR2(500),
    PRESCRIPTION VARCHAR2(500),
    CONSULTFEE NUMBER(10,2),
    ADDFEES NUMBER(10,2),    
    TOTALFEES NUMBER(10,2)
    );
''')

con.close()


@app.route('/')
@app.route('/home')
def home_page():
    return render_template('index.html')


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/signup/', methods=['GET', 'POST'])
def register():
    PAT_NAME = request.form["name"]
    PAT_DOB = request.form["dob"]
    U_NAME = request.form["uname"]
    PAT_EMAIL = request.form["email"]
    PAT_PHONE = request.form["phone"]
    PAT_GENDER = request.form["gender"]
    PAT_ADDRESS = request.form["address"]
    PWD = request.form["pwd"]

    conn = sqlite3.connect('database.db')
    conn.execute('INSERT INTO LOGIN(U_NAME,PWD,TYPE,DPLOC) VALUES("' +
                 U_NAME+'","'+PWD+'","PATIENT","images/user.profile.png");')
    conn.execute('INSERT INTO PATIENT (PAT_NAME,U_NAME,PAT_DOB,PAT_GENDER,PAT_ADDRESS,PAT_PHONE,PAT_EMAIL) VALUES("' +
                 PAT_NAME+'","'+U_NAME+'","'+PAT_DOB+'","'+PAT_GENDER+'","'+PAT_ADDRESS+'","'+PAT_PHONE+'","'+PAT_EMAIL+'");')
    conn.commit()
    conn.close()
    return render_template('login.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/alogin/', methods=['POST'])
def asigin():
    con = sqlite3.connect("database.db")
    uname = request.form["uname"]
    pwd = request.form["pwd"]
    cur = con.cursor()
    cur.execute("SELECT U_NAME,PWD,DPLOC FROM LOGIN WHERE U_NAME='{un}' AND PWD='{pw}' AND TYPE='ADMIN';".format(
        un=uname, pw=pwd))
    acc = cur.fetchall()
    if len(acc) == 1:
        for i in acc:
            dp = i[2]
        session["name"] = uname
        return render_template('adashboard.html', dp=dp)
    else:
        return render_template('error.html')


@app.route('/adashboard')
def adashboard():
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    uname = session["name"]
    cur.execute("SELECT DPLOC FROM LOGIN WHERE U_NAME='{un}'".format(un=uname))
    acc = cur.fetchall()
    for i in acc:
        dp = i[0]
    return render_template('adashboard.html', dp=dp)


@app.route('/viewdocs')
def viewdocs():
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    uname = session["name"]
    cur.execute("SELECT DPLOC FROM LOGIN WHERE U_NAME='{un}'".format(un=uname))
    acc = cur.fetchall()
    for i in acc:
        dp = i[0]
    cur.execute("SELECT *FROM DOCTOR;")
    docs = cur.fetchall()
    return render_template('viewdoc.html', docs=docs, dp=dp)


@app.route('/adddocs')
def adddocs():
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    uname = session["name"]
    cur.execute("SELECT DPLOC FROM LOGIN WHERE U_NAME='{un}'".format(un=uname))
    acc = cur.fetchall()
    for i in acc:
        dp = i[0]
    return render_template('adddoc.html', dp=dp)


@app.route('/adddocs/', methods=['GET', 'POST'])
def addoc():
    con = sqlite3.connect("database.db", isolation_level=None)
    cur = con.cursor()
    uname = session["name"]
    cur.execute("SELECT DPLOC FROM LOGIN WHERE U_NAME='{un}'".format(un=uname))
    acc = cur.fetchall()
    for i in acc:
        dp = i[0]
    U_NAME = request.form["uname"]
    PWD = request.form["pwd"]
    DOC_NAME = request.form["name"]
    DEP = request.form["dep"]
    DOC_GENDER = request.form["gender"]
    DOC_EXP = request.form["exp"]
    DOC_SALARY = request.form["sal"]
    DOC_PHONE = request.form["phone"]
    DOC_EMAIL = request.form["email"]

    con.execute(
        "INSERT INTO LOGIN (U_NAME,PWD,TYPE,DPLOC) VALUES('{u}','{p}','DOCTOR','images/user.profile.png');".format(u=U_NAME, p=PWD))
    con.execute("INSERT INTO DOCTOR (DOC_NAME,U_NAME,DEP,DOC_GENDER,DOC_EXP,DOC_SALARY,DOC_PHONE,DOC_EMAIL) VALUES('{n}','{u}','{d}','{g}','{ex}','{s}','{p}','{e}');".format(
        n=DOC_NAME, u=U_NAME, d=DEP, g=DOC_GENDER, ex=DOC_EXP, s=DOC_SALARY, p=DOC_PHONE, e=DOC_EMAIL))
    con.commit
    con.close()
    return render_template('asuccess.html', dp=dp)


@app.route('/dlogin/', methods=['POST'])
def dsigin():
    con = sqlite3.connect("database.db")
    uname = request.form["uname"]
    pwd = request.form["pwd"]
    cur = con.cursor()
    cur.execute("SELECT U_NAME,PWD,DPLOC FROM LOGIN WHERE U_NAME='{un}' AND PWD='{pw}' AND TYPE='DOCTOR';".format(
        un=uname, pw=pwd))
    acc = cur.fetchall()
    if len(acc) == 1:
        for i in acc:
            dp = i[2]
        session["name"] = uname
        cur.execute("SELECT *FROM DOCTOR WHERE U_NAME='{un}'".format(un=uname))
        ddata = cur.fetchall()
        return render_template('ddashboard.html', ddata=ddata, dp=dp)
    else:
        return render_template('error.html')


@app.route('/ddashboard')
def ddashboard():
    uname = session["name"]
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute("SELECT DPLOC FROM LOGIN WHERE U_NAME='{un}'".format(un=uname))
    acc = cur.fetchall()
    for i in acc:
        dp = i[0]
    cur.execute("SELECT *FROM DOCTOR WHERE U_NAME='{un}'".format(un=uname))
    ddata = cur.fetchall()
    return render_template('ddashboard.html', ddata=ddata, dp=dp)


@app.route('/plogin/', methods=['POST'])
def psignin():
    con = sqlite3.connect("database.db")
    uname = request.form["uname"]
    pwd = request.form["pwd"]
    cur = con.cursor()
    cur.execute("SELECT U_NAME,PWD,DPLOC FROM LOGIN WHERE U_NAME='{un}' AND PWD='{pw}' AND TYPE='PATIENT';".format(
        un=uname, pw=pwd))
    acc = cur.fetchall()
    if len(acc) == 1:
        for i in acc:
            dp = i[2]
        session["name"] = uname
        cur.execute(
            "SELECT *FROM PATIENT WHERE U_NAME='{un}'".format(un=uname))
        pdata = cur.fetchall()
        return render_template('pdashboard.html', pdata=pdata, dp=dp)
    else:
        return render_template('error.html')


@app.route('/pdashboard')
def profile():
    uname = session["name"]
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute("SELECT DPLOC FROM LOGIN WHERE U_NAME='{un}'".format(un=uname))
    acc = cur.fetchall()
    for i in acc:
        dp = i[0]
    cur.execute("SELECT *FROM PATIENT WHERE U_NAME='{un}'".format(un=uname))
    pdata = cur.fetchall()
    return render_template('pdashboard.html', pdata=pdata, dp=dp)


@app.route('/pappointment')
def pappointment():
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    uname = session["name"]

    cur.execute("SELECT DPLOC FROM LOGIN WHERE U_NAME='{un}'".format(un=uname))
    acc = cur.fetchall()
    for i in acc:
        dp = i[0]
    cur.execute("SELECT DEP FROM DOCTOR GROUP BY DEP;")
    deps = cur.fetchall()
    cur = con.cursor()
    cur.execute("SELECT DOC_NAME FROM DOCTOR  WHERE DEP='general';")
    gen = cur.fetchall()
    return render_template('pappointment.html', deps=deps, gen=gen, dp=dp)


@app.route('/vdermatology')
def vdermatology():
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    uname = session["name"]

    cur.execute("SELECT DPLOC FROM LOGIN WHERE U_NAME='{un}'".format(un=uname))
    acc = cur.fetchall()
    for i in acc:
        dp = i[0]
    cur.execute("SELECT DOC_NAME FROM DOCTOR  WHERE DEP='dermatology';")
    doc = cur.fetchall()
    return render_template('alldep.html', doc=doc, dp=dp)


@app.route('/vpediatric')
def vpediatric():
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    uname = session["name"]
    cur.execute("SELECT DPLOC FROM LOGIN WHERE U_NAME='{un}'".format(un=uname))
    acc = cur.fetchall()
    for i in acc:
        dp = i[0]
    cur.execute("SELECT DOC_NAME FROM DOCTOR  WHERE DEP='pediatric';")
    doc = cur.fetchall()
    return render_template('alldep.html', doc=doc, dp=dp)


@app.route('/vgeneral')
def vgeneral():
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    uname = session["name"]

    cur.execute("SELECT DPLOC FROM LOGIN WHERE U_NAME='{un}'".format(un=uname))
    acc = cur.fetchall()
    for i in acc:
        dp = i[0]
    cur.execute("SELECT DOC_NAME FROM DOCTOR  WHERE DEP='general';")
    doc = cur.fetchall()
    return render_template('alldep.html', doc=doc, dp=dp)


@app.route('/vENT')
def vENT():
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    uname = session["name"]

    cur.execute("SELECT DPLOC FROM LOGIN WHERE U_NAME='{un}'".format(un=uname))
    acc = cur.fetchall()
    for i in acc:
        dp = i[0]
    cur.execute("SELECT DOC_NAME FROM DOCTOR  WHERE DEP='ENT';")
    doc = cur.fetchall()
    return render_template('alldep.html', doc=doc, dp=dp)


@app.route('/vcardiology')
def vcardiology():
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    uname = session["name"]

    cur.execute("SELECT DPLOC FROM LOGIN WHERE U_NAME='{un}'".format(un=uname))
    acc = cur.fetchall()
    for i in acc:
        dp = i[0]
    cur.execute("SELECT DOC_NAME FROM DOCTOR  WHERE DEP='cardiology';")
    doc = cur.fetchall()
    return render_template('alldep.html', doc=doc, dp=dp)


@app.route('/vgynecology')
def vgynecology():
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    uname = session["name"]

    cur.execute("SELECT DPLOC FROM LOGIN WHERE U_NAME='{un}'".format(un=uname))
    acc = cur.fetchall()
    for i in acc:
        dp = i[0]
    cur.execute("SELECT DOC_NAME FROM DOCTOR  WHERE DEP='gynecology';")
    doc = cur.fetchall()
    return render_template('alldep.html', doc=doc, dp=dp)


@app.route('/vopthamology')
def vopthamology():
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    uname = session["name"]

    cur.execute("SELECT DPLOC FROM LOGIN WHERE U_NAME='{un}'".format(un=uname))
    acc = cur.fetchall()
    for i in acc:
        dp = i[0]
    cur.execute("SELECT DOC_NAME FROM DOCTOR  WHERE DEP='opthamology';")
    doc = cur.fetchall()
    return render_template('alldep.html', doc=doc, dp=dp)


@app.route('/vinternal')
def vinternal():
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    uname = session["name"]

    cur.execute("SELECT DPLOC FROM LOGIN WHERE U_NAME='{un}'".format(un=uname))
    acc = cur.fetchall()
    for i in acc:
        dp = i[0]
    cur.execute("SELECT DOC_NAME FROM DOCTOR  WHERE DEP='internal';")
    doc = cur.fetchall()
    return render_template('alldep.html', doc=doc, dp=dp)


@app.route('/vsurgery')
def vsurgery():
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    uname = session["name"]

    cur.execute("SELECT DPLOC FROM LOGIN WHERE U_NAME='{un}'".format(un=uname))
    acc = cur.fetchall()
    for i in acc:
        dp = i[0]
    cur.execute("SELECT DOC_NAME FROM DOCTOR  WHERE DEP='surgery';")
    doc = cur.fetchall()
    return render_template('alldep.html', doc=doc, dp=dp)


@app.route('/vdental')
def vdental():
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    uname = session["name"]

    cur.execute("SELECT DPLOC FROM LOGIN WHERE U_NAME='{un}'".format(un=uname))
    acc = cur.fetchall()
    for i in acc:
        dp = i[0]
    cur.execute("SELECT DOC_NAME FROM DOCTOR  WHERE DEP='dental';")
    doc = cur.fetchall()
    return render_template('alldep.html', doc=doc, dp=dp)


@app.route('/alldep/', methods=['GET', 'POST'])
def alldep():
    uname = session["name"]
    dname = request.form.get("dname")
    vdate = request.form.get("vdate")
    vtime = request.form.get("vtime")
    VISIT_TIME = str(vdate)+' '+str(vtime)
    con = sqlite3.connect("database.db")
    cur = con.cursor()

    cur.execute("SELECT DPLOC FROM LOGIN WHERE U_NAME='{un}'".format(un=uname))
    acc = cur.fetchall()
    for i in acc:
        dp = i[0]
    cur.execute(
        "SELECT PAT_ID,PAT_NAME FROM PATIENT WHERE U_NAME='{un}';".format(un=uname))
    pdata = cur.fetchall()
    cur.execute(
        "SELECT DOC_ID,DOC_NAME,DEP FROM DOCTOR  WHERE DOC_NAME='{d}';".format(d=dname))
    doc = cur.fetchall()
    con.close()
    for i in pdata:
        PAT_ID = i[0]
        PAT_NAME = i[1]
    for i in doc:
        DOC_ID = i[0]
        DOC_NAME = i[1]
        DEP = i[2]
    print(PAT_ID)
    print(DOC_ID)
    print(VISIT_TIME)
    print(DEP)
    try:
        conn = sqlite3.connect("database.db", isolation_level=None)
        conn.execute("INSERT INTO VISITS (VISIT_TIME, VISIT_TYPE, PAT_ID,PAT_NAME,DOC_ID,DOC_NAME,DEP,VISIT_STATUS,DIAGNOSIS, PRESCRIPTION) VALUES ('{vd}','Appointment',{p},'{pn}',{d},'{dn}','{dep}','NOT CHECKED IN','Pending','Pending');".format(
            vd=VISIT_TIME, p=PAT_ID, pn=PAT_NAME, d=DOC_ID, dn=DOC_NAME, dep=DEP))
        conn.commit()
        conn.close()
        return render_template('success.html', dp=dp)
    except:
        return render_template('booked.html', dp=dp)


@app.route('/pvisit')
def pvisit():
    uname = session["name"]
    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT DPLOC FROM LOGIN WHERE U_NAME='{un}'".format(un=uname))
    acc = cur.fetchall()
    for i in acc:
        dp = i[0]
    cur.execute("SELECT *FROM PATIENT WHERE U_NAME='{un}'".format(un=uname))
    pdata = cur.fetchall()
    id = pdata[0][0]
    cur.execute("SELECT *FROM VISITS WHERE PAT_ID={i}".format(i=id))
    vdata = cur.fetchall()
    return render_template('pvisit.html', vdata=vdata, dp=dp)


@app.route('/general')
def general():
    return render_template('general.html')


@app.route('/pediatric')
def pediatric():
    return render_template('pediatric.html')


@app.route('/dermatology')
def dermatology():
    return render_template('dermatology.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/dvisit')
def dvisit():
    uname = session["name"]
    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row

    cur = con.cursor()
    cur.execute("SELECT DPLOC FROM LOGIN WHERE U_NAME='{un}'".format(un=uname))
    acc = cur.fetchall()
    for i in acc:
        dp = i[0]

    cur.execute("SELECT *FROM DOCTOR WHERE U_NAME='{un}'".format(un=uname))
    ddata = cur.fetchall()
    did = ddata[0][0]
    cur.execute("SELECT *FROM VISITS WHERE DOC_ID={i}".format(i=did))
    vddata = cur.fetchall()
    print(vddata)
    return render_template('dvisits.html', vddata=vddata, dp=dp)


@app.route('/dapppointment')
def dapppointment():
    uname = session["name"]
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute("SELECT DPLOC FROM LOGIN WHERE U_NAME='{un}'".format(un=uname))
    acc = cur.fetchall()
    for i in acc:
        dp = i[0]
    return render_template('dappointment.html', dp=dp)


@app.route('/dbooked')
def dbooked():
    uname = session["name"]
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute("SELECT DPLOC FROM LOGIN WHERE U_NAME='{un}'".format(un=uname))
    acc = cur.fetchall()
    for i in acc:
        dp = i[0]
    cur.execute(
        "SELECT DOC_ID FROM DOCTOR  WHERE U_NAME='{u}';".format(u=uname))
    ddata = cur.fetchall()
    for i in ddata:
        docid = i[0]
    cur.execute(
        "SELECT TOKEN_NO FROM VISITS WHERE VISIT_STATUS='NOT CHECKED IN' AND DOC_ID={d} ;".format(d=docid))
    tk = cur.fetchall()
    return render_template('dbooked.html', dp=dp, tk=tk)


@app.route('/dbooked/', methods=['GET', 'POST'])
def booked():
    uname = session["name"]
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute("SELECT DPLOC FROM LOGIN WHERE U_NAME='{un}'".format(un=uname))
    acc = cur.fetchall()
    for i in acc:
        dp = i[0]
    con.close()
    TOKEN_NO = request.form["tkno"]
    DIAGNOSIS = request.form["diagn"]
    PRESCRIPTION = request.form["pres"]
    CONSULTFEE = request.form["consult"]
    ADDFEES = request.form["addfee"]
    TOTALFEES = int(CONSULTFEE)+int(ADDFEES)+20
    conn = sqlite3.connect("database.db", isolation_level=None)

    conn.execute("UPDATE VISITS SET VISIT_STATUS='CHECKED IN',DIAGNOSIS='{d}',PRESCRIPTION='{p}',CONSULTFEE={c},ADDFEES={a},TOTALFEES={tf} WHERE TOKEN_NO={t} AND DIAGNOSIS='Pending' AND PRESCRIPTION='Pending';".format(
        d=DIAGNOSIS, p=PRESCRIPTION, t=TOKEN_NO, c=CONSULTFEE, a=ADDFEES, tf=TOTALFEES))
    conn.commit()
    conn.close()
    return render_template('dsuccess.html', dp=dp)


@app.route('/dwalkin')
def dwalkin():
    uname = session["name"]
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute("SELECT DPLOC FROM LOGIN WHERE U_NAME='{un}'".format(un=uname))
    acc = cur.fetchall()
    for i in acc:
        dp = i[0]
    return render_template('dwalkin.html', dp=dp)


@app.route('/dwalkin/', methods=['GET', 'POST'])
def walkin():
    U_NAME = session['name']
    PAT_ID = request.form["pat_id"]
    DIAGNOSIS = request.form["diagn"]
    PRESCRIPTION = request.form["pres"]
    CONSULTFEE = request.form["consult"]
    ADDFEES = request.form["addfee"]
    TOTALFEES = int(CONSULTFEE)+int(ADDFEES)+15
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute(
        "SELECT PAT_NAME FROM PATIENT WHERE PAT_ID={id};".format(id=PAT_ID))
    pdata = cur.fetchall()

    cur.execute(
        "SELECT DPLOC FROM LOGIN WHERE U_NAME='{un}'".format(un=U_NAME))
    acc = cur.fetchall()
    for i in acc:
        dp = i[0]
    cur.execute(
        "SELECT DOC_ID,DOC_NAME,DEP FROM DOCTOR  WHERE U_NAME='{u}';".format(u=U_NAME))
    ddata = cur.fetchall()
    for i in pdata:
        PAT_NAME = pdata[0][0]

    for i in ddata:
        DOC_ID = ddata[0][0]
        DOC_NAME = ddata[0][1]
        DEP = ddata[0][2]

    VISIT_TIME = datetime.datetime.now().replace(microsecond=0)
    cur.execute("INSERT INTO VISITS (VISIT_TIME, VISIT_TYPE, PAT_ID,PAT_NAME,DOC_ID,DOC_NAME,DEP,VISIT_STATUS,DIAGNOSIS, PRESCRIPTION,CONSULTFEE,ADDFEES,TOTALFEES) VALUES ('{vd}','Walk-in',{p},'{pn}',{d},'{dn}','{dep}','CHECKED IN','{diagn}','{pres}',{c},{a},{t});".format(
        vd=VISIT_TIME, p=PAT_ID, pn=PAT_NAME, d=DOC_ID, dn=DOC_NAME, dep=DEP, diagn=DIAGNOSIS, pres=PRESCRIPTION, c=CONSULTFEE, a=ADDFEES, t=TOTALFEES))
    con.commit()
    con.close()
    return render_template('dsuccess.html', dp=dp)


@app.route('/pprofile', methods=['GET', 'POST'])
def editprof():
    uname = session["name"]
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute(
        "SELECT PWD,DPLOC FROM LOGIN WHERE U_NAME='{un}'".format(un=uname))
    acc = cur.fetchall()
    for i in acc:
        pwd = i[0]
        dp = i[1]
    cur.execute("SELECT *FROM PATIENT WHERE U_NAME='{un}'".format(un=uname))
    pdata = cur.fetchall()
    return render_template('pprofile.html', pdata=pdata, dp=dp, pwd=pwd)


@app.route('/pprofile/', methods=['GET', 'POST'])
def submitedit():
    uname = session["name"]
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute("SELECT DPLOC FROM LOGIN WHERE U_NAME='{un}'".format(un=uname))
    acc = cur.fetchall()
    for i in acc:
        dp = i[0]
    profilePic = request.files["profilePic"]
    if os.path.splitext(profilePic.filename)[1] == '':
        picname = dp
    else:
        picname = str(uuid.uuid1())+os.path.splitext(profilePic.filename)[1]
        profilePic.save(os.path.join("static/images", picname))
        picname = 'images/'+picname
    PAT_NAME = request.form["name"]
    PAT_DOB = request.form["dob"]
    PAT_EMAIL = request.form["email"]
    PAT_PHONE = request.form["phone"]
    PAT_ADDRESS = request.form["address"]
    PWD = request.form["pwd"]
    conn = sqlite3.connect('database.db')
    conn.execute(
        "UPDATE LOGIN SET PWD='{p}',DPLOC='{pp}' WHERE U_NAME='{u}';".format(p=PWD, pp=picname, u=uname))
    conn.execute("UPDATE PATIENT SET PAT_NAME='{n}',PAT_DOB='{d}',PAT_EMAIL='{e}',PAT_PHONE='{p}',PAT_ADDRESS='{a}' WHERE U_NAME='{u}';".format(
        n=PAT_NAME, d=PAT_DOB, e=PAT_EMAIL, p=PAT_PHONE, a=PAT_ADDRESS, u=uname))
    conn.commit()
    conn.close()
    return render_template('success.html', dp=picname)


@app.route('/billing')
def billing():
    uname = session["name"]
    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    cur.execute("SELECT DPLOC FROM LOGIN WHERE U_NAME='{un}'".format(un=uname))
    acc = cur.fetchall()
    for i in acc:
        dp = i[0]
    cur.execute("SELECT *FROM PATIENT WHERE U_NAME='{un}'".format(un=uname))
    pdata = cur.fetchall()
    id = pdata[0][0]
    cur.execute("SELECT *FROM VISITS WHERE PAT_ID={i}".format(i=id))
    vdata = cur.fetchall()
    return render_template('billing.html', vdata=vdata, dp=dp)


@app.route('/<token_no>')
def pdf_template(token_no):
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute("SELECT *FROM VISITS WHERE TOKEN_NO={t}".format(t=token_no))
    vdata = cur.fetchall()
    for i in vdata:
        visit_time = i[1]
        visit_type = i[2]
        pat_name = i[4]
        doc_name = i[6]
        dep = i[7]
        diag = i[9]
        pres = i[10]
        consult = i[11]
        addfee = i[12]
        totalfee = i[13]
    rendered = render_template('bill.html', token_no=token_no, visit_time=visit_time,
                               visit_type=visit_type, pat_name=pat_name, doc_name=doc_name, dep=dep, diag=diag, pres=pres, consult=consult, addfee=addfee, totalfee=totalfee)
    config = pdfkit.configuration(
        wkhtmltopdf="C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe")
    pdf = pdfkit.from_string(rendered, configuration=config)

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=bill.pdf'

    return response


app.run(debug=True)
