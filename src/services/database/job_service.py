from sqlalchemy.orm import Session, joinedload
from models.batch import Batch
from models.job import Job
from shared.batch_status import BatchStatus
from shared.job_status import JobStatus

def create_job(db: Session, webhook_url: str, source_filename: str):
    job = Job(webhook_url=webhook_url, source_filename=source_filename)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

def get_job(db: Session, job_id: str):
    return db.query(Job).filter(Job.id == job_id).first()

def update_job_with_batch(db: Session, job_id: int, batch_status: str):
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if batch_status == BatchStatus.COMPLETED or batch_status == BatchStatus.FAILED:
        job.batches_processed += 1
    
    if batch_status == BatchStatus.COMPLETED:
            job.batches_succeeded += 1

    if job.batches_processed == job.total_batches:
        if job.batches_succeeded == job.total_batches:
            job.job_status = JobStatus.COMPLETED
        elif job.batches_succeeded > 0:
            job.job_status = JobStatus.PARTIALLY_COMPLETED
        else:
            job.job_status = JobStatus.FAILED

    db.commit()
    db.refresh(job)
    return job

def update_job_total_batches(db: Session, job_id: int, total_batches: int):
    job = db.query(Job).filter(Job.id == job_id).first()
    if job:
        job.total_batches = total_batches
        db.commit()
        db.refresh(job)
        return job
    return None

def update_job_status(db: Session, job_id: int, job_status: JobStatus):
    job = db.query(Job).filter(Job.id == job_id).first()
    if job:
        job.job_status = job_status
        db.commit()
        db.refresh(job)
        return job
    return None

def get_job_with_vdb_metadata(db: Session, job_id: int):
    return db.query(Job).filter(Job.id == job_id).options(
        joinedload(Job.vector_db_metadata)
    ).first()

def create_job_with_vdb_metadata(db: Session, vectorflow_request, source_filename: str):
    job = Job(webhook_url=vectorflow_request.webhook_url if vectorflow_request.webhook_url else None, 
              source_filename=source_filename,  
              vector_db_metadata=vectorflow_request.vector_db_metadata)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job