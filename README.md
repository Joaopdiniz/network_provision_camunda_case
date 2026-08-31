# Camunda 8 Technical Case

## About the project

This project was created as a technical exercise using Camunda 8 and Python.

The goal is to simulate a simple telecom service provisioning process. The process receives information about a customer request, sends a service task to a Python worker, and then decides the next step based on the provisioning result.

The project was developed and tested locally using Camunda 8 Run.

---

## Technologies used

* Camunda 8
* Camunda 8 Run
* BPMN 2.0
* Python
* Camunda Orchestration Python SDK
* Java 21
* HTTPX

## Requirements

* Camunda 8 Run 8.9.12
* Python 3.13
* Java 21
* Camunda Orchestration Python SDK 9.0.1
* HTTPX 0.28.1

Java must be available and `JAVA_HOME` must be correctly configured before starting Camunda 8 Run.

---

## Project structure

```text
network_provision_camunda_case/
├── bpmn/
│   └── telecom-service-provisioning.bpmn
├── worker/
│   └── worker.py
├── deploy.py
├── start_process.py
├── requirements.txt
├── requirements-lock.txt
├── README.md
└── .gitignore
```

Camunda 8 Run, Java, the Python virtual environment and the offline wheelhouse used during development are local runtime dependencies and are not included in this repository.

### Main files

* `bpmn/telecom-service-provisioning.bpmn`
  Contains the BPMN process.

* `worker/worker.py`
  Contains the Python job worker responsible for processing the provisioning task.

* `deploy.py`
  Deploys the BPMN process to Camunda using the official Camunda Python SDK.

* `start_process.py`
  Starts process instances for the available test scenarios using the Camunda REST API.

* `requirements.txt`
  Contains the direct Python dependencies required by the project.

---

## Process flow

The process follows this basic flow:

```text
B2B Order Received
        |
        v
Provision Network Slice
        |
        v
Capacity Available?
      /       \
    Yes        No
     |          |
     v          v
Activation   Capacity Planning
     |
     v
Service Activated
```

There is also an error path for invalid input.

For example, if the requested bandwidth is invalid, the worker throws a BPMN error with the code:

```text
INVALID_CONFIG
```

The BPMN boundary error event catches this error and the process finishes in the `Invalid Request` path.

---

## Python worker

The Python worker listens for jobs with the type:

```text
provision-telecom-service
```

The worker receives process variables from Camunda and executes the provisioning logic.

The main input variables are:

* `customer_name`
* `service_type`
* `bandwidth_mbps`
* `simulate_technical_failure`

For this demo, the available network capacity is simulated as:

```text
1000 Mbps
```

If the requested bandwidth is lower than or equal to the available capacity, the service can be provisioned.

If the requested bandwidth is higher than the available capacity, the job still completes successfully, but the BPMN gateway routes the process to the `Capacity Planning` path.

The worker is configured with:

```text
max_concurrent_jobs = 5
job_timeout = 30 seconds
```

The value of 5 concurrent jobs was chosen as a conservative value for the demonstration and was not based on production load testing.

---

## API usage

The project uses both the official Camunda Python SDK and the Camunda REST API.

`deploy.py` uses the official SDK to deploy the BPMN resource.

`start_process.py` uses HTTPX to send a request directly to the local Camunda REST API:

```text
POST http://localhost:8080/v2/process-instances
```

The Python worker also uses the official Camunda SDK to activate, complete and fail jobs.

---

## Test scenarios

Four scenarios are available.

### 1. Success

```powershell
python .\start_process.py success
```

Example:

```text
Requested bandwidth: 500 Mbps
Available capacity: 1000 Mbps
```

Expected BPMN result:

```text
Service Activated
```

### 2. Insufficient capacity

```powershell
python .\start_process.py capacity
```

Example:

```text
Requested bandwidth: 1500 Mbps
Available capacity: 1000 Mbps
```

Expected worker result:

```text
Provisioning rejected due to insufficient capacity
```

Expected BPMN result:

```text
Capacity Planning
```

### 3. Invalid request

```powershell
python .\start_process.py invalid
```

This scenario sends an invalid bandwidth value.

The worker throws the BPMN error:

```text
INVALID_CONFIG
```

Expected BPMN result:

```text
Invalid Request
```

### 4. Technical failure

```powershell
python .\start_process.py technical
```

This scenario simulates a temporary technical problem, such as a timeout while communicating with an external network controller.

The worker reports a technical job failure to Camunda. The service task is configured with three retries and a short retry backoff is used between attempts.

If the retries are exhausted, Camunda creates an incident that can be inspected in Operate.

---

## How to run

### 1. Clone the repository

```powershell
git clone https://github.com/Joaopdiniz/network_provision_camunda_case.git
cd network_provision_camunda_case
```

### 2. Create the Python virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install the Python dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Start Camunda 8 Run

Download Camunda 8 Run separately and make sure Java 21 and `JAVA_HOME` are correctly configured.

From the Camunda 8 Run directory:

```powershell
.\c8run.exe start
```

The local Camunda endpoint should be available at:

```text
http://localhost:8080
```

Camunda Operate:

```text
http://localhost:8080/operate
```

Default local credentials:

```text
User: demo
Password: demo
```

The cluster can also be checked using:

```powershell
Invoke-RestMethod http://localhost:8080/v2/topology
```

### 5. Deploy the BPMN process

From the project directory:

```powershell
python .\deploy.py
```

### 6. Start the worker

```powershell
python .\worker\worker.py
```

The worker should display:

```text
Telecom provisioning worker connected.
Listening for job type: provision-telecom-service
```

Keep this terminal open.

### 7. Start a test process

Open another PowerShell window, activate the virtual environment and run one of the scenarios:

```powershell
python .\start_process.py success
```

The process instance can then be inspected in Camunda Operate.

---

## Error handling

The project separates expected business errors from temporary technical failures.

### Business error

A business error is used when the request itself is invalid and repeating the same operation would not solve the problem.

Example:

```text
bandwidth_mbps = -10
```

The worker throws the BPMN error `INVALID_CONFIG`, which is caught by the BPMN process and routed to `Invalid Request`.

### Technical failure

A technical failure represents a problem that may be temporary.

Example:

```text
Network controller timeout
```

In this case, the worker reports a job failure and Camunda handles the retry scheduling.

If the configured retries are exhausted, an incident is created and can be inspected in Camunda Operate.

---

## Development and production considerations

This is a simplified project created for demonstration purposes.

The network capacity and subnet allocation are simulated inside the Python worker. In a real environment, the worker would likely communicate with external systems such as:

* Network inventory APIs
* Network controllers
* Databases
* Internal services

For a production-oriented solution, additional considerations would include:

* External configuration instead of hardcoded environment-specific values
* Secret management
* Idempotency for external side effects
* Structured logging, metrics and monitoring
* Automated tests and CI/CD
* Containerizing the worker
* Multiple worker replicas when horizontal scaling is required

Camunda 8 Run was selected for this exercise because it provided a simple local setup that worked within the restrictions of the development environment. A container-based environment such as Docker Compose could be considered to improve reproducibility for shared development environments.

---

## Goal of the project

The main goal of this project is to demonstrate the integration between a BPMN process in Camunda 8 and a Python job worker, including process routing, business error handling, technical failures, retries and incident handling.
