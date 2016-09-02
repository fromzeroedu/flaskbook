from flask import Blueprint, session, render_template

from user.models import User
from feed.models import Feed
from feed.forms import FeedPostForm

home_app = Blueprint('home_app', __name__)

@home_app.route('/')
def home():
    
    if session.get('username'):
        form = FeedPostForm()
        
        user = User.objects.filter(
            username=session.get('username')
            ).first()
            
        feed_messages = Feed.objects.filter(
            user=user
            ).order_by('-create_date')[:10]
            
        return render_template('home/feed_home.html',
            user=user,
            form=form,
            feed_messages=feed_messages
            )
            
    else:
        return render_template('home/home.html')