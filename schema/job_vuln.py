from sqlalchemy import Column, Integer, String, DateTime, Text  # type: ignore
from config.mysql import Base
from datetime import datetime

class JobVuln(Base):
    __tablename__ = "jobs_vuln"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    job_id = Column(String(150), index=True)
    url = Column(String(255), nullable=False, index=True)  # target action URL
    source_page = Column(String(255), nullable=True)       # page where form found
    method = Column(String(10), nullable=True)             # GET/POST
    field = Column(String(150), nullable=True)             # field name
    payload = Column(Text, nullable=True)
    evidence = Column(Text, nullable=True)
    vuln_type = Column(String(50), default="sqli", index=True)
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return (
            f"JobVuln(id={self.id}, job_id={self.job_id}, url={self.url}, "
            f"source_page={self.source_page}, method={self.method}, field={self.field}, "
            f"payload={self.payload}, evidence={self.evidence}, vuln_type={self.vuln_type}, "
            f"created_at={self.created_at})"
        )