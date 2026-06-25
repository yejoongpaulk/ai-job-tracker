# job_app/routers/jobs.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..database import get_db
from ..models.jobs import Job
from ..dependency import get_current_user
from ..schemas.auth import SessionData
from ..schemas.job import JobCreate, JobStatusUpdate, JobResponse

router = APIRouter(prefix="/jobs", tags=["Jobs Tracker"])

# 1. GET ALL JOBS (Fetch everything for the user's grid)
@router.get("/", response_model=list[JobResponse])
async def get_my_jobs(
    db: AsyncSession = Depends(get_db),
    current_user: SessionData = Depends(get_current_user)
):
    """
    Fetches all tracking rows belonging strictly to the authenticated user.
    """
    query = select(Job).where(Job.user_id == current_user.user_id).order_by(Job.id.desc())
    result = await db.execute(query)
    return result.scalars().all()


# 2. CREATE A JOB (Add a row manually / paste description)
@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job_row(
    job_input: JobCreate,
    db: AsyncSession = Depends(get_db),
    current_user: SessionData = Depends(get_current_user)
):
    """
    Creates a new tracking entry. (AI parsing logic can hook into this pipeline next)
    """
    new_job = Job(
        user_id=current_user.user_id,
        title=job_input.title,
        company_name=job_input.company_name,
        status=job_input.status,
        raw_job_posting=job_input.raw_job_posting
    )
    
    db.add(new_job)
    await db.commit()
    await db.refresh(new_job)
    return new_job


# 3. UPDATE JOB STATUS (Quick edit directly inside the grid cells)
@router.patch("/{job_id}/status", response_model=JobResponse)
async def update_job_status(
    job_id: int,
    status_input: JobStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: SessionData = Depends(get_current_user)
):
    """
    Updates the status field of a job, verifying ownership first.
    """
    query = select(Job).where((Job.id == job_id) & (Job.user_id == current_user.user_id))
    result = await db.execute(query)
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job entry not found or unauthorized access."
        )
        
    job.status = status_input.status
    await db.commit()
    await db.refresh(job)
    return job


# 4. DELETE A JOB (Remove a row from the tracker)
@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job_row(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SessionData = Depends(get_current_user)
):
    """
    Deletes a spreadsheet tracker row completely.
    """
    query = select(Job).where((Job.id == job_id) & (Job.user_id == current_user.user_id))
    result = await db.execute(query)
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job entry not found or unauthorized access."
        )
        
    await db.delete(job)
    await db.commit()
    return None
