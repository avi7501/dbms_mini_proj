from flask import *
import sqlite3



app = Flask(__name__, static_folder='static')

app.config['SECRET_KEY'] = '28852c118493f8b9b2161e506f32d4c5'

con = sqlite3.connect('database.db')
con.execute('''
    CREATE TABLE IF NOT EXISTS LOGIN(
    U_NAME VARCHAR2(10) PRIMARY KEY,
    PWD VARCHAR2(10) NOT NULL,
    TYPE  VARCHAR2(10) NOT NULL);    
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
    DOC_ID REFERENCES DOCTOR(DOC_ID),
    DEP REFERENCES DOCTOR(DEP),
    VISIT_STATUS VARCHAR2(20),
    DIAGNOSIS  VARCHAR2(500),
    PRESCRIPTION VARCHAR2(500));
''')
# conn.execute('''ALTER TABLE DOCTOR ADD ''')
con.close()


  
    

@app.route('/')
@app.route('/home')
def home_page():
    return render_template('index.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signup/', methods=['GET','POST'])
def register():
     PAT_NAME=request.form["name"]
     PAT_DOB=request.form["dob"]
     U_NAME=request.form["uname"]
     PAT_EMAIL=request.form["email"]
     PAT_PHONE=request.form["phone"]
     PAT_GENDER=request.form["gender"]
     PAT_ADDRESS=request.form["address"]
     PWD=request.form["pwd"]
  
     conn = sqlite3.connect('database.db')
     conn.execute('INSERT INTO LOGIN(U_NAME,PWD,TYPE) VALUES("'+U_NAME+'","'+PWD+'","PATIENT");')
     conn.execute('INSERT INTO PATIENT (PAT_NAME,U_NAME,PAT_DOB,PAT_GENDER,PAT_ADDRESS,PAT_PHONE,PAT_EMAIL) VALUES("'+PAT_NAME+'","'+U_NAME+'","'+PAT_DOB+'","'+PAT_GENDER+'","'+PAT_ADDRESS+'","'+PAT_PHONE+'","'+PAT_EMAIL+'");')
     conn.commit()
     conn.close()
     return render_template('login.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/alogin/' ,methods=['POST'])
def asigin():
    con=sqlite3.connect("database.db")
    uname=request.form["uname"]
    pwd=request.form["pwd"]
    cur=con.cursor()
    cur.execute("SELECT U_NAME,PWD FROM LOGIN WHERE U_NAME='{un}' AND PWD='{pw}'".format(un=uname,pw=pwd))
    acc=cur.fetchall()    
    if len(acc)==1:
        session["name"]=uname        
        cur.execute("SELECT *FROM PATIENT WHERE U_NAME='{un}'".format(un=uname))
        pdata=cur.fetchall()        
        return render_template('adashboard.html',pdata=pdata)
    else:
        return ("error")

@app.route('/dlogin/' ,methods=['POST'])
def dsigin():
    con=sqlite3.connect("database.db")
    uname=request.form["uname"]
    pwd=request.form["pwd"]
    cur=con.cursor()
    cur.execute("SELECT U_NAME,PWD FROM LOGIN WHERE U_NAME='{un}' AND PWD='{pw}'".format(un=uname,pw=pwd))
    acc=cur.fetchall()    
    if len(acc)==1:
        session["name"]=uname        
        cur.execute("SELECT *FROM DOCTOR WHERE U_NAME='{un}'".format(un=uname))
        ddata=cur.fetchall()        
        return render_template('ddashboard.html',ddata=ddata)
    else:
        return  render_template('error.html')

@app.route('/ddashboard')
def ddashboard():
    uname=session["name"]
    con=sqlite3.connect("database.db")
    cur=con.cursor()
    cur.execute("SELECT *FROM DOCTOR WHERE U_NAME='{un}'".format(un=uname))
    ddata=cur.fetchall()
    return render_template('ddashboard.html',ddata=ddata)

@app.route('/plogin/',methods=['POST'])
def psignin():    
    con=sqlite3.connect("database.db")
    uname=request.form["uname"]
    pwd=request.form["pwd"]
    cur=con.cursor()
    cur.execute("SELECT U_NAME,PWD FROM LOGIN WHERE U_NAME='{un}' AND PWD='{pw}'".format(un=uname,pw=pwd))
    acc=cur.fetchall()    
    if len(acc)==1:
        session["name"]=uname        
        cur.execute("SELECT *FROM PATIENT WHERE U_NAME='{un}'".format(un=uname))
        pdata=cur.fetchall()        
        return render_template('pdashboard.html',pdata=pdata)
    else:
        return  render_template('error.html')

