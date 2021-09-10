from flask import Flask, redirect, render_template, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Feedback 
from helper import query_all, query_by_id
from forms import RegisterForm, LoginForm, FeedbackForm


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///hashing'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

app.config['SECRET_KEY'] = 'very secret key'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

connect_db(app)
db.create_all()

@app.route('/')
def redirect_to_register():
    """ Redirects to user register page """

    return redirect('/register')

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    """ Registers Users: Serves up register form and handles registing users """

    if 'username' in session:
        return redirect(f'/users/{session['username']}')

    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        user = User.register(username, password, email, first_name, last_name)
        db.session.add(user)
        db.session.commit()

        session['username'] = user.username

        return redirect(f'/users/{session['username']}')
    else:
        return render_template('users/register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_user():
    """ Logins Users: serves up login form and handles logging users in """

    if 'username' in session:
        return redirect(f'/users/{session['username']}')
    
    form = LoginForm()

    if form.validate_on_submit():

        username = form.username.data
        password = form.password.data

        user = User.authenticating(User, username, password)
        if user:
            session['username'] = user.username
            return redirect(f'/users/{username}')
        else:
            form.session.errors = ['Invalid Username or Password']
    return render_template('users/login.html', form=form)

@app.route('/users/<username>')
def show_user_details(username):
    """ Displays users details and feedback """

    if 'username' not in session:
        flash('You must be logined in')
        return redirect('/')
    else:
        user = query_by_id(User, username)
        return render_template('users/details.html', user=user, all_feedback=user.feedback)

@app.route('/logout')
def logout():
    """ Logs users out of site """

    session.pop('username')
    return redirect('/')

@app.route('/users/<username>/delete', methods=['POST'])
def delete_user(username):
    """ Deletes users (must be logged in as the user to be valid) """

    if username != session['username']:
        flash('Invalid request')
        return redirect(f'/users/{username}')
    else:
        user = query_by_id(User, username)
        db.session.delete(user)

        db.session.commit()
        session.pop('username')

        return redirect('/login')

# Feedback routes

@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
def add_feedback_form(username):
    """ Adds Feedback: serves up the feedback form and handles submittions """

    if username is not session['username']:
        flash('Invalid request')
        return redirect(f'/users/{username}')
    else:
        form = FeedbackForm()

        if form.validate_on_submit():
            title = form.title.data
            content = form.content.data

            feedback = Feedback(title=title, content=content, username=username)

            db.session.add(feedback)
            db.session.commit()

            return redirect(f'/users/{username}')
        return render_template('feedback/add.html', form=form, username=username)

@app.route('/feedback/<int:feedback_id>/update', methods=['GET', 'POST'])
def update_feedback_form(feedback_id):
    """ Edits Feedback: serves up the feedback form and handles update submittions """

    feedback = query_by_id(Feedback, feedback_id)
    username = feedback.username

    if username is not session['username']:
        flash('Invalid request')
        return redirect(f'/users/{username}')
    else:
        form = FeedbackForm(obj=feedback)

        if form.validate_on_submit():
            feedback.title = form.title.data
            feedback.content = form.content.data

            db.session.commit()
            flash('Feedback updated')

            return redirect(f'/users/{username}')
        
        return render_template('feedback/edit.html', form=form, feedback=feedback)


@app.route('/feedback/<int:feedback_id>/delete')
def delete_feedback(feedback_id):
    """ Deletes a feedback (must be logged in as the user) """
    feedback = query_by_id(Feedback, feedback_id)
    username = feedback.username

    if username is not session['username']:
        flash('Invalid request')

        return redirect(f'/users/{username}')
    else:
        db.session.delete(feedback)
        db.session.commit()

        return redirect(f'/users/{username}')