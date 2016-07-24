from flask import Blueprint, abort, session, redirect, url_for, request, render_template

from user.models import User
from relationship.models import Relationship
from user.decorators import login_required
from utilities.common import email

relationship_app = Blueprint('relationship_app', __name__)

@relationship_app.route('/add_friend/<to_username>')
@login_required
def add_friend(to_username):
    ref = request.referrer
    logged_user = User.objects.filter(username=session.get('username')).first()
    to_user = User.objects.filter(username=to_username).first()
    
    if to_user:
        rel = Relationship.get_relationship(logged_user, to_user)
        to_username = to_user.username
        if rel == "REVERSE_FRIENDS_PENDING":
            Relationship(
                from_user=logged_user,
                to_user=to_user,
                rel_type=Relationship.FRIENDS,
                status=Relationship.APPROVED
                ).save()
            reverse_rel = Relationship.objects.get(
                from_user=to_user,
                to_user=logged_user)
            reverse_rel.status=Relationship.APPROVED
            reverse_rel.save()
        elif rel == None and rel != "REVERSE_BLOCKED":
            Relationship(
                from_user=logged_user,
                to_user=to_user,
                rel_type=Relationship.FRIENDS,
                status=Relationship.PENDING
                ).save()
                
            # email the user
            body_html = render_template(
                'mail/relationship/added_friend.html',
                from_user=logged_user,
                to_user=to_user,
                )
            body_text = render_template(
                'mail/relationship/added_friend.txt',
                from_user=logged_user,
                to_user=to_user,
                )
            email(to_user.email,
                ("%s has requested to be friends") % logged_user.first_name, 
                body_html,
                body_text)
            
        return redirect(ref)
    else:
        abort(404)
        
@relationship_app.route('/remove_friend/<to_username>')
@login_required
def remove_friend(to_username):
    ref = request.referrer
    logged_user = User.objects.filter(username=session.get('username')).first()
    to_user = User.objects.filter(username=to_username).first()
    
    if to_user:
        rel = Relationship.get_relationship(logged_user, to_user)
        to_username = to_user.username
        if rel == "FRIENDS_PENDING" or rel == "FRIENDS_APPROVED" or rel == "REVERSE_FRIENDS_PENDING":
            rel = Relationship.objects.filter(
                from_user=logged_user,
                to_user=to_user).delete()
            reverse_rel = Relationship.objects.filter(
                from_user=to_user,
                to_user=logged_user).delete()
        return redirect(ref)
    else:
        abort(404)

@relationship_app.route('/block/<to_username>')
@login_required
def block(to_username):
    ref = request.referrer
    logged_user = User.objects.filter(username=session.get('username')).first()
    to_user = User.objects.filter(username=to_username).first()
    
    if to_user:
        rel = Relationship.get_relationship(logged_user, to_user)
        to_username = to_user.username
        
        if rel == "FRIENDS_PENDING" or rel == "FRIENDS_APPROVED" or rel == "REVERSE_FRIENDS_PENDING":
            rel = Relationship.objects.filter(
                from_user=logged_user,
                to_user=to_user).delete()
            reverse_rel = Relationship.objects.filter(
                from_user=to_user,
                to_user=logged_user).delete()
        Relationship(
            from_user=logged_user,
            to_user=to_user,
            rel_type=Relationship.BLOCKED,
            status=Relationship.APPROVED
            ).save()
        return redirect(ref)
    else:
        abort(404)
        
@relationship_app.route('/unblock/<to_username>')
@login_required
def unblock(to_username):
    ref = request.referrer
    logged_user = User.objects.filter(username=session.get('username')).first()
    to_user = User.objects.filter(username=to_username).first()
    
    if to_user:
        rel = Relationship.get_relationship(logged_user, to_user)
        to_username = to_user.username
        
        if rel == "BLOCKED":
            rel = Relationship.objects.filter(
                from_user=logged_user,
                to_user=to_user).delete()
        return redirect(ref)
    else:
        abort(404)