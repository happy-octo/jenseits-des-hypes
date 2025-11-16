# Ollama standalone deployment


## Deployment
```
oc apply -f ollama-deployment.yaml
```
Note, there is a baremetal hack in the deployment.

Pull the model:
```
oc exec deployment/ollama  -n semantic-sonnenschirm-ollama -- ollama pull sroecker/nuextract-tiny-v1.5
oc exec deployment/ollama  -n semantic-sonnenschirm-ollama -- ollama list
```

## Test local

```
oc port-forward  service/ollama 11435:11434 -n  semantic-sonnenschirm-ollama
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

# Test Raw Mode

[Chapter 3. Serving large models | Red Hat Product Documentation](https://docs.redhat.com/en/documentation/red_hat_openshift_ai_self-managed/2-latest/html/serving_models/serving-large-models_serving-large-models#deploying-models-on-single-node-openshift-using-kserve-raw-deployment-mode_serving-large-models)


## OCP 5
### Current

default-dcs:
```
    kserve:
      devFlags: {}
      managementState: Managed
      serving:
        ingressGateway:
          certificate:
            type: SelfSigned
        managementState: Managed
        name: knative-serving
```

from:
```
 name: default-dsc

    kserve:
      devFlags: {}
      managementState: Managed
      serving:
        ingressGateway:
          certificate:
            type: SelfSigned
        managementState: Managed
        name: knative-serving
    modelmeshserving:
      devFlags: {}
      managementState: Managed
```
https://pub-cd1ebf88bf724029bc25e21c905b3db9.r2.dev/ollama/emptyfile
      devFlags: {}
      defaultDeploymentMode: RawDeployment
      managementState: Managed
      serving:
        managementState: Removed
        name: knative-serving
    modelmeshserving:
      devFlags: {}
      managementState: Removed
```

## OpenShift Local (CRC)

```
  name: default-dsci

  serviceMesh:
    auth:
      audiences:
        - 'https://kubernetes.default.svc'
    controlPlane:
      metricsCollection: Istio
      name: data-science-smcp
      namespace: istio-systemminio.minio.svc.cluster.local
    managementState: Removed   <------
```

https://pub-cd1ebf88bf724029bc25e21c905b3db9.r2.dev/ollama/emptyfile


oc patch dscinitialization default-dsci --type=merge -p '{"spec":{"serviceMesh":{"managementState":"Removed"}}}'
oc patch datasciencecluster default-dsc --type=merge -p '{"spec":{"components":{"kserve":{"defaultDeploymentMode":"RawDeployment","serving":{"managementState":"Removed"}}}}}'



spec:
  components:
    codeflare:
      managementState: Managed
    kserve:
      serving:
        ingressGateway:
          certificate:
            type: OpenshiftDefaultIngress
        managementState: Managed
        name: knative-serving
      managementState: Managedminio.minio.svc.cluster.localhttps://pub-cd1ebf88bf724029bc25e21c905b3db9.r2.dev/ollama/emptyfile
    ray:
      managementState: Managed
    kueue:
      managementState: Managed
    workbenches:
      managementState: Managed
    dashboard:
      managementState: Managed
    modelmeshserving:
      managementState: Managed
    datasciencepipelines:
      managementState: Managed
    trainingoperator:
      managementState: Removed

```


to:
```
apiVersion: datasciencecluster.opendatahub.io/v1
kind: DataScienceCluster
metadata:
  name: default-dsc
  labels:
    app.kubernetes.io/created-by: rhods-operator
    app.kubernetes.io/instance: default-dsc
    app.kubernetes.io/managed-by: kustomize
    app.kubernetes.io/name: datascienceclusterhttps://pub-cd1ebf88bf724029bc25e21c905b3db9.r2.dev/ollama/emptyfile
    app.kubernetes.io/part-of: rhods-operator
spec:
  components:
    codeflare:
      managementState: Removed   
    kserve:
      defaultDeploymentMode: RawDeployment
      managementState: Managed
      serving:
        managementState: Removed
        name: knative-serving
    trustyai:
      managementState: Removed
    ray:
      managementState: Removed
    kueue:
      managementState: Removed
    workbenches:
      managementState: Managed
    dashboard:
      managementState: Managed
    modelmeshserving:
      managementState: Removed
    datasciencepipelines:
      managementState: Managed
    trainingoperator:
      managementState: Removed
```

## OCP on AWS

```
spec:
  applicationsNamespace: redhat-ods-applications
  monitoring:
    managementState: Managed
    namespace: redhat-ods-monitoring
  serviceMesh:
    auth:
      audiences:
        - 'https://kubernetes.default.svc'
    controlPlane:
      metricsCollection: Istio
      name: data-science-smcp
      namespace: istio-system
    managementState: Removed
  trustedCABundle:
    customCABundle: ''
    managementState: Managed
```


Ollama Runtime:
https://raw.githubusercontent.com/rh-aiservices-bu/llm-on-openshift/refs/heads/main/serving-runtimes/ollama_runtime/ollama-runtime.yaml


curl -s http://ollama-predictor.01-ollama.svc.cluster.local:11434/api/tags


curl http://ollama-predictor.01-ollama.svc.cluster.local:11434 \
    -k \
    -H "Content-Type: application/json" \
    -d '{
    "model": "sroecker/nuextract-tiny-v1.5:latest"
    "prompt":"Why is the sky blue?"
    }'