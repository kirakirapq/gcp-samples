#!/usr/bin/env python

# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import logging
# [START pubsub_quickstart_sub_all]
import argparse

# [START pubsub_quickstart_sub_deps]
from google.cloud import pubsub_v1

# [END pubsub_quickstart_sub_deps]

def create_sub(project_id: str, topic_name: str, subscription_name: str):
    """create subscription

    Arguments:
        project_id {str} -- [description]
        topic_name {str} -- [description]
        subscription_name {str} -- [description]
    """
    subscriber = pubsub_v1.SubscriberClient()
    topic_path = subscriber.topic_path(project_id, topic_name)
    subscription_path = subscriber.subscription_path(
        project_id, subscription_name
    )

    subscription = subscriber.create_subscription(
        subscription_path, topic_path
    )

    logging.info("Subscription created: {}".format(subscription))

    subscriber.close()

def sub(project_id: str, subscription_name: str):
    """get subscription data

    Arguments:
        project_id {str} -- [description]
        subscription_name {str} -- [description]
    """
    # [START pubsub_quickstart_sub_client]
    # Initialize a Subscriber client
    subscriber_client = pubsub_v1.SubscriberClient()
    # [END pubsub_quickstart_sub_client]
    # Create a fully qualified identifier in the form of
    # `projects/{project_id}/subscriptions/{subscription_name}`
    subscription_path = subscriber_client.subscription_path(
        project_id, subscription_name
    )

    def callback(message):
        logging.info(
            "Received message {} of message ID {}\n".format(
                message, message.message_id
            )
        )
        # Acknowledge the message. Unack'ed messages will be redelivered.
        message.ack()

        logging.info("Acknowledged message {}\n".format(message.message_id))
        print("Acknowledged message {}\n".format(message.message_id))

    streaming_pull_future = subscriber_client.subscribe(
        subscription_path, callback=callback
    )
    logging.info("Listening for messages on {}..\n".format(subscription_path))

    try:
        # Calling result() on StreamingPullFuture keeps the main thread from
        # exiting while messages get processed in the callbacks.
        result = streaming_pull_future.result()

        # logging.warning("streaming_pull_future.result: {}".format(result))
    except:  # noqa
        logging.exception("streaming_pull_future exeption")
        streaming_pull_future.cancel()

    subscriber_client.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("project_id", help="Google Cloud project ID")
    parser.add_argument("subscription_name", help="Pub/Sub subscription name")

    args = parser.parse_args()

    sub(args.project_id, args.subscription_name)
# [END pubsub_quickstart_sub_all]
