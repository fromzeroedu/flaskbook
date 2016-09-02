from flask import Blueprint, request, session, redirect, url_for, abort, render_template
from werkzeug import secure_filename
import os

from user.decorators import login_required
from user.models import User
from feed.models import Message, Feed, POST, COMMENT, LIKE
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
        if uploaded_files and uploaded_files[0].filename != '':
            for file in uploaded_files:
                filename = secure_filename(file.filename)
                file_path = os.path.join(UPLOAD_FOLDER, 'posts', filename)
                file.save(file_path)
                post_images.append(file_path)
                
        # process post
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
            message_type=POST,
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
            return redirect(url_for('home_app.home'))

    else:
        return 'Error!'
        
@feed_app.route('/message/<message_id>', methods=('GET', 'POST'))
def message(message_id):
    form = FeedPostForm()
    message = None
    
    message = Message.objects.filter(id=message_id).first()
    if not message:
        abort(404)
        
    if message and message.parent:
        abort(404)
        
    if form.validate_on_submit() and session.get('username'):
        # process post
        from_user = User.objects.get(username=session.get('username'))
        post = form.post.data
        
        # write the message
        comment = Message(
            from_user=from_user,
            text=post,
            message_type=COMMENT,
            parent=message_id
            ).save()
            
        return redirect(url_for('feed_app.message', message_id=message.id))
            
    return render_template('feed/message.html',
        message=message,
        form=form
    )
    
@feed_app.route('/like/<message_id>', methods=('GET', 'POST'))
@login_required
def like_message(message_id):
    message = None

    message = Message.objects.filter(id=message_id).first()
    if not message:
        abort(404)
    
    if message and message.parent:
        abort(404)
        
    from_user = User.objects.get(username=session.get('username'))
    
    #check if first like
    existing_like = Message.objects.filter(
        parent=message_id,
        message_type=LIKE,
        from_user=from_user).count()

    if not existing_like:
        # write the like
        like = Message(
            from_user=from_user,
            to_user=message.from_user,
            message_type=LIKE,
            parent=message_id
            ).save()
        
    return redirect(url_for('feed_app.message', message_id=message.id))