podman build -t processor:latest -f Containerfile . 
podman tag processor:latest quay.io/semantic-sonnenschirm/processor:latest
podman push quay.io/semantic-sonnenschirm/processor:latest
