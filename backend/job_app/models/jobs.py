import enum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text, ForeignKey, Enum
from ..database import Base


class JobStatus(str, enum.Enum):
    WISHLIST = "Wishlist"        # <-- Job saved as a to-do, application not yet submitted
    APPLIED = "Applied"
    INTERVIEWING = "Interviewing"
    OFFER = "Offer"
    REJECTED = "Rejected"
    GHOSTED = "Ghosted"


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
