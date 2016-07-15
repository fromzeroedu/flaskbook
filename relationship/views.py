from flask import Blueprint

relationship_app = Blueprint('relationship_app', __name__)

@relationship_app.route('/add_friend', methods=('GET', 'POST'))
def add_friend():
    return "Add Friend"