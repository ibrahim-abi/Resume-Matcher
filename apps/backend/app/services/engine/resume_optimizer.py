"""Resume optimizer for the Engine Flow."""

import json

from tenacity import retry, stop_after_attempt, wait_exponential

from app.llm import get_llm_config, complete_json
from app.services.engine.models import JobRequirements, ResumeEngineData, OptimizedSections


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def optimize_resume(base_resume: ResumeEngineData, job_reqs: JobRequirements) -> ResumeEngineData:
    """Optimizes a base resume's bullet points and skills against job requirements using LiteLLM."""
    
    system_prompt = (
        "You are an expert resume writer and ATS optimizer. "
        "Your task is to take a candidate's base resume sections and a set of job requirements, "
        "and rewrite the resume's experience, project bullet points, and skills to align "
        "perfectly with the job description."
        "\n\nSTRICT RULES FOR IMPACT & METRICS:"
        "\n1. Every relevant bullet point MUST be re-written to use strong action verbs (e.g., 'Spearheaded', 'Engineered', 'Orchestrated')."
        "\n2. You MUST QUANTIFY achievements where possible. If the original doesn't have numbers, use reasonable estimates or phrasing that implies scale (e.g., 'Reduced latency by over 30%', 'Supported 5+ cross-functional teams')."
        "\n3. Map ATS keywords from the job description naturally into the experience bullets."
        "\n4. Do NOT invent new degrees or job titles. Keep all factual data accurate."
        "\n5. Tailor the 'skills' list to prioritize those mentioned in the job requirements."
        f"\nYou MUST output raw valid JSON exactly matching this schema for the changed sections:\n{OptimizedSections.model_json_schema()}"
    )
    
    # Only pass the sections that actually need to be rewritten to save thousands of input tokens
    candidate_subset = base_resume.model_dump(include={"experience", "projects", "skills"})
    
    user_prompt = (
        f"Job Requirements:\n{job_reqs.model_dump_json(indent=2)}\n\n"
        f"Candidate Data (To Optimize):\n{json.dumps(candidate_subset, indent=2)}"
    )

    config = get_llm_config()

    response_dict = await complete_json(
        prompt=user_prompt,
        system_prompt=system_prompt,
        config=config,
        max_tokens=2500,  # Cap output tokens to trigger num_predict correctly
    )
    
    # Reassemble the final resume by merging the optimized sections back into the base resume
    optimized_subset = OptimizedSections.model_validate(response_dict)
    
    final_resume = base_resume.model_copy()
    final_resume.experience = optimized_subset.experience
    final_resume.projects = optimized_subset.projects
    
    # NEW: Merge skills back correctly (fixing previous bug where skills were dropped)
    if optimized_subset.skills:
        final_resume.skills = optimized_subset.skills
    
    return final_resume
