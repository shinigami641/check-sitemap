from model.JobsCrawl import create_job_crawl, get_all_job_crawl
from utils.api_response import APP_ERROR_CODES
from utils.api_response import error_response, success_response
from model.sitemap_model import SitemapScanner
from model.data_model import process_data
from model.Jobs import create_job, update_job, get_job, get_all_job
import threading
import uuid
from typing import Dict
from utils.socket_handlers import send_ws_event

def process_request(payload):
    """
    Process incoming request payload
    
    Args:
        payload (dict): The request payload
        
    Returns:
        dict: Processed response
    """
    # Validate payload
    if not payload:
        return error_response("Empty Payload", http_status=400, app_code=APP_ERROR_CODES["INVALID_INPUT"])
    
    # Process data using model
    result = process_data(payload)
    
    return result

# scan_domain function removed as per request (using Jobs model with background job API)


# -----------------------------
# Background job utilities
# -----------------------------

JobsStore: Dict[str, Dict] = {}

# Utility: safely convert datetime to ISO string
def _to_iso(dt):
    try:
        return dt.isoformat() if dt is not None else None
    except Exception:
        return None

def _run_scan_job(job_id: str, domain: str):
    """Internal worker to execute scan in a background thread and update JobsStore."""
    try:
        # Update DB status to running
        update_job(job_id, "running")
        JobsStore[job_id]["status"] = "running"
        JobsStore[job_id]["progress"] = 10

        # Callback yang dipanggil oleh SitemapScanner._log(url)
        # Signature on_output(message) -> di sini message adalah URL
        def on_output_callback(message):
            try:
                url = str(message)
                # Simpan setiap URL hasil crawling ke DB
                create_job_crawl(job_id, url)
                # Sedikit progres incremental (best effort)
                JobsStore[job_id]["progress"] = min(90, JobsStore[job_id].get("progress", 10) + 5)
            except Exception:
                # Abaikan error insert agar scanning tetap berjalan
                pass

        scanner = SitemapScanner(
            domain,
            on_output=on_output_callback,
        )
        JobsStore[job_id]["progress"] = 30

        results = scanner.run_scan()
        JobsStore[job_id]["progress"] = 90

        JobsStore[job_id]["result"] = results
        JobsStore[job_id]["status"] = "done"
        # Update DB status to finish
        update_job(job_id, "finish")
        JobsStore[job_id]["progress"] = 100
        send_ws_event(
            "scan_result",
            {
                "job_id": job_id,
                "message": "Job Id Telah selesai, dan sukses"
            }
        )
    except Exception as e:
        # Update DB status to error
        update_job(job_id, "error")
        send_ws_event(
            "scan_result",
            {
                "job_id": job_id,
                "message": "Job Id Telah selesai, dan sepertinya ada kegagalan"
            }
        )
        JobsStore[job_id]["status"] = "error"
        JobsStore[job_id]["error"] = str(e)

def start_scan_job(payload: dict):
    """Start a background scan job and return a job_id immediately."""
    if not isinstance(payload, dict) or "domain" not in payload or not payload.get("domain"):
        return error_response("Invalid input: 'domain' is required", http_status=400, app_code=APP_ERROR_CODES["INVALID_INPUT"])

    domain = payload["domain"]
    job_id = uuid.uuid4().hex
    JobsStore[job_id] = {"status": "pending", "progress": 0, "result": None}
    # Create job in DB
    create_job(job_id, domain)

    t = threading.Thread(target=_run_scan_job, args=(job_id, domain), daemon=True)
    t.start()

    # Return 202 Accepted to indicate job started
    return success_response(data={"job_id": job_id}, message="Scan started", http_status=202, meta={"status": "accepted"})

def get_scan_status(job_id: str):
    # Prefer DB status; combine with in-memory progress if exists
    job_row = get_job(job_id)
    if not job_row:
        return error_response("Job not found", http_status=404, app_code=APP_ERROR_CODES["NOT_FOUND"])
    mem = JobsStore.get(job_id, {})
    progress = mem.get("progress", 0)
    return success_response(data={"status": job_row.status, "progress": progress}, message="Scan status", http_status=200)

def get_scan_result(job_id: str):
    job_row = get_job(job_id)
    if not job_row:
        return error_response("Job not found", http_status=404, app_code=APP_ERROR_CODES["NOT_FOUND"])
    mem = JobsStore.get(job_id)
    if not mem or mem.get("status") != "done":
        return error_response("Scan not completed", http_status=409, app_code=APP_ERROR_CODES["SCAN_FAILED"])
    return success_response(data=mem["result"], message="Scan result", http_status=200)

def get_scan_all_data():
    jobs = get_all_job("")
    # Serialize SQLAlchemy model objects to plain dicts (safe for None datetimes)
    jobs_data = [{
        "id": j.id,
        "job_id": j.job_id,
        "domain": j.domain,
        "status": j.status,
        "created_at": _to_iso(j.created_at),
        "updated_at": _to_iso(j.updated_at),
        "finish_at": _to_iso(j.finish_at),
    } for j in jobs] if jobs else []
    return success_response(data=jobs_data, message="Scan all data", http_status=200, meta={"count": len(jobs_data)})

def get_scan_all_crawl(job_id: str):
    jobs = get_all_job_crawl(job_id)
    # Serialize to dicts safe for JSON
    crawls = [{
        "id": c.id,
        "job_id": c.job_id,
        "url": c.url,
        "created_at": _to_iso(c.created_at),
    } for c in jobs] if jobs else []
    # Always return 200 with possibly empty list; frontend will treat empty list as partial progress
    return success_response(data=crawls, message="Scan all crawl data", http_status=200, meta={"count": len(crawls), "job_id": job_id})