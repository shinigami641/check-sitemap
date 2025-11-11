from datetime import datetime
from config.mysql import SessionLocal, engine
from schema.job import Job

Job.metadata.create_all(bind=engine)

def create_job(job_id: str, domain: str):
    db = SessionLocal()
    job = Job(job_id=job_id, domain=domain, status="pending")
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

def get_all_job(status: str):
    db = SessionLocal()
    jobs = db.query(Job)
    if status != "":
        jobs = jobs.filter(Job.status == status)
    jobs = jobs.all()
    return jobs

def get_job(job_id: str):
    db = SessionLocal()
    job = db.query(Job).filter(Job.job_id == job_id).first()
    return job

def update_job(job_id: str, status: str):
    db = SessionLocal()
    job = db.query(Job).filter(Job.job_id == job_id).first()
    if job is None:
        return None
    job.status = status
    if status == "finish":
        job.finish_at = datetime.now()  
    db.commit()
    db.refresh(job)
    return job