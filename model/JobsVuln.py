from typing import Optional, List
from config.mysql import SessionLocal, engine
from schema.job_vuln import JobVuln

# Ensure table exists
JobVuln.metadata.create_all(bind=engine)

def create_job_vuln(
    job_id: str,
    url: str,
    source_page: Optional[str] = None,
    method: Optional[str] = None,
    field: Optional[str] = None,
    payload: Optional[str] = None,
    evidence: Optional[str] = None,
    vuln_type: str = "sqli",
) -> JobVuln:
    db = SessionLocal()
    try:
        item = JobVuln(
            job_id=job_id,
            url=url,
            source_page=source_page,
            method=method,
            field=field,
            payload=payload,
            evidence=evidence,
            vuln_type=vuln_type,
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return item
    finally:
        db.close()

def get_all_job_vuln(job_id: str) -> List[JobVuln]:
    db = SessionLocal()
    try:
        items = db.query(JobVuln).filter(JobVuln.job_id == job_id).all()
        return items
    finally:
        db.close()