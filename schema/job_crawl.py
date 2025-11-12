from sqlalchemy import Column, Integer, String
from config.mysql import Base
from sqlalchemy import DateTime
from datetime import datetime

class JobCrawl(Base):
    __tablename__ = "jobs_crawl"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    job_id = Column(String(150), index=True)
    url = Column(String(150), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"JobCrawl(id={self.id}, job_id={self.job_id}, url={self.url}, created_at={self.created_at})"
