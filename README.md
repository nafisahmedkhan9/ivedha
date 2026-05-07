# rbcapp1 Assignment Solution

This repository contains implementations for TEST1, TEST2, and TEST3 of the monitoring assignment.

## Installation and setup

### 1) Create and activate virtual environment

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

Windows (PowerShell):

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2) Install Python dependencies

```bash
pip install fastapi uvicorn elasticsearch pandas python-multipart
```

### 3) Setup Elasticsearch locally

If you already extracted Elasticsearch in project root (for example `elasticsearch-8.13.0`), start it:

Linux/macOS:

```bash
./elasticsearch-8.13.0/bin/elasticsearch
```

Windows (PowerShell):

```powershell
.\elasticsearch-8.13.0\bin\elasticsearch.bat
```

Keep Elasticsearch running and verify:

```bash
curl http://127.0.0.1:9200
```

The API in `app.py` expects Elasticsearch at `http://localhost:9200`.

## Prerequisites

- Linux host(s) for service monitoring (systemd services)
- Python 3.10+
- Elasticsearch running on `http://localhost:9200`
- Ansible (for TEST2)
- SMTP relay reachable from Ansible control node (for disk alert email in TEST2)

Install Python dependencies using the setup section above.

## TEST1

### 1) Service monitor script

File: `monitor.py`

What it does:
- Checks status of:
  - `httpd`
  - `rabbitmq-server`
  - `postgresql`
- Builds JSON payload for each service:
  - `service_name`
  - `service_status` (`UP`/`DOWN`)
  - `host_name`
- Writes one file per service to `report_files/` using:
  - `{serviceName}-status-{@timestamp}.json`

Run:

```bash
python monitor.py
```

### 2) REST API + Elasticsearch

File: `app.py`

Endpoints:
- `POST /add`
  - Upload a generated JSON file and store in Elasticsearch
- `GET /healthcheck`
  - Returns `application_name`, overall `application_status`, per-service list, and `down_services`
- `GET /healthcheck/{serviceName}`
  - Returns status for the requested service as application status (`UP`/`DOWN`)

Run API:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Example calls:

```bash
curl -F "file=@report_files/httpd-status-20260507040524.json" http://127.0.0.1:8000/add
curl http://127.0.0.1:8000/healthcheck
curl http://127.0.0.1:8000/healthcheck/httpd
```

## TEST2

Files:
- `ansible-test2/inventory.ini`
- `ansible-test2/assignment.yml`

### Inventory

Defines:
- `host1` (httpd)
- `host2` (rabbitmq)
- `host3` (postgresql)

Update host IPs/user/key path in `inventory.ini` as needed before running.

### Playbook actions

Run from `ansible-test2/`:

```bash
ansible-playbook assignment.yml -i inventory.ini -e action=verify_install
ansible-playbook assignment.yml -i inventory.ini -e action=check-disk
ansible-playbook assignment.yml -i inventory.ini -e action=check-status
```

Behavior:
- `action=verify_install`
  - Verifies/installs one sample service (`httpd`) on `host1` using RHEL package manager (`dnf`)
- `action=check-disk`
  - Checks root disk usage on all servers
  - If usage is `>80%`, sends alert email to configured address
- `action=check-status`
  - Calls TEST1 API `/healthcheck`
  - Prints overall app status and list of down services

## TEST3

File: `csv_filter.py`

What it does:
- Reads `sales-data.csv`
- Calculates `price_per_sqft = price / sq__ft`
- Computes average `price_per_sqft`
- Outputs only rows below average to `filtered_sales.csv`

Run:

```bash
python csv_filter.py
```

## Notes

- For TEST3, ensure input filename is exactly `sales-data.csv` in project root.
- For TEST2 disk email alerts, configure SMTP relay if `localhost:25` is not available.

## SMTP configuration (production note)

To send alert emails through SMTP (instead of local `localhost:25`), configure the Ansible `mail` task with your SMTP server details.

Example (Gmail SMTP):

```yaml
mail:
  host: smtp.gmail.com
  port: 587
  username: "{{ smtp_username }}"
  password: "{{ smtp_password }}"
  to: "{{ alert_email_to }}"
  subject: "RBCAPP1 disk alert on {{ inventory_hostname }}"
  body: "Disk usage is {{ disk_usage.stdout }}% on {{ inventory_hostname }} (threshold: 80%)."
  secure: starttls
```

Security recommendations:
- Use app passwords for Gmail (not account password).
- Store `smtp_username`/`smtp_password` in Ansible Vault or environment variables.
- Do not hardcode credentials in playbooks or commit them to Git.
