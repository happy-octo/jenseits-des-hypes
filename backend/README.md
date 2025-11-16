
# Build and push the backend image
```
podman build -t backend:latest -f Containerfile .
podman tag backend:latest quay.io/semantic-sonnenschirm/backend:latest
podman push quay.io/semantic-sonnenschirm/backend:latest
```

# Run the backend locally
```
podman run -it --rm --name backend -p 8080:8080 backend:latest
```

# Local testing

```
python backend.py
```

```
curl  http://127.0.0.1:8080 -X POST -H "Content-Type: application/json" -H "Ce-specversion: 1.0"  \
      -d '{"specversion": "1.0", "id": "007", "type": "semantic.sonnenschirm.response", "source": "semantic.sonnenschirm/processor",
      "data": {  "time_received": "2024-11-17 12:34:56",  "claim": "This is a test claim", "data": [{"data": "hi"} ] }} '
```

```
curl  http://127.0.0.1:8080 -X POST -H "Content-Type: application/json" -H "Ce-specversion: 1.0"  \
      -d '{"specversion": "1.0", "id": "007", "type": "semantic.sonnenschirm.response", "source": "semantic.sonnenschirm/processor",
      "data": {  "time_received": "2024-11-17 12:34:56",  "claim": "This is a test claim", "data": {"Customer": {"Name": "Emily Patel", "Address": "456 Maple Street", "Policy Number": "EV-901234567", "Telephone Number": "(555) 901-2345"}, "Case": {"Accident Location": "Oakdale, CA 95361", "Date": "January 15th, 2024", "Time": "9:45 AM"}} }} '
```
