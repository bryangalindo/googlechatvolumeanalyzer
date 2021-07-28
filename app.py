#!/usr/bin/env python3
import os 
from logging.config import dictConfig

from flask import Flask, request, json
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from dotenv import load_dotenv

from common import constants as c
from common import helpers as h
from models.GoogleCredentials import GoogleCredentials
from models.GoogleService import GoogleService
import utils as u

load_dotenv()

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FlaskIntegration()],

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production,
    traces_sample_rate=1.0
)

scopes = [c.READ_WRITE_SCOPE]
creds = GoogleCredentials(c.TOKEN_JSON_FILE, c.CREDENTIALS_JSON_FILE, scopes).get_oauth_credentials()
service = GoogleService(creds, c.GOOGLE_PRODUCT, c.PRODUCT_VERSION)

app = Flask(__name__)

@app.route('/', methods=['POST'])
def on_event():
    """Handles an event from Google Chat."""
    event = request.get_json()
    if event:
        if event.get('type') == c.ADDED:
            room_name = event.get('space', {}).get('displayName')
            text = 'Thanks for adding me to *{}*!'.format(room_name if room_name else 'this chat')
        elif event.get('type') == c.MESSAGE:
            app.logger.info(f"Pulling in list of thread IDs")
            threads = service.read_single_range(c.SPREADSHEET_ID, c.THREAD_ID_SHEET_RANGE)
            app.logger.info(f"Pulled the following list of threads: {threads}")
            filtered_event_dict = u.create_filtered_dict(event)
            if filtered_event_dict:
                responder_flag = u.is_first_responder(filtered_event_dict['thread_id'], threads)
                values = [
                    filtered_event_dict.get('email'), filtered_event_dict.get('room_id'),
                    filtered_event_dict.get('room_name'), filtered_event_dict.get('thread_id'),
                    filtered_event_dict.get('message'), responder_flag,
                    filtered_event_dict.get('timestamp'),
                    ]
                u.update_google_spreadsheet(values, service)
                responder_type = 'first responder' if responder_flag == True else 'participator'
                text = "Got you down as a {}, <{}>!".format(responder_type, filtered_event_dict['user_id'])
            else:
                text = "Error: Google did not send your message in the correct format. Please try again."
        else:
            return "It's been real"
    return json.jsonify({'text': text})
    
if __name__ == '__main__':
    app.run(port=8000, debug=True)
