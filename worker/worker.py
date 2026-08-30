import asyncio

from camunda_orchestration_sdk import (
    CamundaAsyncClient,
    JobError,
    JobFailure,
    WorkerConfig,
)

AVAILABLE_CAPACITY_MBPS = 1000
ALLOCATED_SUBNET = "10.10.10.0/24"
ALLOWED_SERVICE_TYPES = ["5G_SLICE", "MPLS", "SD_WAN"]


async def provision_service(job):
    variables = job.variables.to_dict()

    customer_name = variables.get("customer_name", "")
    service_type = variables.get("service_type", "")
    bandwidth = variables.get("bandwidth_mbps")
    simulate_technical_failure = variables.get(
        "simulate_technical_failure", False
    )

    print(
        f"Provisioning request received - "
        f"Customer: {customer_name}, "
        f"Service: {service_type}, "
        f"Bandwidth: {bandwidth} Mbps"
    )

    # Validations
    if not customer_name:
        raise JobError(
            error_code="INVALID_CONFIG",
            message="Customer name is required",
        )

    if service_type not in ALLOWED_SERVICE_TYPES:
        raise JobError(
            error_code="INVALID_CONFIG",
            message="Invalid service type",
        )

    if bandwidth is None or bandwidth <= 0:
        raise JobError(
            error_code="INVALID_CONFIG",
            message="Bandwidth must be greater than zero",
        )

    # Technical problem with an external system
    # Camunda will handle the retries and backoff
    if simulate_technical_failure:
        raise JobFailure(
            message="Simulated network controller timeout",
            retries=None,
            retry_back_off=3000,
        )

    # Simulates waiting for an external component
    await asyncio.sleep(0.5)

    if bandwidth <= AVAILABLE_CAPACITY_MBPS:
        print("Provisioning completed successfully")

        return {
            "provisioned": True,
            "available_capacity_mbps": AVAILABLE_CAPACITY_MBPS,
            "allocated_subnet": ALLOCATED_SUBNET,
            "status_message": "Network service provisioned successfully",
        }

    print("Provisioning rejected due to insufficient capacity")

    return {
        "provisioned": False,
        "available_capacity_mbps": AVAILABLE_CAPACITY_MBPS,
        "allocated_subnet": None,
        "status_message": "Insufficient network capacity",
    }


async def main():
    async with CamundaAsyncClient() as client:
        worker_config = WorkerConfig(
            job_type="provision-telecom-service",
            job_timeout_milliseconds=30000,
            max_concurrent_jobs=5,
            worker_name="telecom-provisioning-python-worker",
        )

        client.create_job_worker(
            config=worker_config,
            callback=provision_service,
        )

        print("Telecom provisioning worker connected.")
        print("Listening for job type: provision-telecom-service")
        print("Press Ctrl+C to stop.")

        await client.run_workers()


if __name__ == "__main__":
    asyncio.run(main())
