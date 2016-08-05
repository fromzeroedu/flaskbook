from mongoengine import CASCADE

from application import db
from utilities.common import utc_now_ts as now
from user.models import User

class Message(db.Document):
    from_user = db.ReferenceField(User, db_field="fu", reverse_delete_rule=CASCADE)
    to_user = db.ReferenceField(User, db_field="tu", default=None, reverse_delete_rule=CASCADE)
    text = db.StringField(db_field="t", max_length=1024)
    live = db.BooleanField(db_field="l", default=None)
    create_date = db.IntField(db_field="c", default=now())
    parent = db.ObjectIdField(db_field="p", default=None)
    image = db.StringField(db_field="i", default=None)
    
    meta = {
        'indexes': [('from_user', 'to_user', '-create_date', 'parent', 'live')]
    }
    
class Feed(db.Document):
    user = db.ReferenceField(User, db_field="u", reverse_delete_rule=CASCADE)
    message = db.ReferenceField(Message, db_field="m", reverse_delete_rule=CASCADE)
    parent = db.ObjectIdField(db_field="p", default=None)
    create_date = db.IntField(db_field="c", default=now())
    
    meta = {
        'indexes': [('user', 'parent', '-create_date')]
    }