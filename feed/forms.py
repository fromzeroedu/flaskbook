from flask_wtf import Form
from wtforms import validators, StringField
from wtforms.widgets import TextArea

class FeedPostForm(Form):
    post = StringField('Post',
        widget=TextArea(),
        validators=[validators.Length(max=1024)]
        )