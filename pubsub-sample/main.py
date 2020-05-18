#!/usr/bin/env python
import logging
import os

from flask import Flask, request, jsonify
from publisher import create_topic, delete_topic, get_topics_list, pub, create_topic
from subscriber import sub, create_sub

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

ALLOWED_EXTENSIONS = {'csv'}

@app.route('/_ah/push-handlers//topic/create',  methods=['POST'])
def create():
    payload = request.json
    topic_name = payload.get('topic_name')
    project_id = os.environ.get('PROJECT_ID')

    create_topic(project_id, topic_name)

    return jsonify({
        "result": "201 Created"
    })

@app.route('/_ah/push-handlers//push',  methods=['POST'])
def push():
    payload = request.json
    topic_name = payload.get('topic_name')
    message = payload.get('message')

    logging.info("topic : {}".format(topic_name))
    logging.info("message : {}".format(message))

    project_id = os.environ.get('PROJECT_ID')

    pub(project_id, topic_name, message)

    return jsonify({
        "result": "201 Created"
    })

@app.route('/_ah/push-handlers//get',  methods=['POST'])
def pull():
    payload = request.json
    subscription_name = payload.get('subscription_name')

    project_id = os.environ.get('PROJECT_ID')

    sub(project_id, subscription_name)

    return jsonify({
        "result": "get"
    })

@app.route('/_ah/push-handlers//subscription/create',  methods=['POST'])
def create_subscription():
    payload = request.json
    topic_name = payload.get('topic_name')
    message = payload.get('subscription_name')

    project_id = os.environ.get('PROJECT_ID')

    create_sub(project_id, topic_name, subscription_name)
 
if __name__ == '__main__':
  app.run()