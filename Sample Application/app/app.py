import re  
import logging
import os
from flask import Flask, flash, get_flashed_messages, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__) 

app.secret_key = 'abcdefgh'
  
app.config['MYSQL_HOST'] = 'db'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'cs353hw4db'
   
mysql = MySQL(app)  

@app.route('/')

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute('SELECT * FROM student WHERE sname = %s AND sid = %s', (username, password))
        print("fetched")
        user = cursor.fetchone()

        if user:
            session['loggedin'] = True
            session['userid'] = user['sid']
            session['username'] = user['sname']
            message = 'Logged in successfully!'
            return redirect(url_for('lists'))
        else:
            message = 'Please enter correct student name / ID !'
    
    return render_template('login.html', message=message)


##logout
@app.route("/logout", methods=['GET', "POST"])
def logout():
    session['loggedin'] = False
    session['userid'] = ""
    session['username'] = ""
    session['email'] = ""
    return redirect(url_for("login"))

@app.route('/register', methods =['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST' and 'sname' in request.form and 'sid' in request.form and 'bdate' in request.form and 'dept' in request.form and 'syear' in request.form and 'gpa' in request.form:
        sname = request.form['sname']
        sid = request.form['sid']
        bdate = request.form['bdate']
        dept = request.form['dept']
        syear = request.form['syear']
        gpa = request.form['gpa']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM student WHERE sid = %s', (sid, ))
        account = cursor.fetchone()
        if account:
            message = 'Choose a different id!'
  
        elif not sname or not sid or not bdate or not dept or not syear or not gpa:
            message = 'Please fill out the form!'

        else:
            cursor.execute('INSERT INTO student (sid, sname, bdate, dept, syear, gpa) VALUES (%s, %s, %s, %s, %s, %s)', (sid,sname,bdate,dept,syear,gpa))
            mysql.connection.commit()
            message = 'User successfully created!'

    elif request.method == 'POST':

        message = 'Please fill all the fields!'
    return render_template('register.html', message = message)

@app.route('/list', methods =['GET', 'POST'])
def lists():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    sid = session['userid']
    
    query = """
    SELECT C.cid, C.cname, C.quota, C.gpa_threshold 
    FROM company C, applied A
    WHERE C.cid = A.cid AND
    A.sid = %s
    """

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(query, (sid,))
    companies = cursor.fetchall()
    
    message = ''
    
    if request.args.get("message") :
        message = request.args.get("message")

    return render_template('list.html', companies=companies, message = message)

@app.route('/analysis', methods =['GET', 'POST'])
def analysis():

    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    sid = session['userid']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    query1 = """
    SELECT C.cid, C.cname, C.quota, C.gpa_threshold
    FROM company C
    JOIN applied A ON C.cid = A.cid
    JOIN student S ON A.sid = S.sid
    WHERE S.sid = %s
    ORDER BY C.gpa_threshold DESC
    """
    cursor.execute(query1, (sid,))
    companies = cursor.fetchall()

    query2 = """
    SELECT ROUND(MAX(C.gpa_threshold),2) AS max_gpa_threshold, ROUND(MIN(C.gpa_threshold),2) AS min_gpa_threshold
    FROM company C
    JOIN applied A ON C.cid = A.cid
    WHERE A.sid = %s;
    """
    cursor.execute(query2, (sid,))
    min_max_gpa_companies = cursor.fetchall()

    query3 = """
    SELECT COUNT(DISTINCT A.cid) AS application_count, C.city
    FROM company C
    JOIN applied A ON C.cid = A.cid
    WHERE A.sid = %s
    GROUP BY C.city
    """
    cursor.execute(query3, (sid,))
    company_by_city = cursor.fetchall()

    query4 = """
    SELECT 
    MAX(C.quota) AS company_with_max_quota,
    MIN(C.quota) AS company_with_min_quota
    FROM company C
    JOIN applied A ON C.cid = A.cid
    WHERE A.sid = %s
    """
    cursor.execute(query4, (sid,))
    quotas = cursor.fetchall()
    return render_template('analysis.html', companies=companies, min_max_gpa_companies = min_max_gpa_companies, company_by_city=company_by_city, quotas=quotas)



### CANCEL APPLICATION 
@app.route("/cancel/<cid>")
def cancel(cid):
    sid = session['userid']
    message = ''
    success = 0
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute('DELETE FROM applied WHERE sid = %s AND cid = %s', (sid, cid))
        mysql.connection.commit()
        success = 1
        message = 'Application cancelled successfully.'
    except Exception as e:
        # Rollback in case there is any error
        mysql.rollback()
        message = 'An error occurred: ' + str(e), 'error',

    if success :
        query2 = """
        UPDATE company SET quota = quota + 1 WHERE cid = %s
        """
        cursor.execute(query2, (cid,))
        mysql.connection.commit()

    return redirect(url_for("lists", message = message))


### APPLY
@app.route('/test_apply', methods =['GET', 'POST'])
def test_apply():
    message = ''
    sid = session['userid']

    query = """
    SELECT COUNT(cid) as CNT 
    FROM applied 
    WHERE sid = %s
    """

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute(query, (sid,))
    app_cnt = cursor.fetchone()

    if app_cnt and app_cnt['CNT'] >= 3:
        message = 'Cannot apply more than 3 companies'
        return redirect(url_for("lists", message = message))


    return redirect(url_for("apply_list"))

@app.route('/apply_list', methods =['GET', 'POST'])
def apply_list():
    sid = session['userid']
    search = ''

    ##get companies that the student have not applied to and their gpa is enough to apply and quota is not full for company
    query = """
    SELECT C.cid, C.cname
    FROM company C
    WHERE C.cid NOT IN (SELECT A.cid 
                        FROM applied A
                        WHERE A.sid = %s)
    AND C.gpa_threshold <= (SELECT gpa FROM student WHERE sid = %s)
    AND C.quota > 0
    """

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.args.get("search_result") :
        search = request.args.get("search_result")
        partial_id = f"%{search}%"
        query = query + ' AND C.cid LIKE %s'
        cursor.execute(query, (sid,sid,partial_id))

    else:
        cursor.execute(query, (sid,sid))
        

    companies = cursor.fetchall()
    ##apply
    return render_template('application.html', companies = companies)

@app.route('/apply/<cid>', methods =['GET', 'POST'])
def apply(cid):

    sid = session['userid']
    success = 0

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    query = """
    INSERT INTO applied(sid, cid)
    VALUE(%s,%s)
    """
    try:
        cursor.execute(query, (sid, cid))
        mysql.connection.commit()
        message = 'Application submitted successfully.'
        success =  1
    except Exception as e:
        mysql.rollback()
        message = 'An error occurred: ' + str(e), 'error'

    if success :
        query2 = """
        UPDATE company SET quota = quota - 1 WHERE cid = %s
        """
        cursor.execute(query2, (cid,))
        mysql.connection.commit()
    
    return redirect(url_for("lists", message = message))


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
