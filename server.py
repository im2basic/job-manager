import re
from flask import Flask, render_template, request, redirect, flash, session
from connection import connectToMySQL
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)

app.secret_key = 'secret'

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')


@app.route("/")
def home():
    db = connectToMySQL('joblist')
    db.query_db('SELECT * FROM users;')
    return render_template("loginReg.html")


@app.route("/register", methods=['POST'])
def process():
    pw_hash = bcrypt.generate_password_hash(request.form['passCon'])
    print(pw_hash)
    db = connectToMySQL('joblist')
    query = "SELECT * FROM users WHERE email = %(email)s;"
    data = {"email": request.form['email']}
    emailcheck = db.query_db(query, data)
    is_valid = True
    if (len(emailcheck) != 0):
        is_valid = False
        flash("Email address already in use")
    if not EMAIL_REGEX.match(request.form['email']):
        is_valid = False
        flash("Invalid email address!")
    if len(request.form['email']) < 10:
        is_valid = False
        flash("please enter a valid email")
    if len(request.form['fname']) < 2:
        is_valid = False
        flash("Please enter a valid first name")
    if len(request.form['lname']) < 2:
        is_valid = False
        flash("Please enter a valid last name")
    if len(request.form['passCon']) < 8:
        is_valid = False
        flash("Password is too short")
    if (request.form['passCon'] != request.form['passCon2']):
        is_valid = False
        flash("Passwords do not match")
    if not is_valid:
        return redirect("/")
    db = connectToMySQL('joblist')
    query = 'INSERT INTO users(first_name, last_name, email,pw_hash, created_at, updated_at) VALUES (%(fn)s, %(ln)s,%(em)s, %(pwh)s, NOW(), NOW());'
    data = {
        "fn": request.form["fname"],
        "ln": request.form["lname"],
        "em": request.form["email"],
        "pwh": pw_hash
    }
    db.query_db(query, data)
    return redirect("/")


@app.route("/login", methods=['POST'])
def login():
    db = connectToMySQL("joblist")
    query = "SELECT * FROM users WHERE email = %(em)s;"
    data = {
        "em": request.form["email"]
    }
    result = db.query_db(query, data)
    if len(result) > 0:
        if bcrypt.check_password_hash(result[0]['pw_hash'], request.form['passCon']):
            session['users'] = result[0]
            return redirect('/dashboard')
    flash("You could not be logged in")
    return redirect("/")


@app.route('/dashboard')
def dash():
    db = connectToMySQL('joblist')
    job = db.query_db('SELECT * FROM works WHERE granted = 0;')
    db = connectToMySQL('joblist')
    user = db.query_db('SELECT * FROM users;')
    db = connectToMySQL('joblist')
    job1 = db.query_db('SELECT * FROM works WHERE granted = 1;')
    return render_template('dashboard.html', job=job, job1=job1, user=user[0])


@app.route('/add/job')
def addjobh():
    db = connectToMySQL('joblist')
    db.query_db('SELECT * FROM works;')
    return render_template("addjob.html")


@app.route("/add/job/process", methods=['POST'])
def makeWishProcess():
    db = connectToMySQL('joblist')
    is_valid = True
    if len(request.form['job']) < 3:
        is_valid = False
        flash("A job must contain 3 characters!")
    if len(request.form['description']) < 3:
        is_valid = False
        flash("A description must contain 3 characters!")
    if len(request.form['location']) < 3:
        is_valid = False
        flash("A location must contain 3 characters!")
    if not is_valid:
        return redirect("/add/job")
    query = "INSERT INTO works (job, description, location, category, worker, created_at, updated_at) VALUES (%(jo)s, %(ds)s, %(lo)s,%(ca)s,%(id)s, NOW(), NOW());"
    data = {
        "jo": request.form['job'],
        "ds": request.form['description'],
        "lo": request.form['location'],
        "ca": request.form['category'],
        "id": session['users']['id']
    }
    print(query)
    print(db)
    db.query_db(query, data)
    return redirect("/dashboard")


@app.route("/<id>/remove")
def user_delete(id):
    db = connectToMySQL('joblist')
    query = "DELETE FROM works WHERE id = %(id)s;"
    data = {
        'id': int(id)
    }
    db.query_db(query, data)
    return redirect("/dashboard")


@app.route("/jobs/<id>/edit/")
def jobsEdit(id):
    db = connectToMySQL('joblist')
    query = "SELECT * FROM works WHERE id = %(id)s;"
    data = {
        "id": id

    }
    job = db.query_db(query, data)
    return render_template("jobEdit.html", job=job[0])


@app.route("/jobs/<id>/edit/process", methods=["POST"])
def jobEditProcess(id):
    db = connectToMySQL('joblist')
    is_valid = True
    if len(request.form['job']) < 3:
        is_valid = False
        flash("A job must contain 3 characters!")
    if len(request.form['description']) < 3:
        is_valid = False
        flash("A description must contain 3 characters!")
    if len(request.form['location']) < 3:
        is_valid = False
        flash("A location must contain 3 characters!")
    if not is_valid:
        return redirect("/jobs/<id>/edit/")
    query = "UPDATE works SET job = %(jo)s , description = %(ds)s,location = %(lo)s, updated_at = NOW() WHERE id= %(id)s;"

    data = {
        "jo": request.form['job'],
        "ds": request.form['description'],
        "lo": request.form['location'],
        "id": id

    }
    db.query_db(query, data)
    return redirect("/dashboard")


@app.route("/added/<id>")
def granted(id):
    db = connectToMySQL('joblist')
    query = "UPDATE works SET granted = '1', updated_at = NOW() WHERE id = %(id)s;"
    data = {
        'id': id
    }
    db.query_db(query, data)
    return redirect("/dashboard")


@app.route("/giveup/<id>")
def giveup(id):
    db = connectToMySQL('joblist')
    query = "UPDATE works SET granted = '0', updated_at = NOW() WHERE id = %(id)s;"
    data = {
        'id': id
    }
    db.query_db(query, data)
    return redirect("/dashboard")


@app.route("/view/<id>")
def jobview(id):
    db = connectToMySQL('joblist')
    query = "SELECT * FROM works WHERE id = %(id)s;"
    data = {
        "id": id

    }
    job = db.query_db(query, data)
    return render_template("viewjob.html", job=job[0])


@app.route('/logout', methods=['POST'])
def logout():
    if request.form['logout'] == 'logout':
        session['logout'] = 0
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)
