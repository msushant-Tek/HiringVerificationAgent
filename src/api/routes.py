from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from typing import Optional
import uuid
import uuid
from src.models.trust_score import TrustScoreReport
from src.integrations.ocr_service import OCRService
from src.core.fact_checker import FactChecker

router = APIRouter()
fact_checker = FactChecker()

# In-memory store for async jobs for demonstration purposes
# In production, this would be Redis or a database.
JOBS = {}

async def run_verification_job(job_id: str, candidate_name: str, file_content: bytes, filename: str, linkedin_url: str, github_handle: str):
    try:
        # 1. Parse Document
        JOBS[job_id]["status"] = "processing_document"
        resume_text = await OCRService.process_document(file_content, filename)
        
        # 2. Fact Check Loop
        JOBS[job_id]["status"] = "fact_checking"
        report = await fact_checker.verify_candidate(
            candidate_name=candidate_name,
            resume_text=resume_text,
            linkedin_url=linkedin_url,
            github_handle=github_handle
        )
        
        # 3. Store Result
        JOBS[job_id]["status"] = "completed"
        JOBS[job_id]["result"] = report
        
    except Exception as e:
        JOBS[job_id]["status"] = "failed"
        JOBS[job_id]["error"] = str(e)


@router.post("/verify/analyze", status_code=202)
async def analyze_candidate(
    background_tasks: BackgroundTasks,
    candidate_name: str = Form(...),
    linkedin_url: Optional[str] = Form(None),
    github_handle: Optional[str] = Form(None),
    resume: UploadFile = File(...)
):
    """
    Ingests candidate data and starts an asynchronous verification job.
    """
    file_content = await resume.read()
    
    job_id = str(uuid.uuid4())
    JOBS[job_id] = {
        "status": "pending",
        "candidate_name": candidate_name
    }
    
    background_tasks.add_task(
        run_verification_job,
        job_id,
        candidate_name,
        file_content,
        resume.filename,
        linkedin_url,
        github_handle
    )
    
    return {"job_id": job_id, "status": "Job initiated"}


@router.get("/verify/report/{job_id}", response_model=None)
async def get_report(job_id: str):
    """
    Retrieves the parsed Trust Score Report for a completed job.
    """
    if job_id not in JOBS:
        raise HTTPException(status_code=404, detail="Job not found")
        
    job = JOBS[job_id]
    if job["status"] == "completed":
        return job["result"]
    elif job["status"] == "failed":
        return {"status": "failed", "error": job.get("error")}
    else:
        return {"status": job["status"], "message": "Verification is still in progress."}
