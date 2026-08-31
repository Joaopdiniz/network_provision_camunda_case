# Camunda 8 Technical Case

## About the project

This project was created as a technical exercise using Camunda 8 and Python.

The idea is to simulate a simple telecom service provisioning process.

The process receives information about a customer request, sends the task to a Python worker, and then decides what should happen depending on the result.

The project runs locally using Camunda 8 Run.

\---

## Technologies used

* Camunda 8 Run
* BPMN
* Python
* Camunda Python SDK
* Java 21

## Requirements

- Camunda 8 Run 8.9.12
- Python 3.13.11
- Java 21
- Camunda Orchestration Python SDK 9.0.1

\---

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
Camunda 8 Run, Java, the Python virtual environment and the offline
wheelhouse are local runtime dependencies and are not included in
the repository.
### Main files

* `telecom-service-provisioning.bpmn`  
Contains the BPMN process.
* `worker.py`  
Contains the Python worker that processes the provisioning task.
* `deploy.py`  
Deploys the BPMN process to Camunda.
* `start\_process.py`  
Starts process instances using different test scenarios.

\---

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
      /     \\
    Yes      No
     |        |
     v        v
Activation   Capacity Planning
     |
     v
Service Activated
```

There is also an error path for invalid input.

For example, if the requested bandwidth is negative, the worker returns a BPMN error called:

```text
INVALID\_CONFIG
```

The process catches this error and finishes in the `Invalid Request` path.

\---

## Python worker

The Python worker listens for jobs with the type:

```text
provision-telecom-service
```

The worker receives the variables from Camunda and executes the provisioning logic.

The main input variables are:

* `customer\_name`
* `service\_type`
* `bandwidth\_mbps`

For this demo, the available network capacity is simulated as:

```text
1000 Mbps
```

If the requested bandwidth is lower than or equal to the available capacity, the service can be provisioned.

If it is higher, the process goes to the Capacity Planning path.

The worker is configured to handle up to 5 jobs at the same time.

\---

## Test scenarios

Four scenarios were created to test the process.

### Success

```powershell
python .\\start\_process.py success
```

Example:

```text
Requested bandwidth: 500 Mbps
Available capacity: 1000 Mbps
```

Expected result:

```text
Service Activated
```

\---

### Insufficient capacity

```powershell
python .\\start\_process.py capacity
```

Example:

```text
Requested bandwidth: 1500 Mbps
Available capacity: 1000 Mbps
```

Expected result:

```text
Capacity Planning
```

\---

### Invalid request

```powershell
python .\\start\_process.py invalid
```

This scenario sends an invalid bandwidth value.

The worker throws the BPMN error:

```text
INVALID\_CONFIG
```

Expected result:

```text
Invalid Request
```

\---

### Technical failure

```powershell
python .\\start\_process.py technical
```

This scenario simulates a technical problem, such as a timeout when calling another system.

The job is retried by Camunda.

A small retry delay is used between attempts.

If all retries fail, Camunda creates an incident that can be checked in Operate.

\---

## How to run

### 1\. Start Camunda

```powershell
cd C:\\camunda\_case\\camunda\\c8run-8.9.12
.\\c8run.exe start
```

Camunda Operate:

```text
http://localhost:8080/operate
```

Login:

```text
User: demo
Password: demo
```

\---

### 2\. Activate the Python environment

```powershell
cd C:\\camunda\_case
.\\.venv\\Scripts\\Activate.ps1
```

\---

### 3\. Deploy the BPMN process

```powershell
python .\\deploy.py
```

\---

### 4\. Start the worker

```powershell
python .\\worker\\worker.py
```

The worker should display:

```text
Telecom provisioning worker connected.
Listening for job type: provision-telecom-service
```

Keep this terminal open.

\---

### 5\. Start a test process

Open another PowerShell window and run, for example:

```powershell
python .\\start\_process.py success
```

The process instance can then be checked in Camunda Operate.

\---

## Error handling

I separated the errors into two main cases.

### Business error

Used when the request itself is invalid.

Example:

```text
bandwidth\_mbps = -10
```

The worker throws `INVALID\_CONFIG`, and the BPMN process handles the error.

### Technical failure

Used when something external could temporarily fail.

Example:

```text
Network controller timeout
```

In this case, Camunda retries the job.

If the retries are exhausted, an incident is created.

\---

## Notes

This is a simplified project created for demonstration purposes.

The network capacity and subnet allocation are simulated inside the Python worker.

In a real environment, the worker would probably communicate with external systems such as:

* Network inventory APIs
* Network controllers
* Databases
* Other internal services

The main goal of this project is to demonstrate the integration between a BPMN process in Camunda and a Python worker.

