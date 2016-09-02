from feed.models import Message, Feed
from relationship.models import Relationship

def process_message(message):
    
    # get the from_user's friends
    from_user = message.from_user
    friends = Relationship.objects.filter(
        from_user=from_user,
        rel_type=Relationship.FRIENDS,
        status=Relationship.APPROVED
    )
    
    # get the from_user's friends
    for friend in friends:
        rel = Relationship.get_relationship(friend.to_user, message.to_user)
        if rel != "BLOCKED":
            feed = Feed(
                user=friend.to_user,
                message=message
            ).save()
    return True