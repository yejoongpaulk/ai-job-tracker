# job_app/schemas/job.py
from pydantic import BaseModel, Field, ConfigDict  # 🔒 Import ConfigDict
from typing import Optional
from ..models.jobs import JobStatus

class JobCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    company_name: str = Field(..., min_length=1, max_length=255)
    raw_job_posting: str = Field(..., min_length=1)
    status: JobStatus = Field(default=JobStatus.WISHLIST)

class JobExtractionResponse(BaseModel):
    title: str = Field(..., description="Extracted official job title")
    company_name: str = Field(..., description="Extracted clean company name")

class JobResponse(BaseModel):
    id: int
    title: str
    company_name: str
    status: JobStatus
    raw_job_posting: str

    # 🚀 Replace class Config with modern v2 model_config dictionary mapping!
    model_config = ConfigDict(from_attributes=True)

    ai_summary: Optional[str] = None


class JobStatusUpdate(BaseModel):
    """
    Used when changing the status of a job cell (e.g., changing from Applied to Interviewing).
    """
    status: JobStatus