@app.route('/pappointment')
def pappointment():    
    con=sqlite3.connect("database.db")
    cur=con.cursor()
    cur.execute("SELECT DEP FROM DOCTOR GROUP BY DEP;")
    deps=cur.fetchall() 
    cur=con.cursor()
    cur.execute("SELECT DOC_NAME FROM DOCTOR  WHERE DEP='general';")
    gen=cur.fetchall()  
    return render_template('pappointment.html',deps=deps,gen=gen)

@app.route('/vdermatology')
def vdermatology():
    con=sqlite3.connect("database.db")   
    cur=con.cursor()
    cur.execute("SELECT DOC_NAME FROM DOCTOR  WHERE DEP='dermatology';")
    derma=cur.fetchall()  
    return render_template('vdermatology.html',derma=derma) 

@app.route('/vdermatology/' ,methods=['GET','POST'])
def vderma():
    uname=session["name"]
    dname=request.form.get("dname")
    vdate=request.form.get("vdate")
    vtime=request.form.get("vtime")
    VISIT_TIME=str(vdate)+' '+str(vtime)
    con=sqlite3.connect("database.db")   
    cur=con.cursor()
    cur.execute("SELECT PAT_ID FROM PATIENT WHERE U_NAME='{un}'".format(un=uname))
    pdata=cur.fetchall()
    cur.execute("SELECT DOC_ID,DEP FROM DOCTOR  WHERE DOC_NAME='{d}';".format(d=dname))
    doc=cur.fetchall()
    con.close()
    for i in pdata:
        PAT_ID=i[0]        
    for i  in doc:
        DOC_ID=i[0]
        DEP=i[1]
    print(PAT_ID)
    print(DOC_ID)
    print(VISIT_TIME)
    print(DEP)   
    try:
        conn=sqlite3.connect("database.db",isolation_level=None)   
        conn.execute("INSERT INTO VISITS (VISIT_TIME, VISIT_TYPE, PAT_ID, DOC_ID, DEP,VISIT_STATUS,DIAGNOSIS, PRESCRIPTION) VALUES ('{vd}','Appointment',{p},{d},'{dep}','NOT CHECKED IN','Pending','Pending');".format(vd=VISIT_TIME,p=PAT_ID,d=DOC_ID,dep=DEP))
        # conn.execute('INSERT INTO VISITS (VISIT_TIME, VISIT_TYPE, PAT_ID, DOC_ID, DEP, DIAGNOSIS, PRESCRIPTION) VALUES ("'+VISIT_TIME+'","Appointment","PAT_ID","DOC_ID","'+DEP+'","Pending","Pending");')
        # conn.execute('INSERT INTO LOGIN(U_NAME,PWD,TYPE) VALUES("a","12","DOCTOR");')
        conn.commit()
        conn.close()
    
        return render_template('success.html')
    except:
        return render_template('booked.html')
@app.route('/vpediatric')
def vpediatric():
    con=sqlite3.connect("database.db")   
    cur=con.cursor()
    cur.execute("SELECT DOC_NAME FROM DOCTOR  WHERE DEP='pediatric';")
    pedia=cur.fetchall()  
    return render_template('vpediatric.html',pedia=pedia) 

@app.route('/vpediatric/' ,methods=['GET','POST'])
def vpedia():
    uname=session["name"]
    dname=request.form.get("dname")
    vdate=request.form.get("vdate")
    vtime=request.form.get("vtime")
    VISIT_TIME=str(vdate)+' '+str(vtime)
    con=sqlite3.connect("database.db")   
    cur=con.cursor()
    cur.execute("SELECT PAT_ID FROM PATIENT WHERE U_NAME='{un}'".format(un=uname))
    pdata=cur.fetchall()
    cur.execute("SELECT DOC_ID,DEP FROM DOCTOR  WHERE DOC_NAME='{d}';".format(d=dname))
    doc=cur.fetchall()
    con.close()
    for i in pdata:
        PAT_ID=i[0]        
    for i  in doc:
        DOC_ID=i[0]
        DEP=i[1]
    print(PAT_ID)
    print(DOC_ID)
    print(VISIT_TIME)
    print(DEP)   
    try:
        conn=sqlite3.connect("database.db",isolation_level=None)   
        conn.execute("INSERT INTO VISITS (VISIT_TIME, VISIT_TYPE, PAT_ID, DOC_ID, DEP,VISIT_STATUS,DIAGNOSIS, PRESCRIPTION) VALUES ('{vd}','Appointment',{p},{d},'{dep}','NOT CHECKED IN','Pending','Pending');".format(vd=VISIT_TIME,p=PAT_ID,d=DOC_ID,dep=DEP))
        # conn.execute('INSERT INTO VISITS (VISIT_TIME, VISIT_TYPE, PAT_ID, DOC_ID, DEP, DIAGNOSIS, PRESCRIPTION) VALUES ("'+VISIT_TIME+'","Appointment","PAT_ID","DOC_ID","'+DEP+'","Pending","Pending");')
        # conn.execute('INSERT INTO LOGIN(U_NAME,PWD,TYPE) VALUES("a","12","DOCTOR");')
        conn.commit()
        conn.close()
    
        return render_template('success.html')
    except:
        return render_template('booked.html')

