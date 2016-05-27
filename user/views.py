from flask import Blueprint

user_app = Blueprint('user_app', __name__)

@user_app.route('/login')
def login():
    return "User login"