from flask import Flask, request, make_response, jsonify, render_template
import uuid
import os
import logging
from cloudevents.http import from_http

from collections import deque

log_level = os.getenv("LOGLEVEL", default="INFO").upper()
maxlen = int(os.getenv("MAXEVENTS", default="10"))

# Store up to 20 recent events in a deque
event_log = deque(maxlen=maxlen)

app = Flask(__name__)

logging.basicConfig(level=getattr(logging, log_level, logging.INFO))

werkzeug_logger = logging.getLogger("werkzeug")
werkzeug_logger.setLevel(getattr(logging, log_level, logging.INFO))


@app.route("/")
def index():
    # Render the HTML template with the event log
    return render_template("index.html", events=list(event_log))


# Receive CloudEvent
@app.route("/", methods=["POST"])
def receive_cloudevent():
    # Try to parse the incoming JSON data as a Cloud Event
    try:
        # create a CloudEvent
        event = from_http(request.headers, request.get_data())

        # app.logger.info(f"Event: {event}")

        app.logger.info(
            f"Found {event['id']} from {event['source']} with type "
            f"{event['type']} and specversion {event['specversion']}"
        )

        data = event.data
        # app.logger.info(f"Data: {data},{type(data)}")

        claim = data.get("claim", "")
        app.logger.info(f"Claim: {type(claim)}:{claim}")

        time_received = data.get("time_received", "")

        extract_data = data.get("data", {})

        app.logger.info(f"extract_data: {type(extract_data)}:{extract_data}")

        # INFO:backend:extract_data: <class 'dict'>:{'Customer': {'Name': 'Emily Patel', 'Address': '456 Maple Street', 'Policy Number': 'EV-901234567', 'Telephone Number': '(555) 901-2345'}, 'Case': {'Accident Location': 'Oakdale, CA 95361', 'Date': 'January 15th, 2024', 'Time': '9:45 AM'}}

        name = extract_data["Customer"]["Name"]
        app.logger.info(f"Name: {name}")

        address = extract_data["Customer"]["Address"]
        app.logger.info(f"Address: {address}")

        policy = extract_data["Customer"]["Policy Number"]
        app.logger.info(f"Policy: {policy}")

        phone = extract_data["Customer"]["Telephone Number"]
        app.logger.info(f"Telephone: {phone}")

        location = extract_data["Case"]["Accident Location"]
        app.logger.info(f"Accident Location: {location}")

        adate = extract_data["Case"]["Date"]
        app.logger.info(f"Date: {adate}")

        atime = extract_data["Case"]["Time"]
        app.logger.info(f"Time: {atime}")

        # Append the event to the event_log

        event_log.appendleft(
            {
                "time": time_received,
                "name": name,
                "address": address,
                "policy": policy,
                "telephone": phone,
                "location": location,
                "adate": adate,
                "atime": atime,
                "message": claim.replace("\n", "  "),
            }
        )

        # Return a success response
        response = make_response({"msg": "Hey, semantic-sonnenschirm"})
        response.headers["Ce-Id"] = str(uuid.uuid4())
        response.headers["Ce-specversion"] = "1.0"
        response.headers["Ce-Source"] = "semantic.sonnenschirm/backend"
        response.headers["Ce-Type"] = "semantic.sonnenschirm.result"
        return response

    except Exception as e:
        print("Error processing event:", e)
        return jsonify({"error": "Failed to process Cloud Event"}), 500


if __name__ == "__main__":
    app.logger.info("Start backend ...")
    app.run(debug=False, host="0.0.0.0", port=8080)
