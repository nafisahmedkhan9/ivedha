import json
import socket
import subprocess
from datetime import datetime
from pathlib import Path

SERVICES = {
    "httpd": "apache2",
    "rabbitmq": "rabbitmq-server",
    "postgresql": "postgresql",
}


def check_service(service: str) -> str:
    """Return UP/DOWN by checking systemd service state."""
    result = subprocess.run(
        ["systemctl", "is-active", service],
        capture_output=True,
        text=True,
        check=False,
    )
    return "UP" if result.stdout.strip() == "active" else "DOWN"


def main() -> None:
    host_name = socket.gethostname()
    data_dir = Path(__file__).resolve().parent / "report_files"
    data_dir.mkdir(exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")

    for service_name, linux_service in SERVICES.items():
        status = check_service(linux_service)
        payload = {
            "service_name": service_name,
            "service_status": status,
            "host_name": host_name,
        }

        filename = data_dir / f"{service_name}-status-{timestamp}.json"
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(payload, file, indent=4)

        print(f"{service_name}: {status} -> {filename}")


if __name__ == "__main__":
    main()