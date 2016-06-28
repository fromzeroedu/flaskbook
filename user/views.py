from flask import Blueprint, render_template, request, redirect, session, url_for, abort
import bcrypt
import uuid

from user.models import User
from user.forms import RegisterForm, LoginForm, EditForm
from utilities.common import email

user_app = Blueprint('user_app', __name__)
    
@user_app.route('/register', methods=('GET', 'POST'))
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(form.password.data, salt)
        code = str(uuid.uuid4())
        user = User(
            username=form.username.data,
            password=hashed_password,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            change_configuration={
                "new_email": form.email.data.lower(),
                "confirmation_code": code
                }
            )
            
        # email the user
        body_html = render_template('mail/user/register.html', user=user)
        body_text = render_template('mail/user/register.txt', user=user)
        email(user.email, "Welcome to Flaskbook", body_html, body_text)
        
        user.save()
        return "User registered"
    return render_template('user/register.html', form=form)
    
@user_app.route('/login', methods=('GET', 'POST'))
def login():
    form = LoginForm()
    error = None
    
    if request.method == 'GET' and request.args.get('next'):
        session['next'] = request.args.get('next')
        
    if form.validate_on_submit():
        user = User.objects.filter(
            username=form.username.data
            ).first()
        if user:
            if bcrypt.hashpw(form.password.data, user.password) == user.password:
                session['username'] = form.username.data
                if 'next' in session:
                    next = session.get('next')
                    session.pop('next')
                    return redirect(next)
                else:
                    return 'User logged in'
            else:
                user = None
        if not user:
            error = 'Incorrect credentials'
    return render_template('user/login.html', form=form, error=error)
    
@user_app.route('/logout', methods=('GET', 'POST'))
def logout():
    session.pop('username')
    return redirect(url_for('user_app.login'))
    
@user_app.route('/<username>', methods=('GET', 'POST'))
def profile(username):
    edit_profile = False
    user = User.objects.filter(username=username).first()
    if session.get('username') and user.username == session.get('username'):
        edit_profile = True
    if user:
        return render_template('user/profile.html', user=user, edit_profile=edit_profile)
    else:
        abort(404)
        
@user_app.route('/edit', methods=('GET', 'POST'))
def edit():
    error = None
    message = None
    user = User.objects.filter(username=session.get('username')).first()
    if user:
        form = EditForm(obj=user)
        if form.validate_on_submit():
            if user.username != form.username.data.lower():
                if User.objects.filter(username=form.username.data.lower()).first():
                    error = "Username already exists"
                else:
                    session['username'] = form.username.data.lower()
                    form.username.data = form.username.data.lower()
            if user.email != form.email.data.lower():
                if User.objects.filter(email=form.email.data.lower()).first():
                    error = "Email already exists"
                else:
                    code = str(uuid.uuid4())
                    
                    user.change_configuration = {
                        "new_email": form.email.data.lower(),
                        "confirmation_code": code
                    }
                    user.email_confirmed = False
                    form.email.data = user.email
                    message = "You will need to confirm the new email to complete this change"
                    
                    # email the user
                    body_html = render_template('mail/user/change_email.html', user=user)
                    body_text = render_template('mail/user/change_email.txt', user=user)
                    email(user.change_configuration['new_email'], "Confirm your new email", body_html, body_text)
                    
            if not error:
                form.populate_obj(user)
                user.save()
                if not message:
                    message = "Profile updated"
    
        return render_template("user/edit.html", form=form, error=error, message=message)
    else:
        abort(404)
        
@user_app.route('/confirm/<username>/<code>', methods=('GET', 'POST'))
def confirm(username, code):
    user = User.objects.filter(username=username).first()
    if user and user.change_configuration and user.change_configuration.get('confirmation_code'):
        if code == user.change_configuration.get('confirmation_code'):
            user.email = user.change_configuration.get('new_email')
            user.change_configuration = {}
            user.email_confirmed = True
            user.save()
            return render_template('user/email_confirmed.html')
    else:
        abort(404)
            