import argparse
import sys

import httpx


BASE_URL = "http://localhost:8080/v2"
PROCESS_ID = "telecom-service-provisioning"


SCENARIOS: dict[str, dict[str, object]] = {
    "success": {
        "customer_name": "Contoso Telecom",
        "service_type": "5G_SLICE",
        "bandwidth_mbps": 500,
    },
    "capacity": {
        "customer_name": "Contoso Telecom",
        "service_type": "5G_SLICE",
        "bandwidth_mbps": 1500,
    },
    "invalid": {
        "customer_name": "Contoso Telecom",
        "service_type": "5G_SLICE",
        "bandwidth_mbps": -10,
    },
    "technical": {
        "customer_name": "Contoso Telecom",
        "service_type": "5G_SLICE",
        "bandwidth_mbps": 500,
        "simulate_technical_failure": True,
    },
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Start a Camunda demo process instance.")
    parser.add_argument(
        "scenario",
        choices=SCENARIOS,
        help="Demo scenario to start.",
    )
    args = parser.parse_args()

    payload = {
        "processDefinitionId": PROCESS_ID,
        "processDefinitionVersion": -1,
        "variables": SCENARIOS[args.scenario],
    }

    try:
        response = httpx.post(
            f"{BASE_URL}/process-instances",
            json=payload,
            timeout=10.0,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        print(f"Could not start process: {exc}", file=sys.stderr)
        if getattr(exc, "response", None) is not None:
            print(exc.response.text, file=sys.stderr)
        raise SystemExit(1) from exc

    data = response.json()
    print(f"Scenario: {args.scenario}")
    print(f"Process instance key: {data['processInstanceKey']}")
    print(f"Variables sent: {SCENARIOS[args.scenario]}")


if __name__ == "__main__":
    main()
