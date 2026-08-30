from pathlib import Path

from camunda_orchestration_sdk import CamundaClient


BPMN_FILE = Path(__file__).resolve().parent / "bpmn" / "telecom-service-provisioning.bpmn"


def main() -> None:
    with CamundaClient() as client:
        result = client.deploy_resources_from_files([str(BPMN_FILE)])

    print(f"Deployment key: {result.deployment_key}")
    for process in result.processes:
        print(
            f"Process deployed: id={process.process_definition_id}, "
            f"key={process.process_definition_key}"
        )


if __name__ == "__main__":
    main()
