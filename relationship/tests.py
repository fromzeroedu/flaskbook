from application import create_app as create_app_base
from mongoengine.connection import _get_db
import unittest
from flask import session

from user.models import User
from relationship.models import Relationship

class RelationshipTest(unittest.TestCase):
    def create_app(self):
        self.db_name = 'flaskbook_test'
        return create_app_base(
            MONGODB_SETTINGS={'DB': self.db_name},
            TESTING=True,
            WTF_CSRF_ENABLED=False,
            SECRET_KEY='mySecret!',
            )
            
    def setUp(self):
        self.app_factory = self.create_app()
        self.app = self.app_factory.test_client()
        
    def tearDown(self):
        db = _get_db()
        db.client.drop_database(db)
        
    def user1_dict(self):
        return dict(
            first_name="Jorge",
            last_name="Escobar",
            username="jorge",
            email="jorge@example.com",
            password="test123",
            confirm="test123"
            )
            
    def user2_dict(self):
        return dict(
            first_name="Javier",
            last_name="Escobar",
            username="javier",
            email="javier@example.com",
            password="test123",
            confirm="test123"
            )
            
    def test_friends_operations(self):
        # register users
        rv = self.app.post('/register', data=self.user1_dict(),
            follow_redirects=True)
        assert User.objects.filter(username=self.user1_dict()['username']).count() == 1
        rv = self.app.post('/register', data=self.user2_dict(),
            follow_redirects=True)
        assert User.objects.filter(username=self.user2_dict()['username']).count() == 1
         
        # login the first user
        rv = self.app.post('/login', data=dict(
            username=self.user1_dict()['username'],
            password=self.user1_dict()['password']
        ))
        
        # add second user as a friend
        rv = self.app.get('/add_friend/' + self.user2_dict()['username'],
            follow_redirects=True)
        assert "relationship-friends-requested" in str(rv.data)
        
        # check that only one record exists at this point
        relcount = Relationship.objects.count()
        assert relcount == 1
        
        # login the second user
        rv = self.app.post('/login', data=dict(
            username=self.user2_dict()['username'],
            password=self.user2_dict()['password']
        ))
        
        # check the friend request is pending
        rv = self.app.get('/' + self.user1_dict()['username'])
        assert "relationship-reverse-friends-requested" in str(rv.data)
        
        # confirm first user as a friend
        rv = self.app.get('/add_friend/' + self.user1_dict()['username'],
            follow_redirects=True)
        assert "relationship-friends" in str(rv.data)
        
        # check that two records exist at this point
        relcount = Relationship.objects.count()
        assert relcount == 2
        
        # user2 now unfriends user1
        rv = self.app.get('/remove_friend/' + self.user1_dict()['username'],
            follow_redirects=True)
        assert "relationship-add-friend" in str(rv.data)
        
        # check that no records exist at this point
        relcount = Relationship.objects.count()
        assert relcount == 0
        
        # login the first user
        rv = self.app.post('/login', data=dict(
            username=self.user1_dict()['username'],
            password=self.user1_dict()['password'],
            ))
        
        # check no longer friends
        rv = self.app.get('/' + self.user2_dict()['username'])
        assert "relationship-add-friend" in str(rv.data)
        
    def test_block_operations(self):
        # register users
        rv = self.app.post('/register', data=self.user1_dict(),
            follow_redirects=True)
        assert User.objects.filter(username=self.user1_dict()['username']).count() == 1
        rv = self.app.post('/register', data=self.user2_dict(),
            follow_redirects=True)
        assert User.objects.filter(username=self.user2_dict()['username']).count() == 1
         
        # login the first user
        rv = self.app.post('/login', data=dict(
            username=self.user1_dict()['username'],
            password=self.user1_dict()['password']
        ))
        
        # user1 blocks the second user
        rv = self.app.get('/block/' + self.user2_dict()['username'],
            follow_redirects=True)
        assert "relationship-blocked" in str(rv.data)
        
        # login the second user
        rv = self.app.post('/login', data=dict(
            username=self.user2_dict()['username'],
            password=self.user2_dict()['password']
        ))
        
        # check user1's profile reflects it's blocked
        rv = self.app.get('/' + self.user1_dict()['username'])
        assert "relationship-reverse-blocked" in str(rv.data)
        
        # try to become friends with user1
        rv = self.app.get('/add_friend/' + self.user1_dict()['username'],
            follow_redirects=True)
        assert "relationship-reverse-blocked" in str(rv.data)

        # login the first user
        rv = self.app.post('/login', data=dict(
            username=self.user1_dict()['username'],
            password=self.user1_dict()['password']
        ))
        
        # user1 unblocks user2
        rv = self.app.get('/unblock/' + self.user2_dict()['username'],
            follow_redirects=True)
        assert "relationship-add-friend" in str(rv.data)