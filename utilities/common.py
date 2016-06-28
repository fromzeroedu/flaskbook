import time
import boto3
from flask import current_app

def utc_now_ts():
    return int(time.time())
    
def email(to_email, subject, body_html, body_text):
    # don't run this if we're running a test
    if current_app.config.get('TESTING'):
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