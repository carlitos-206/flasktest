from logging import fatal
from flask import Flask, render_template, request, redirect, session,flash
from mysqlconnection import connectToMySQL    # import the function that will return an instance of a connection
#python 3.6 
#import bcrypt
import re
#python 3.7-3.8
#
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app) 
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
app = Flask(__name__)
app.secret_key = "Secret Time" 

@app.route("/")
def index():

    return render_template("index.html")
@app.route('/create_users', methods=["POST"])
def add_user():
    print('fromUSer')
    print(request.form)
    is_valid = True
    if len(request.form['first_name']) < 3:
        is_valid = False
        flash("Please enter First name or make it longer than 3 character")
    if len(request.form['last_name']) < 3:
        is_valid = False
        flash("Please enter a last name or make it longer than 3 character")
    if not EMAIL_REGEX.match(request.form['email']):    # test whether a field matches the pattern
        flash("Invalid email address!")
    #----

    if len(request.form['password'])<8:
            flash("Password too short needs to be least 8 characters")
    if request.form['password'] != request.form['pw_confirmation']:
            flash("Password fields need to match")
    #----
    if is_valid:
        query ="INSERT INTO `examdb`.`users` (`first_name`, `last_name`, `email`, `password`)  VALUES (%(fn)s, %(ln)s, %(mail)s, %(pw)s);"
    
        data = {
            'fn':request.form['first_name'],
            'ln':request.form['last_name'],
            'mail':request.form['email'],
            'pw':bcrypt.generate_password_hash(request.form['password']),
        }
        db= connectToMySQL('examdb')
        user_id=db.query_db(query, data)
        session['user_id']=user_id
        print('new_user:', user_id)
        return redirect("/dashboard")
    else:
        return redirect('/')
#----------------------------------------------MISSING-------------------------------------------------------
@app.route('/login', methods=['POST'])
def login():
    is_valid = True
    if len(request.form['email']) < 1:
        is_valid = False
        flash("Please enter your email")
    if len(request.form['password']) < 1:
        is_valid = False
        flash("Please enter your password")
    
    if not is_valid:
        return redirect("/")
    else:
        mysql = connectToMySQL('examdb')
        query = "SELECT * FROM users WHERE users.email = %(email)s"
        data = {
            'email': request.form['email']
        }
        user = mysql.query_db(query, data)
        if user:
            hashed_password = user[0]['password']
            if bcrypt.check_password_hash(hashed_password, request.form['password']):
                session['user_id'] = user[0]['user_id']               
                return redirect("/dashboard")
            else:
                flash("Password is invalid")
                return redirect("/")
        else:
            flash("Please use a valid email address")
            return redirect("/")
@app.route('/logout')
def logout():
    print('this user is loggin out', session['user_id'])
    session.clear()
    return redirect("/")

#-----------------------------------------END----------------------------------------------------
@app.route('/dashboard')
def inside():
    if 'user_id' not in session:
        return redirect("/")
    print(session['user_id'])
    
    mysql = connectToMySQL('examdb')
    query = "SELECT * FROM users WHERE user_id = %(id)s"
    data = {'id': session['user_id']}
    user = mysql.query_db(query, data)

    mysql = connectToMySQL('examdb')
    shows= mysql.query_db("SELECT * FROM shows WHERE user_id=17;")
    return render_template("dashboard.html", all_shows=shows, user=user[0])
@app.route('/show/<show_id>')
def show(show_id):
    #bring user via session in to the data
    #SELECT * FROM users WHERE id=session{'user_id] 
    mysql = connectToMySQL("examdb")
    query= "SELECT * FROM shows WHERE show_id=%(id)s"
    data = {'id':show_id}
    
    show=mysql.query_db(query, data)
    print(show)
    mysql = connectToMySQL("examdb")
    query= "SELECT * FROM users WHERE user_id=%(id)s LIMIT 1"
    data={
        'id': show[0]['user_id']
    }
    print('THIS TEST:', show[0]['user_id'])
    user=mysql.query_db(query,data)
    # mysql = connectToMySQL("examdb")
    # query= "SELECT examdb.users FROM examdb.shows WHERE show_id=%(id)s"
    # data = {'id':show_id}
    # owner=mysql.query_db(query, data)
    return render_template("show.html", show=show, user=user[0]['first_name'])
@app.route('/newShow')
def newShowForm():
    return render_template('newShow.html')

@app.route('/addShow', methods=['POST'])
def createShow():
    is_valid = True
    if len(request.form['title']) < 3:
        is_valid = False
        flash("title must be more than 3 characters")
    if len(request.form['network']) < 3:
        is_valid = False
        flash("Network need to be longer than 3 character")
    if len(request.form['description']) < 3:
        is_valid = False
        flash("Description need to be longer than 3 character")
    if len(request.form['release_date'])<1:
        is_valid=False
        flash("Release date is needed")
    if is_valid:
        query="INSERT INTO `examdb`.`shows` ( `user_id`, `title`, `network`, `release_date`, `description`) VALUES (%(id)s,%(name)s, %(net)s, %(relDate)s, %(desc)s);"
        data= {
            'id':session['user_id'],
            'name':request.form['title'],
            'net':request.form['network'],
            'relDate':request.form['release_date'],
            'desc':request.form['description']
        }
        db= connectToMySQL('examdb')
        new_show=db.query_db(query, data)
        print('new_show:', new_show)
        return redirect('/dashboard')
    else:
        return redirect('/newShow')

@app.route('/<show_id>/editShow')
    # UPDATE `examdb`.`shows` SET `title` = 'The ' WHERE (`show_id` = '{{show_id}}');
def editShow(show_id):
    query = "SELECT * FROM shows WHERE show_id = %(id)s"
    data = {'id': show_id}
    mysql = connectToMySQL('examdb')
    show = mysql.query_db(query, data)
    return render_template("editShow.html", show = show[0])
@app.route('/<show_id>/updateShow', methods=['POST'])
def update(show_id):
    is_valid = True
    if len(request.form['title']) < 3:
        is_valid = False
        flash("title must be more than 3 characters")
    if len(request.form['network']) < 3:
        is_valid = False
        flash("Network need to be longer than 3 character")
    if len(request.form['description']) < 3:
        is_valid = False
        flash("Description need to be longer than 3 character")
    if len(request.form['release_date'])<1:
        is_valid=False
        flash("Release date is needed")
    if is_valid:
        query = "UPDATE shows SET title = %(name)s, network=%(net)s, release_date=%(relDate)s, description=%(desc)s, updated_at = NOW() WHERE show_id=%(id)s"
        data = {
            'name':request.form['title'],
            'net':request.form['network'],
            'relDate':request.form['release_date'],
            'desc':request.form['description'],
            'id':show_id
        }
        mysql = connectToMySQL('examdb')
        result = mysql.query_db(query, data)
        return redirect("/dashboard")
    else:
        return redirect("/<show_id>/editShow") 
    # query = # UPDATE `examdb`.`shows` SET `title` = 'The ' WHERE (`show_id` = '{{show_id}}');
@app.route("/delete/<show_id>")
def delete(show_id):
    query = "DELETE FROM shows WHERE show_id = %(id)s"
    data = {
        'id': show_id
    }
    mysql = connectToMySQL('examdb')
    mysql.query_db(query, data)
    return redirect("/dashboard")
if __name__ == "__main__":
    app.run(debug=True)
