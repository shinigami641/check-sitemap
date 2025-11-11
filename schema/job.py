from sqlalchemy import Column, Integer, String
from config.mysql import Base
from sqlalchemy import DateTime
from datetime import datetime

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    job_id = Column(String(150), unique=True, index=True)
    domain = Column(String(150), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="pending")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    finish_at = Column(DateTime, default=None, onupdate=None)
    
    def __repr__(self):
        return f"Job(id={self.id}, job_id={self.job_id}, domain={self.domain}, created_at={self.created_at}, updated_at={self.updated_at}, finish_at={self.finish_at})"
