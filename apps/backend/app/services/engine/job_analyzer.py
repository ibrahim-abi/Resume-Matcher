"""Job description analyzer for the Engine Flow."""

import json

from tenacity import retry, stop_after_attempt, wait_exponential

from app.llm import get_llm_config, complete_json
from app.services.engine.models import JobRequirements


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def analyze_job_description(job_description: str) -> JobRequirements:
    """Analyzes a raw job description string and extracts structured requirements using LiteLLM."""
    
    system_prompt = (
        "You are an expert technical recruiter and ATS specialist. "
        "Analyze the following job description and extract the required skills, "
        "preferred skills, technologies, ATS keywords, experience level, and key responsibilities. "
        "Be comprehensive with the ATS keywords as they will be used for resume scoring.\n"
        f"You MUST output raw valid JSON exactly matching this schema:\n{JobRequirements.model_json_schema()}"
    )
    
    config = get_llm_config()
    
    
    response_dict = await complete_json(
        prompt=job_description,
        system_prompt=system_prompt,
        config=config,
    )
    
    return JobRequirements.model_validate(response_dict)
