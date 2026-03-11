"""ATS scorer for the Engine Flow."""

import json

from tenacity import retry, stop_after_attempt, wait_exponential

from app.llm import get_llm_config, complete_json
from app.services.engine.models import ATSScore, JobRequirements, ResumeEngineData


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def calculate_ats_score(resume: ResumeEngineData, requirements: JobRequirements) -> ATSScore:
    """Advanced AI-Driven ATS Scorer using LiteLLM."""
    
    system_prompt = (
        "You are an expert ATS (Applicant Tracking System) specialist and senior technical recruiter. "
        "Your task is to provide a critical yet fair evaluation of the resume against the job description."
        "\n\nSCORING MATRIX:"
        "\n1. Semantic Keyword Match (40%): How well do the skills match? (Allow for synonyms and transferable skills)."
        "\n2. Impact & Metrics (30%): Are achievements quantified? (Numbers, scale, percentages)."
        "\n3. Action-Oriented Language (20%): Use of strong action verbs and clear structure."
        "\n4. Clarity & Brevity (10%): Professionalism and readability."
        "\n\nDOMAIN MATCH RULE:"
        "\n- If the candidate is in a related technical field (e.g., student in AI for a Software role), treat it as a strong match. "
        "\n- Only apply a severe penalty (score < 40%) if the fields are completely unrelated (e.g., Yoga Instructor for a DevOps role)."
        "\n\nOUTPUT REQUIREMENTS:"
        "\n- Identify `matched_keywords` and `missing_keywords`."
        "\n- Provide high-quality, actionable `recommendations` targeted at boosting specifically the 'Impact' and 'Keywords' scores."
        f"\nYou MUST output raw valid JSON exactly matching this schema:\n{ATSScore.model_json_schema()}"
    )

    
    # Exclude personal_info to save tokens (name/email don't affect ATS score)
    candidate_subset = resume.model_dump(exclude={"personal_info"})

    user_prompt = f"""
    Job Requirements:
    {requirements.model_dump_json(indent=2)}

    Resume Data (Evaluation Subset):
    {json.dumps(candidate_subset, indent=2)}
    """
    
    config = get_llm_config()

    response_dict = await complete_json(
        prompt=user_prompt,
        system_prompt=system_prompt,
        config=config,
        max_tokens=1500,  # Cap token generation
    )

    return ATSScore.model_validate(response_dict)
