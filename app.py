#!/usr/bin/env python3
"""Example bot that returns a synchronous response."""

from flask import Flask, request, json
import requests

app = Flask(__name__)


@app.route('/', methods=['POST'])
def on_event():
  """Handles an event from Google Chat."""
  event = request.get_json()
  if event['type'] == 'MESSAGE':
    text = str(event)
  else:
    return str(event)
  return json.jsonify({'text': text})


if __name__ == '__main__':
  app.run(port=8080, debug=True)