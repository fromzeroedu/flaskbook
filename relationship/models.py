from mongoengine import CASCADE

from application import db
from utilities.common import utc_now_ts as now
from user.models import User

class Relationship(db.Document):
    
    FRIENDS = 1
    BLOCKED = -1
    
    RELATIONSHIP_TYPE = (
        (FRIENDS, 'Friends'),
        (BLOCKED, 'Blocked'),
        )
        
    PENDING = 0
    APPROVED = 1
    
    STATUS_TYPE = (
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        )
        
    from_user = db.ReferenceField(User, db_field='fu', reversed_delete_rule=CASCADE)
    to_user = db.ReferenceField(User, db_field='tu', reversed_delete_rule=CASCADE)
    rel_type = db.IntField(db_field='rt', choices=RELATIONSHIP_TYPE)
    status = db.IntField(db_field='s', choices=STATUS_TYPE)
    req_date = db.IntField(db_field='rd', default=now())
    approved_date = db.IntField(db_field="ad", default=0)

    meta = {
        'indexes': [('from_user', 'to_user'), ('from_user', 'to_user', 'rel_type', 'status')]
    }