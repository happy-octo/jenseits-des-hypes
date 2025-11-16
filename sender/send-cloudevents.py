import sys
import time
import os
from datetime import datetime

import argparse

from cloudevents.http import CloudEvent
from cloudevents.conversion import to_structured
import requests
import logging
import json

import jsonlines


# Constants

# json_file = "data/claims.json"
json_file = "data/insurance_claim_reports.jsonl"
sleep_interval = 5  # Interval in seconds between each request


# Logging
module = sys.modules["__main__"].__file__
logger = logging.getLogger(module)

# E.g. http://broker-ingress.knative-eventing.svc.cluster.local/$NAMESPACE/default
broker_base = "http://broker-ingress.knative-eventing.svc.cluster.local"
broker_name = "default"

#
# Function to read JSON file and load data
#


def load_json_objects(file_path):
    data = []

    # with open(file_path, "r") as file:
    #     data = json.load(file)

    with jsonlines.open(file_path) as reader:
        for obj in reader:
            data.append(obj)
    return data


def send_cloud_event(broker, msg):
    logger.info(f"Send cloud event to {broker}")
    ce_action_type = "semantic.sonnenschirm.rawclaim"
    ce_action_source = "semantic.sonnenschirm/sender"

    # Create a CloudEvent

    try:
        attributes = {
            "type": ce_action_type,
            "source": ce_action_source,
        }

        # Define the event data (payload)
        data = {"claim": msg}

        event = CloudEvent(attributes, data)

        # Creates the HTTP request representation of the CloudEvent in structured content mode
        headers, body = to_structured(event)

        logger.info(f"Send CloudEvent {msg} to {broker}")
        # POST
        response = requests.post(broker, data=body, headers=headers)
        if response.status_code == 200 or response.status_code == 202:
            logger.info(f"Event sent successfully ...")
        else:
            logger.error(
                f"Failed to send event: {response.status_code}, {response.text}"
            )

    except Exception as e:
        logger.error(f"Failed to send CloudEvent to: {broker}, {e}")

    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cloud Event simulator Client")

    parser.add_argument(
        "--broker",
        type=str,
        default="http://localhost:8080/",
        help="brocker address  [default: http://localhost:8080]",
    )

    parser.add_argument(
        "-l",
        "--log-level",
        default="INFO",
        help="Set log level to ERROR, WARNING, INFO or DEBUG",
    )

    parser.add_argument(
        "--ns_default_broker",
        action="store_true",
        help="Send messages to default broker in current namespace [default: false]",
    )

    args = parser.parse_args()

    #
    # Configure logging
    #

    try:
        logging.basicConfig(
            stream=sys.stderr,
            level=args.log_level,
            format="%(name)s (%(levelname)s): %(message)s",
        )
    except ValueError:
        logger.error("Invalid log level: {}".format(args.log_level))
        sys.exit(1)

    logger.info(
        "Log level set: {}".format(logging.getLevelName(logger.getEffectiveLevel()))
    )

    if args.ns_default_broker:
        namespace = os.getenv("NAMESPACE", "default")
        broker = f"{broker_base}/{namespace}/{broker_name}"

    else:
        broker = args.broker

    # Load JSON objects from file
    json_objects = load_json_objects(json_file)

    logger.info(f"Send cloud event to: {broker}")

    # Infinite loop over the JSON objects
    while True:
        for claim in json_objects:
            # Create Cloud Event for each object
            print(claim["description"])
            send_cloud_event(broker, claim["description"])
            # Wait before sending the next event
            time.sleep(sleep_interval)
