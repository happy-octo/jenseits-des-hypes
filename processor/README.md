
# Processor

## Build and push the processor image
```
podman build -t processor:latest -f Containerfile .
podman tag processor:latest quay.io/semantic-sonnenschirm/processor:latest
podman push quay.io/semantic-sonnenschirm/processor:latest
```

## Run the processor locally
```
podman run -it --rm --name processor -p 8080:8080 processor:latest
```


## Ollama Deployment
```
oc apply -f ollama-deployment.yaml
```


Pull the model:
```
oc exec deployment/ollama  -n semantic-sonnenschirm -- ollama pull sroecker/nuextract-tiny-v1.5
oc exec deployment/ollama  -n semantic-sonnenschirm -- ollama list
```


## Test local

```
oc port-forward  service/ollama 11435:11434 -n  semantic-sonnenschirm
```


```
curl -s http://localhost:11435/api/tags | jq .
{
  "models": [
    {
      "name": "sroecker/nuextract-tiny-v1.5:latest",
      "model": "sroecker/nuextract-tiny-v1.5:latest",
      "modified_at": "2024-11-23T18:02:51.350172387Z",
      "size": 994157142,
      "digest": "bc78f842b2630f720f1b0d2d15d8f466405995ab315dc34e0a7b063d8298555b",
      "details": {
        "parent_model": "",
        "format": "gguf",
        "family": "qwen2",
        "families": [
          "qwen2"
        ],
        "parameter_size": "494.03M",
        "quantization_level": "F16"
      }
    }
  ]
}
```