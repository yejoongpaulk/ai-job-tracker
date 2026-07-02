import enum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text, ForeignKey, Enum
from ..database import Base


class JobStatus(str, enum.Enum):
    WISHLIST = "Wishlist" # to-do (not submitted)
    APPLIED = "Applied" # applied
    INTERVIEWING = "Interviewing" # in the process of interviews
    OFFER = "Offer" # received an offer
    REJECTED = "Rejected" # self-explanatory
    GHOSTED = "Ghosted" # no response despite follow ups


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Defaults to WISHLIST so newly saved postings start as a to-do item
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus, name="job_status_enum", create_type=True), 
        default=JobStatus.WISHLIST,
        nullable=False
    )
    
    raw_job_posting: Mapped[str] = mapped_column(Text, nullable=False)
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
