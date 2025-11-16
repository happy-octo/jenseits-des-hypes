import os
import time
import requests

# Environment variable for model name
MODEL_NAME = os.getenv("MODEL_NAME", "sroecker/nuextract-tiny-v1.5:latest")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")


# Constants
CHECK_INTERVAL = 10  # seconds
TIMEOUT_DURATION = 5 * 60  # 60  # 5 minutes in seconds


def main():
    start_time = time.time()

    while True:
        if time.time() - start_time >= TIMEOUT_DURATION:
            print("Timeout reached. Exiting.")
            exit(1)

        try:
            # Perform HTTP GET
            URL = OLLAMA_HOST + "/api/tags"
            response = requests.get(URL)
            print(f"GET {URL} - Status Code: {response.status_code}")

            if response.status_code != 200:
                print("HTTP Service not availve (yet)")

            else:
                # Parse the JSON response
                try:
                    data = response.json()
                except ValueError:
                    print("Invalid JSON received.")

                # Check the "models" list
                models = data.get("models", [])

                model_deployed = False
                for model in models:
                    if model.get("model") == MODEL_NAME:
                        print(f"Model '{MODEL_NAME}' found in response.")
                        return

                if not model_deployed:
                    print(f"Model '{MODEL_NAME}' not found in response. Try to pull ..")
                    post_payload = {"name": MODEL_NAME}
                    headers = {"Content-Type": "application/json"}
                    POST_URL = OLLAMA_HOST + "/api/pull"
                    post_response = requests.post(
                        POST_URL, json=post_payload, headers=headers
                    )
                    print(f"POST {POST_URL} - Status Code: {post_response.status_code}")

                    if post_response.status_code == 200:
                        print("Model pulled successfully.")
                        return
                    else:
                        print(
                            f"Model pull failed. Status Code: {post_response.status_code}"
                        )

        except requests.RequestException as e:
            print(f"HTTP request failed: {e}")

        # Wait before the next check
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
