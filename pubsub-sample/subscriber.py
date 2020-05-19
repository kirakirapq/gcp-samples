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

def register_subscription(project_id: str, topic_name: str, subscription_name: str):
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
    """get message

    Arguments:
        project_id {str} -- [description]
        subscription_name {str} -- [description]

    Returns:
        list -- message.message_id and message.data
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

    timeout=5.0
    result = dict()
    def callback(message):
        logging.warning(
            "Received message {} of message ID {}\n".format(message, message.message_id)
        )
        # Acknowledge the message. Unack'ed messages will be redelivered.
        message.ack()
        return message

    streaming_pull_future = subscriber_client.subscribe(
        subscription_path, callback=callback
    )

    try:
        # Calling result() on StreamingPullFuture keeps the main thread from
        # exiting while messages get processed in the callbacks.
        result = streaming_pull_future.result()

        # logging.warning("streaming_pull_future.result: {}".format(result))
    except Exception as e:  # noqa
        logging.exception(
            "Listening for messages on {} threw an exception: {}.".format(
                subscription_name, e
            )
        )
        streaming_pull_future.cancel()
    

    logging.warning(result)

    subscriber_client.close()

    return result

def sync_sub(project_id: str, subscription_name: str):
    """同期取得

    Arguments:
        project_id {str} -- [description]
        subscription_name {str} -- [description]

    Returns:
        list -- public_message
    """
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(
        project_id, subscription_name
    )

    NUM_MESSAGES = 3

    # The subscriber pulls a specific number of messages.
    response = subscriber.pull(subscription_path, max_messages=NUM_MESSAGES)

    public_message = []
    ack_ids = []
    for received_message in response.received_messages:
        logging.info("Received: {}".format(received_message.message.data))
        ack_ids.append(received_message.ack_id)
        public_message.append(
            {
                "message_id": received_message.message.message_id,
                "message_data": received_message.message.data.decode("utf-8")
            }
        )

    # Acknowledges the received messages so they will not be sent again.
    subscriber.acknowledge(subscription_path, ack_ids)

    logging.info(
        "Received and acknowledged {} messages. Done.".format(
            len(response.received_messages)
        )
    )

    subscriber.close()

    return public_message


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
