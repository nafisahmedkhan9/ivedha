from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, BackgroundTasks
from datetime import datetime
import json
from elasticsearch import Elasticsearch

from auth import create_access_token
from background_jobs import run_csv_filter_job
from dependencies import get_es_client
from middleware import HomeJWTMiddleware

app = FastAPI()
app.add_middleware(HomeJWTMiddleware)

INDEX_NAME = "service-health"
EXPECTED_SERVICES = ["httpd", "rabbitmq", "postgresql"]
VALID_STATUSES = {"UP", "DOWN"}


@app.get("/")
def home():
    return {
        "message": "RBCAPP1 Monitoring API Running"
    }


@app.post("/token")
def get_token(username: str):
    token = create_access_token({"sub": username})
    return {"access_token": token, "token_type": "bearer"}


@app.post("/add")
async def add_data(
    file: UploadFile = File(...),
    es: Elasticsearch = Depends(get_es_client),
):
    content = await file.read()
    try:
        payload = json.loads(content)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON file") from exc

    required_fields = {"service_name", "service_status", "host_name"}
    if not required_fields.issubset(payload.keys()):
        raise HTTPException(
            status_code=400,
            detail="Payload must contain service_name, service_status, host_name",
        )

    payload["service_name"] = str(payload["service_name"]).lower()
    payload["service_status"] = str(payload["service_status"]).upper()
    if payload["service_status"] not in VALID_STATUSES:
        raise HTTPException(
            status_code=400,
            detail="service_status must be one of: UP, DOWN",
        )
    payload["@timestamp"] = datetime.utcnow().isoformat()

    response = es.index(
        index=INDEX_NAME,
        document=payload
    )

    return {
        "message": "File uploaded successfully",
        "id": response["_id"]
    }


@app.get("/healthcheck")
def healthcheck(es: Elasticsearch = Depends(get_es_client)):
    response = es.search(
        index=INDEX_NAME,
        query={"match_all": {}},
        sort=[{"@timestamp": {"order": "desc"}}],
        size=200
    )

    latest_status_by_service = {}
    overall_status = "UP"

    for hit in response["hits"]["hits"]:
        data = hit["_source"]
        service_name = data.get("service_name", "").lower()
        if service_name and service_name not in latest_status_by_service:
            latest_status_by_service[service_name] = data.get("service_status", "DOWN").upper()

    services = []
    down_services = []
    for service_name in EXPECTED_SERVICES:
        status = latest_status_by_service.get(service_name, "DOWN")
        if status not in VALID_STATUSES:
            status = "DOWN"
        services.append({"service_name": service_name, "service_status": status})
        if status == "DOWN":
            down_services.append(service_name)
            overall_status = "DOWN"

    return {
        "application_name": "rbcapp1",
        "application_status": overall_status,
        "services": services,
        "down_services": down_services
    }


@app.get("/healthcheck/{service_name}")
def service_health(service_name: str, es: Elasticsearch = Depends(get_es_client)):
    response = es.search(
        index=INDEX_NAME,
        query={
            "match": {
                "service_name": service_name.lower()
            }
        },
        sort=[{"@timestamp": {"order": "desc"}}],
        size=1
    )

    hits = response["hits"]["hits"]

    if not hits:
        raise HTTPException(status_code=404, detail="Service not found")

    source = hits[0]["_source"]
    status = source.get("service_status", "DOWN").upper()
    if status not in VALID_STATUSES:
        status = "DOWN"
    return {
        "application_name": "rbcapp1",
        "service_name": source.get("service_name", service_name.lower()),
        "application_status": status
    }


@app.post("/csv-filter/run")
def run_csv_filter(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_csv_filter_job)
    return {"message": "CSV filter job started in background"}

@app.get("/welcome")
def welcome(name: str):
    return {
        "message": f"Welcome to the RBCAPP1 Monitoring API {name}"
    }