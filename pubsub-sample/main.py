#!/usr/bin/env python
import json
import logging
import os

from flask import Flask, request, jsonify, Response
from publisher import register_topic, delete, get_topics_list, pub
from subscriber import sub, sync_sub, register_subscription

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

ALLOWED_EXTENSIONS = {'csv'}


@app.route('/_ah/push-handlers//topic/create',  methods=['POST'])
def add_topic():
    payload = request.json
    topic_name = payload.get('topic_name')
    project_id = os.environ.get('PROJECT_ID')

    register_topic(project_id, topic_name)

    return jsonify({
        "result": "201 Created"
    })


@app.route('/_ah/push-handlers//push',  methods=['POST'])
def push_message():
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
def pull_messages():
    payload = request.json
    subscription_name = payload.get('subscription_name')
    logging.warning("test")
    project_id = os.environ.get('PROJECT_ID')

    message = sync_sub(project_id, subscription_name)

    return Response(json.dumps(message),  mimetype='application/json')


@app.route('/_ah/push-handlers//subscription/create',  methods=['POST'])
def add_subscription():
    payload = request.json
    topic_name = payload.get('topic_name')
    message = payload.get('subscription_name')

    project_id = os.environ.get('PROJECT_ID')

    register_subscription(project_id, topic_name, subscription_name)


if __name__ == '__main__':
    app.run()
