from flask import Blueprint, request, session, redirect, url_for

from user.decorators import login_required
from user.models import User
from feed.models import Message, Feed
# from feed.process import process_message

feed_app = Blueprint('feed_app', __name__)

@feed_app.route('/message/add', methods=('GET', 'POST'))
@login_required
def add_message():
    ref = request.referrer
    if request.method == 'POST':
        from_user = User.objects.get(username=session.get('username'))
        to_user = User.objects.get(username=request.values.get('to_user'))
        post = request.values.get('post')

        # if this is a self post
        if to_user == from_user:
            to_user = None
            
        # write the message
        message = Message(
            from_user=from_user,
            to_user=to_user,
            text=post,
            ).save()
            
        # store on the same user's feed
        feed = Feed(
            user=from_user,
            message=message,
            ).save()
        
        # process the message
        #process_message(message)
        
        if ref:
            return redirect(ref)
        else:
            return redirect(url_for('user_app.profile', username=from_user.username))
