# Jenseits des Hypes - Hands-on Lab


## Navigate your environment

- You should have your unique user (e.g. `user29`)
- The following instructions is using `userXX`
- The password is `*****` (see Slide)
- Login to OpenShift. https://red.ht/jenseits-des-hypes
- You have a project `userXX-sonnenschirm`
- Navigate to OpenShift AI via the 9-dot menu.

## Deploy a ollama serving runtime

Your OpenShift project `userXX-sonnenschirm` is also a OpenShift AI Data Science Project.

### Create a data connection
- Within your project, navigate to `Connections`
- Then, `Create Connection`
- Select `S3 compatible object storage - v1`
- Enter:
  - `Connection name: ollama`
  - `Access key: minio`
  - `Secret key: *****` (See Slide)
  - `Endpoint: http://minio.minio.svc.cluster.local:9000`
  - `Region: EMEA`
  - `Bucket: models-ollama`
- Hit `Create`


### Deploy ollama

- Within your project, navigate to `Models`
- Hit `Deploy Model` (We are not deploying a model here, just ollama)
- Enter:
  - `Model deployment name: semantic-sonnenschirm`
  - `Serving runtime: Ollama`
  - `Model framework: Ollama`
  - `Number of model server replicas to deploy: 1`
  - `Model server size: Small`
  - `Accelerator: No`
  - `Token authentication: no`
  - `Require token authentication: no`
  - `Existing connection: ollama`
  - `Path: ollama`
- Hit `Deploy`

- Optionally, navigate back to the OpenShift Console and watch the pods
- After some time, you see in `Models and model servers` the status switched to `Started`

### Inspect your ollama runtime
- Navigate  to the OpenShift Console
- Find your `ollama-predictor` pod
- Hit `Terminal`
- Enter `ollama list`
```
ollama list
NAME    ID      SIZE    MODIFIED
```
- No error and no models, that is okay

## Let's go to the Workbench
### Create a Workbench
- Back to OpenShift AI
- Within your Data Science Project `userXX-sonnenschirm`, navigate to `Workbenches`
- Hit `Create Workbench`
- Enter:
  - `Name: <whatever-you-want>`
  - `Description: <write-a-poem-about-your-favorite-pet>`
  - `Workbench image: Jupyter | Minimal | CPU | Python 3.12`
  - `Version selection: 2025.2`
  -  `Container size: Small`
  - `Accelerator: No   `
  - `Environment variables: None`
  - `Cluster storage` keep suggested default values
- Hit `Create Workbench`
- Wait until the workbench started
- Open the workbench

### Explore Structured information extraction with a specialized small LLM
- You opened the workbench, now you are in a JupyterLab environment.
- Clone the github repo https://github.com/happy-octo/jenseits-des-hypes.git
   - There are many ways to clone repos. Find your choice.
 - Navigate and open `sonnenschrim/notesbooks/01_structured_extraction`
 - Walk through the notebook and have fun
   - Hint: Updated `OLLAMA_HOST=` ... check your in OpenShift Networking/Services for your `semantic-sonnenschirm-predictor`

---
### Did it work for you?
> Please share your experience and feedback

## ⚙️ Optional Lab: Deploy the Runtime Application

This lab guides you through deploying the `semantic-sonnenschirm` application using Helm and verifying its status on OpenShift.

-----

### 1\. Verify Current Project (Namespace)

Before deployment, ensure you are in the correct namespace for your lab environment. Replace `userXX-sonnenschirm` with your assigned project name.

```bash
oc project userXX-sonnenschirm
```

-----

### 2\. Deploy the Application with Helm

Use **Helm** to install the application's resources (backend, sender, and processor Pods) defined in the local chart.

This command installs a new **release** named `semantic-sonnenschirm` from the local chart directory `helm/semantic-sonnenschirm`, applying a label that identifies all created resources as part of `test-app`.

| Component | Description |
| :--- | :--- |
| `semantic-sonnenschirm` | The **name** of the Helm release. |
| `helm/semantic-sonnenschirm` | The path to the local **Helm chart**. |
| `--labels ...` | Adds custom Kubernetes labels to all deployed resources for grouping/tracking. |

```bash
helm install semantic-sonnenschirm helm/semantic-sonnenschirm --labels app.kubernetes.io/part-of=test-app
```

**Expected Output:**

```bash
NAME: semantic-sonnenschirm
LAST DEPLOYED: Sun Nov 16 19:43:47 2025
NAMESPACE: userXX-sonnenschirm
STATUS: deployed
REVISION: 1
TEST SUITE: None
```

-----

### 3\. Verify Pod Status

Confirm that the application's components—the **backend**, **processor**, and **sender** Pods—are running successfully.

```bash
oc get pods
```

**Expected Output (all Pods should show `1/1` in `READY` and `Running` in `STATUS`):**

```bash
NAME                                               READY   STATUS    RESTARTS   AGE
semantic-sonnenschirm-backend-578f968787-5fzrw     1/1     Running   0          3m15s
semantic-sonnenschirm-processor-754dfcfb69-bkp99   1/1     Running   0          3m15s
semantic-sonnenschirm-sender-6c5f875ccc-2sjsl      1/1     Running   0          3m15s
```

-----

### 4\. Retrieve Application URL

The **backend** component is exposed externally via an OpenShift **Route**. Use `jsonpath` to extract just the hostname (URL) for the backend service.

```bash
oc get route semantic-sonnenschirm-backend --output=jsonpath='{.spec.host}'
```