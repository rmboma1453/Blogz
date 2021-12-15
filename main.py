from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import cgi
from bcrypt import gensalt, hashpw,checkpw
from app import app, db
from models import Blog, User

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        users = User.query.filter_by(email=email)
        if users.count() == 1:
            user = users.first()
            if checkpw(password.encode("utf-8"), user.hash.encode("utf-8")):
                session['user'] = user.email
                flash('Welcome back, '+ user.email)
                return redirect("/")
            flash('Wrong Password')
            return redirect("/login")
        flash('Wrong Username')
        
        return redirect("/login")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']
        
        if email =='':
            flash('You did not enter an email.')
            return redirect('redirect')
        if not is_email(email):
            flash('Oups! "' + email + '". A correct email must have period -.- following by -@- in its form.')
            return redirect('/register')
        if len(email) <= 3:
            flash('Email is too short. Must have more than three characters.')
            return redirect('/register')
        email_db_count = User.query.filter_by(email=email).count()
        if email_db_count > 0:
            flash('Yikes!! "' + email + '" is already taken and password reminders are not implemented')
            return redirect('/register')
        
        if password =='':
            flash('You did not enter a password.')
            return redirect('/register')
        if len(password) <= 3:
            flash('Password is too short. Must have more than three characters')
            return redirect('/register')
        if password != verify:
            flash('Passwords did not match')
            return redirect('/register')
        #Hashing the password
        salt = gensalt()
        hash = hashpw(password.encode("utf-8"), salt)
        
        user = User(email=email, hash=hash)
        db.session.add(user)
        db.session.commit()
        session['user'] = user.email
        return redirect("/")
    else:
        return render_template('register.html')

def is_email(string):
    atsign_index = string.find('@')
    atsign_present = atsign_index >= 0
    if not atsign_present:
        return False
    else:
        domain_dot_index = string.find('.', atsign_index)
        domain_dot_present = domain_dot_index >= 0
        return domain_dot_present
@app.route("/logout", methods=['POST'])
def logout():
    del session['user']
    return redirect("/login")

@app.route("/add", methods=['POST','GET'])
def add():
    title_name = ''
    body_name=''
    if request.method == 'POST':
        title_name = request.form['title']
        body_name = request.form['body']
        
        #initializing all the error statements
        title_error =''
        body_error =''
        # checking for errors
        if (title_name == '') and (not body_name == ''):
            title_error = 'You did not enter the title'
            title_name = ''
        elif (body_name == '') and (not title_name == ''):
            body_error = 'You did not write a blog'
            body_name = ''
        elif (title_name == '') and (body_name == ''):
            title_error = 'You did not enter the title'
            body_error = 'You did not write a blog'
            title_name = ''
            body_name = ''

        if (not title_error and not body_error):
            new_blog = Blog(title_name, body_name,logged_in_user())
            db.session.add(new_blog)
            db.session.commit()
            return render_template('add-confirmation.html',new_blog=new_blog)

        else:
            return render_template('add.html',title_error=title_error,body_error=body_error) 

    #if we have the id query parameter
    reqId = request.args.get('id')
    if not (reqId is None):
        post = Blog.query.filter_by(id=reqId).first()
    
        #use the id to query the database
        return render_template('add-confirmation.html',new_blog=post)

    else:
        return render_template('add.html')
    
@app.route('/index', methods =['GET'] )
def homepage():
    users= User.query.all()
    blogs = Blog.query.all()

    # userid = request.args.get('id')
    # current_user=""
    # for user in users:
    #     if(user.id == int(userid)):
    #         current_user = user
    #         break
    userposts = []    
    for blog in blogs:
        userposts.append(blog)
    return render_template("index.html", blogs = userposts, users= users)
    
    # return render_template('index.html',users=users,blogs=blogs)
    
    
    
@app.route('/')
def index():
    blogs = Blog.query.filter_by(owner_id=logged_in_user()).all()
    return render_template('edit.html',title ="Build A Blog" ,blogs=blogs)

def logged_in_user():
    owner = User.query.filter_by(email=session['user']).first()
    return owner.id

endpoints_without_login = ['login', 'register']

@app.before_request
def require_login():
    if not ('user' in session or request.endpoint in endpoints_without_login):
        return redirect("/register")

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RU'

if __name__ == "__main__":
    app.run()