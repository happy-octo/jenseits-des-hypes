podman build -t backend:latest -f Containerfile . 
podman tag backend:latest quay.io/semantic-sonnenschirm/backend:latest
podman push quay.io/semantic-sonnenschirm/backend:latest
