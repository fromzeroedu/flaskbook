from mongoengine import CASCADE
from flask import url_for
import os

from application import db
from utilities.common import utc_now_ts_ms as now
from user.models import User
from utilities.common import linkify, ms_stamp_humanize
from settings import STATIC_IMAGE_URL, AWS_BUCKET, AWS_CONTENT_URL

POST = 1
COMMENT = 2
LIKE = 3

MESSAGE_TYPE = (
    (POST, 'Post'),
    (COMMENT, 'Comment'),
    (LIKE, 'Like'),
    )

class Message(db.Document):
    from_user = db.ReferenceField(User, db_field="fu", reverse_delete_rule=CASCADE)
    to_user = db.ReferenceField(User, db_field="tu", default=None, reverse_delete_rule=CASCADE)
    text = db.StringField(db_field="t", max_length=1024)
    live = db.BooleanField(db_field="l", default=None)
    create_date = db.LongField(db_field="c", default=now())
    parent = db.ObjectIdField(db_field="p", default=None)
    images = db.ListField(db_field="ii")
    message_type = db.IntField(db_field='mt', default=POST, choices=MESSAGE_TYPE)
    
    @property
    def text_linkified(self):
        return linkify(self.text)
        
    @property
    def human_timestamp(self):
        return ms_stamp_humanize(self.create_date)
        
    @property
    def comments(self):
        return Message.objects.filter(parent=self.id, message_type=COMMENT).order_by('create_date')

    @property
    def likes(self):
        return Message.objects.filter(parent=self.id, message_type=LIKE).order_by('-create_date')
        
    def post_imgsrc(self, image_ts, size):
        if AWS_BUCKET:
            return os.path.join(AWS_CONTENT_URL, AWS_BUCKET, 'posts', '%s.%s.%s.png' % (self.id, image_ts, size))
        else:
            return url_for('static', filename=os.path.join(STATIC_IMAGE_URL, 'posts', '%s.%s.%s.png' % (self.id, image_ts, size)))
    
    meta = {
        'indexes': [('from_user', 'to_user', '-create_date', 'parent', 'message_type', 'live')]
    }
    
class Feed(db.Document):
    user = db.ReferenceField(User, db_field="u", reverse_delete_rule=CASCADE)
    message = db.ReferenceField(Message, db_field="m", reverse_delete_rule=CASCADE)
    create_date = db.LongField(db_field="c", default=now())
    
    meta = {
        'indexes': [('user', '-create_date')]
    }