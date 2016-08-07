from flask import Blueprint, request, session, redirect, url_for
from werkzeug import secure_filename
import os

from user.decorators import login_required
from user.models import User
from feed.models import Message, Feed
from feed.process import process_message
from feed.forms import FeedPostForm
from settings import UPLOAD_FOLDER
from utilities.imaging import image_height_transform

feed_app = Blueprint('feed_app', __name__)

@feed_app.route('/message/add', methods=('GET', 'POST'))
@login_required
def add_message():
    ref = request.referrer
    form = FeedPostForm()
    
    if form.validate_on_submit():
        # process images
        post_images = []
        uploaded_files = request.files.getlist('images')
        if uploaded_files[0].filename != '':
            for file in uploaded_files:
                filename = secure_filename(file.filename)
                file_path = os.path.join(UPLOAD_FOLDER, 'posts', filename)
                file.save(file_path)
                post_images.append(file_path)
                
        # pocess post
        from_user = User.objects.get(username=session.get('username'))
        to_user = User.objects.get(username=request.values.get('to_user'))
        post = form.post.data

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
        
        # store images
        if len(post_images):
            images = []
            for file_path in post_images:
                (image_ts, width) = image_height_transform(file_path, 'posts', str(message.id))
                images.append({"ts": str(image_ts), "w": str(width)})
            message.images = images
            message.save()
            
        # process the message
        process_message(message)
        
        if ref:
            return redirect(ref)
        else:
            return redirect(url_for('user_app.profile', username=from_user.username))

    else:
        return 'Error!'