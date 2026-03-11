"""FastAPI router for the Engine Flow (ATS Scoring & LaTeX Export)."""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any

from app.schemas.models import ResumeData
from app.services.engine.models import EngineFlowRequest, EngineFlowResult
from app.services.engine.schema_adapter import rm_to_engine, engine_to_rm
from app.services.engine.job_analyzer import analyze_job_description
from app.services.engine.ats_scorer import calculate_ats_score
from app.services.engine.resume_optimizer import optimize_resume
from app.services.engine.latex_builder import build_latex_resume
from app.services.engine.pdf_compiler import compile_to_pdf_docker
from app.database import db
import os
import uuid
import asyncio
import json
from starlette.responses import FileResponse
from app.config import settings
from pydantic import BaseModel

class EngineGenerateRequest(BaseModel):
    resume_id: str
    job_description: str

class EngineGenerateResponse(BaseModel):
    resume_id: str

router = APIRouter()

@router.post("/score", response_model=EngineFlowResult)
async def score_resume(request: EngineFlowRequest) -> EngineFlowResult:
    """Run the engine flow to optimize a resume and calculate ATS scores."""

    raw_resume = db.get_resume(request.resume_id)
    if not raw_resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    try:
        content_dict = json.loads(raw_resume["content"])
        resume_data = ResumeData.model_validate(content_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse resume: {str(e)}")

    try:
        engine_data = rm_to_engine(resume_data)
        job_reqs = await analyze_job_description(request.job_description)

        optimized_engine_data = await optimize_resume(engine_data, job_reqs)

        ats_score = await calculate_ats_score(optimized_engine_data, job_reqs)
        final_resume_data = engine_to_rm(optimized_engine_data, resume_data)

        return EngineFlowResult(
            resume_id=request.resume_id,
            job_requirements=job_reqs,
            ats_score=ats_score,
            optimized_resume=final_resume_data.model_dump(),
            pdf_url=None
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Engine flow failed: {str(e)}")


# --- NEW ENDPOINT FOR TAILOR CREATION ---
@router.post("/generate", response_model=EngineGenerateResponse)
async def generate_engine_resume(request: EngineGenerateRequest):
    """
    Full dual-engine generation flow:
    Takes Master Resume + Job Description, runs the optimizer, calculates ATS Score,
    and SAVES it as a new Tailored Resume in TinyDB, saving the ATS score permanently.
    Returns the new resume ID.
    """
    resume = db.get_resume(request.resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Master Resume not found")

    try:
        content_dict = resume.get("processed_data")
        if not content_dict and resume.get("content_type") == "json":
            content_dict = json.loads(resume["content"])
        resume_data = ResumeData.model_validate(content_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse resume: {str(e)}")

    try:
        # 1. Translate
        engine_data = rm_to_engine(resume_data)

        # 2. Analyze Job Description
        job_reqs = await analyze_job_description(request.job_description)

        # 3. Optimize Resume
        optimized_engine_data = await optimize_resume(engine_data, job_reqs)

        # 4. Score
        ats_score = await calculate_ats_score(optimized_engine_data, job_reqs)

        # 5. Translate back
        final_resume_data = engine_to_rm(optimized_engine_data, resume_data)

        improved_dump = final_resume_data.model_dump()
        improved_text = json.dumps(improved_dump, indent=2)

        saved_ats_payload = {
            "job_requirements": job_reqs.model_dump(),
            "ats_score": ats_score.model_dump()
        }

        # 6. Save to DB
        tailored_resume = db.create_resume(
            content=improved_text,
            content_type="json",
            filename=f"tailored_engine_{resume.get('filename', 'resume')}",
            is_master=False,
            parent_id=request.resume_id,
            processed_data=improved_dump,
            processing_status="ready",
            engine_ats_score=saved_ats_payload
        )

        return EngineGenerateResponse(resume_id=tailored_resume["resume_id"])

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Engine generation failed: {str(e)}")


@router.post("/export-latex")
async def export_latex_pdf(resume_data: dict) -> FileResponse:
    """
    Receives Resume-Matcher JSON data, converts it to Engine Schema,
    builds the LaTeX string, compiles it via Docker, and returns the PDF file.
    """
    try:
        rm_data = ResumeData.model_validate(resume_data)
        engine_data = rm_to_engine(rm_data)
        latex_str = build_latex_resume(engine_data)

        from pathlib import Path
        exports_dir = settings.data_dir / "exports"
        exports_dir.mkdir(parents=True, exist_ok=True)

        unique_id = str(uuid.uuid4())
        output_pdf = exports_dir / f"resume_{unique_id}.pdf"

        success = await compile_to_pdf_docker(latex_str, str(output_pdf))

        if not success or not output_pdf.exists():
            raise HTTPException(status_code=500, detail="LaTeX compilation failed.")

        return FileResponse(
            path=str(output_pdf),
            filename="ATS_Optimized_Resume.pdf",
            media_type="application/pdf"
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"LaTeX export failed: {str(e)}")