@app.route('/vgeneral')
def vgeneral():
    con=sqlite3.connect("database.db")   
    cur=con.cursor()
    cur.execute("SELECT DOC_NAME FROM DOCTOR  WHERE DEP='general';")
    gen=cur.fetchall()  
    return render_template('vgeneral.html',gen=gen) 

@app.route('/vgeneral/' ,methods=['GET','POST'])
def vgen():
    uname=session["name"]
    dname=request.form.get("dname")
    vdate=request.form.get("vdate")
    vtime=request.form.get("vtime")
    VISIT_TIME=str(vdate)+' '+str(vtime)
    con=sqlite3.connect("database.db")   
    cur=con.cursor()
    cur.execute("SELECT PAT_ID FROM PATIENT WHERE U_NAME='{un}'".format(un=uname))
    pdata=cur.fetchall()
    cur.execute("SELECT DOC_ID,DEP FROM DOCTOR  WHERE DOC_NAME='{d}';".format(d=dname))
    doc=cur.fetchall()
    con.close()
    for i in pdata:
        PAT_ID=i[0]        
    for i  in doc:
        DOC_ID=i[0]
        DEP=i[1]
    print(PAT_ID)
    print(DOC_ID)
    print(VISIT_TIME)
    print(DEP)   
    try:
        conn=sqlite3.connect("database.db",isolation_level=None)   
        conn.execute("INSERT INTO VISITS (VISIT_TIME, VISIT_TYPE, PAT_ID, DOC_ID, DEP,VISIT_STATUS,DIAGNOSIS, PRESCRIPTION) VALUES ('{vd}','Appointment',{p},{d},'{dep}','NOT CHECKED IN','Pending','Pending');".format(vd=VISIT_TIME,p=PAT_ID,d=DOC_ID,dep=DEP))
        # conn.execute('INSERT INTO VISITS (VISIT_TIME, VISIT_TYPE, PAT_ID, DOC_ID, DEP, DIAGNOSIS, PRESCRIPTION) VALUES ("'+VISIT_TIME+'","Appointment","PAT_ID","DOC_ID","'+DEP+'","Pending","Pending");')
        # conn.execute('INSERT INTO LOGIN(U_NAME,PWD,TYPE) VALUES("a","12","DOCTOR");')
        conn.commit()
        conn.close()
    
        return render_template('success.html')
    except:
        return render_template('booked.html')

@app.route('/pvisit')
def pvisit():
    uname=session["name"]
    con=sqlite3.connect("database.db")
    con.row_factory=sqlite3.Row
    cur=con.cursor()
    cur.execute("SELECT *FROM PATIENT WHERE U_NAME='{un}'".format(un=uname))
    pdata=cur.fetchall()    
    id=pdata[0][0]    
    cur.execute("SELECT *FROM VISITS WHERE PAT_ID={i}".format(i=id))
    vdata=cur.fetchall()     
    print(vdata)
    return render_template('pvisit.html',vdata=vdata)


@app.route('/pdashboard')
def profile():
    uname=session["name"]
    con=sqlite3.connect("database.db")
    cur=con.cursor()
    cur.execute("SELECT *FROM PATIENT WHERE U_NAME='{un}'".format(un=uname))
    pdata=cur.fetchall()   
    return render_template('pdashboard.html',pdata=pdata)

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
    uname=session["name"]
    con=sqlite3.connect("database.db")
    con.row_factory=sqlite3.Row
    cur=con.cursor()
    cur.execute("SELECT *FROM DOCTOR WHERE U_NAME='{un}'".format(un=uname))
    ddata=cur.fetchall()    
    did=ddata[0][0]    
    cur.execute("SELECT *FROM VISITS WHERE DOC_ID={i}".format(i=did))
    vddata=cur.fetchall()     
    print(vddata)
    return render_template('dvisits.html',vddata=vddata)

app.run(debug=True)
