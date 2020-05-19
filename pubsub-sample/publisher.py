#!/usr/bin/env python
import logging
import argparse
import os
import time
from google.cloud import pubsub, pubsub_v1

def get_topics_list(project_id: str):
    """Lists all Pub/Sub topics in the given project

    Arguments:
        project_id {str} -- project id
    """
    # [START pubsub_list_topics]
    publisher = pubsub.PublisherClient()
    project_path = publisher.project_path(project_id)
    topic_list = publisher.list_topics(project_path)
    logging.error(vars(topic_list))
    return 1

    

    # print("befor for")
    # print(vars(topic_list))
    # for topic in topic_list:
    #     print("----")
    #     print(topic)
    # [END pubsub_list_topics]

def register_topic(project_id: str, topic_name: str):
    """Create a new Pub/Sub topic.

    Arguments:
        project_id {str} -- project jid
        topic_name {str} -- topic name
    """
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_name)
    logging.info("topic_path: {}".format(topic_path))

    topic = publisher.create_topic(topic_path)

    logging.info("Topic created: {}".format(topic))

def delete(project_id: set, topic_name: str):
    """delete message

    Arguments:
        project_id {str} -- project id
        topic_name {str} -- topic_name
    """
    # [START pubsub_delete_topic]
    publisher = pubsub.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_name)

    publisher.delete_topic(topic_path)

    logging.info("Topic deleted: {}".format(topic_path))
    # [END pubsub_delete_topic]


def publish_message(project_id: str, topic_name: str, message: str):
    """Publishes message

    Arguments:
        project_id {str} -- project_id
        topic_name {str} -- topic_name
        message {str}    -- message
    """

    publisher = pubsub.PublisherClient()
    # The `topic_path` method creates a fully qualified identifier
    # in the form `projects/{project_id}/topics/{topic_name}`
    topic_path = publisher.topic_path(project_id, topic_name)

    data = message.encode("utf-8")
    logging.info(topic_path)
    # When you publish a message, the client returns a future.
    future = publisher.publish(topic_path, data=data)
    message_id = future.result()
    logging.info(message_id)
        

    logging.info("Published messages.")
    # [END pubsub_quickstart_publisher]
    # [END pubsub_publish]

def pub(project_id, topic_name, message):
    """Publishes a message to a Pub/Sub topic."""
    # [START pubsub_quickstart_pub_client]
    # Initialize a Publisher client.
    client = pubsub_v1.PublisherClient()
    # [END pubsub_quickstart_pub_client]
    # Create a fully qualified identifier in the form of
    # `projects/{project_id}/topics/{topic_name}`
    topic_path = client.topic_path(project_id, topic_name)

    # Data sent to Cloud Pub/Sub must be a bytestring.
    data = message.encode("utf-8")

    # Keep track of the number of published messages.
    ref = dict({"num_messages": 0})

    # When you publish a message, the client returns a future.
    api_future = client.publish(topic_path, data=data)
    api_future.add_done_callback(get_callback(api_future, data, ref))

    # Keep the main thread from exiting while the message future
    # gets resolved in the background.
    while api_future.running():
        time.sleep(0.5)
        logging.info("Published {} message(s).".format(ref["num_messages"]))

def get_callback(api_future, data, ref):
    """Wrap message data in the context of the callback function."""

    def callback(api_future):
        try:
            logging.info(
                "Published message {} now has message ID {}".format(
                    data, api_future.result()
                )
            )
            ref["num_messages"] += 1
        except Exception:
            logging.info(
                "A problem occurred when publishing {}: {}\n".format(
                    data, api_future.exception()
                )
            )
            raise

    return callback

if __name__ == "__main__":
    # project_id = "Google Cloud Project ID"
    project_id = os.environ.get('PROJECT_ID')

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("command", help="publisher action is get | create | delete | publish")

    parser.add_argument("--project_id")
    parser.add_argument("--topic_name")
    parser.add_argument("--message")

    args = parser.parse_args()

    if args.command == "get":
        if not args.project_id == None:
            project_id = args.project_id
        get_topics_list(project_id)
    elif args.command == "create":
        create_topic(project_id, args.topic_name)
    elif args.command == "delete":
        delete_topic(project_id, args.topic_name)
    elif args.command == "publish":
        pub(project_id, args.topic_name, args.message)