from datetime import datetime
from config.mysql import SessionLocal, engine
from schema.job_crawl import JobCrawl

JobCrawl.metadata.create_all(bind=engine)

def create_job_crawl(job_id: str, url: str):
    db = SessionLocal()
    jobCrawl = JobCrawl(job_id=job_id, url=url)
    db.add(jobCrawl)
    db.commit()
    db.refresh(jobCrawl)
    return jobCrawl

def get_all_job_crawl(job_id: str):
    db = SessionLocal()
    jobsCrawl = db.query(JobCrawl).filter(JobCrawl.job_id == job_id).all()
    return jobsCrawl