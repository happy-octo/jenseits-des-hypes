from flask import Flask, request, make_response, jsonify
import uuid
import os
import logging
from cloudevents.http import from_http
import datetime
from phi.agent import Agent, RunResponse
from phi.model.ollama import Ollama
import json
import time
import requests

log_level = os.getenv("LOGLEVEL", default="INFO").upper()
ollama_host = os.getenv("OLLAMA_HOST", default="http://localhost:11434")
model_name = os.getenv("MODEL_NAME", "sroecker/nuextract-tiny-v1.5:latest")


app = Flask(__name__)

logging.basicConfig(level=getattr(logging, log_level, logging.INFO))

werkzeug_logger = logging.getLogger("werkzeug")
werkzeug_logger.setLevel(getattr(logging, log_level, logging.INFO))

# Constants
CHECK_INTERVAL = 10  # seconds
TIMEOUT_DURATION = 5 * 60  # 60  # 5 minutes in seconds


def check_model():
    start_time = time.time()

    while True:
        if time.time() - start_time >= TIMEOUT_DURATION:
            app.logger.info("Timeout reached. Exiting.")
            exit(1)

        try:
            # Perform HTTP GET
            URL = ollama_host + "/api/tags"
            response = requests.get(URL)
            app.logger.info(f"GET {URL} - Status Code: {response.status_code}")

            if response.status_code != 200:
                app.logger.info("HTTP Service not availve (yet)")

            else:
                # Parse the JSON response
                try:
                    data = response.json()
                except ValueError:
                    app.logger.info("Invalid JSON received.")

                # Check the "models" list
                models = data.get("models", [])

                model_deployed = False
                for model in models:
                    if model.get("model") == model_name:
                        app.logger.info(f"Model '{model_name}' found in response.")
                        return

                if not model_deployed:
                    app.logger.info(
                        f"Model '{model_name}' not found in response. Try to pull .."
                    )
                    post_payload = {"name": model_name}
                    headers = {"Content-Type": "application/json"}
                    POST_URL = ollama_host + "/api/pull"
                    post_response = requests.post(
                        POST_URL, json=post_payload, headers=headers
                    )
                    app.logger.info(
                        f"POST {POST_URL} - Status Code: {post_response.status_code}"
                    )

                    if post_response.status_code == 200:
                        app.logger.info("Model pulled successfully.")
                    else:
                        app.logger.warning(
                            f"Model pull failed. Status Code: {post_response.status_code}"
                        )

        except requests.RequestException as e:
            app.logger.error(f"HTTP request failed: {e}")

        # Wait before the next check
        time.sleep(CHECK_INTERVAL)


def json_to_dict(json_string):
    """
    Converts a JSON string to a dictionary with error handling.

    Args:
        json_string (str): The JSON string to convert.

    Returns:
        dict: The resulting dictionary if the JSON is valid.
        None: If the JSON is invalid, returns None.
    """
    try:
        # Attempt to parse the JSON string
        data = json.loads(json_string)
        return data
    except json.JSONDecodeError as e:
        # Handle invalid JSON error
        app.logger.error(f"JSON decoding failed: {e}")
        return None
    except TypeError as e:
        # Handle case where input is not a string
        app.logger.error(f"Invalid input type: {e}")
        return None


extract_agent = Agent(
    model=Ollama(id=model_name, host=ollama_host),
    description="You extract information.",
)


def process_clain_data(claim: str) -> dict:
    # Run agent and return the response as a variable

    start_time = time.time()  # Record start time
    app.logger.info("Run agent ....")
    response: RunResponse = extract_agent.run(predict_nuextract(claim))
    end_time = time.time()  # Record end time
    execution_time = end_time - start_time  # Calculate elapsed time

    print(f"Execution time: {execution_time:.6f} seconds")
    app.logger.info(f"... received repsonse in {execution_time:.6f} second")

    data = json_to_dict(response.content)
    if data is not None:
        app.logger.info(f"Parsed JSON: {data}")
    else:
        app.logger.info(f"Failed to parse JSON: {data}")
    return data


def predict_nuextract(input_text):
    template = """
    {
        "Customer": {
            "Name": "",
            "Address": "",
            "Policy Number": "",
            "Telephone Number": "",
        },
        "Case": {
            "Accident Location": "",
            "Date": "",
            "Time": ""
        }
    }
    """
    template = f"""<|input|>\n ### Template:\n{template}\n### Text:\n{input_text}\n\n<|output|>"""

    return template


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

        data = process_clain_data(claim)

        # Return a success response
        response = make_response(
            {
                "time_received": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "data": data,
                "claim": claim,
            }
        )
        response.headers["Ce-Id"] = str(uuid.uuid4())
        response.headers["Ce-specversion"] = "1.0"
        response.headers["Ce-Source"] = "semantic.sonnenschirm/processor"
        response.headers["Ce-Type"] = "semantic.sonnenschirm.response"
        return response

    except Exception as e:
        app.logger.info("Error processing event:", e)
        return jsonify({"error": "Failed to process Cloud Event"}), 500


if __name__ == "__main__":
    app.logger.info(f"Start processor ... with ollama_host: {ollama_host}")
    check_model()
    app.run(debug=False, host="0.0.0.0", port=8080)
