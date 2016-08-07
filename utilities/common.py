import time
import boto3
from flask import current_app
import datetime
import arrow
import bleach

def utc_now_ts():
    return int(time.time())
    
def ms_stamp_humanize(ts):
    ts = datetime.datetime.fromtimestamp(ts)
    return arrow.get(ts).humanize()
    
def linkify(text):
    text = bleach.clean(text, tags=[], attributes={}, styles=[], strip=True)
    return bleach.linkify(text)
    
def email(to_email, subject, body_html, body_text):
    # don't run this if we're running a test or setting is False
    if current_app.config.get('TESTING') or not current_app.config.get('AWS_SEND_MAIL'):
        return False

    client = boto3.client('ses')
    return client.send_email(
        Source='webmaster@fromzero.io',
            Destination={
                'ToAddresses': [
                    to_email,
                ]
            },
        Message={
            'Subject': {
                'Data': subject,
                'Charset': 'UTF-8'
            },
            'Body': {
                'Text': {
                    'Data': body_text,
                    'Charset': 'UTF-8'
                },
                'Html': {
                    'Data': body_html,
                    'Charset': 'UTF-8'
                },                
            }
        }
    )