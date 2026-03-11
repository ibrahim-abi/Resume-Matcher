"""Pydantic models used by the ResumeEngine flow."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Resume Engine internal models (mirroring ResumeEngine_Jinja2/core/models.py)
# ---------------------------------------------------------------------------

class PersonalInformation(BaseModel):
    name: str
    title: Optional[str] = None
    email: str
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None


class SkillRecord(BaseModel):
    category: str
    skills: List[str]


class EngineExperience(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    start_date: str = ""
    end_date: str = ""
    bullets: List[str] = Field(default_factory=list)


class EngineEducation(BaseModel):
    degree: str
    institution: str
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: str = ""
    gpa: Optional[str] = None


class EngineProject(BaseModel):
    name: str
    description: Optional[str] = None
    technologies: List[str] = Field(default_factory=list)
    bullets: List[str] = Field(default_factory=list)
    link: Optional[str] = None


class ResumeEngineData(BaseModel):
    personal_info: PersonalInformation
    skills: List[SkillRecord] = Field(default_factory=list)
    experience: List[EngineExperience] = Field(default_factory=list)
    education: List[EngineEducation] = Field(default_factory=list)
    projects: List[EngineProject] = Field(default_factory=list)


class OptimizedSections(BaseModel):
    """Schema for the LLM output to save tokens by not regenerating unchanged sections."""
    experience: List[EngineExperience] = Field(default_factory=list)
    projects: List[EngineProject] = Field(default_factory=list)
    skills: List[SkillRecord] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Job analysis models
# ---------------------------------------------------------------------------

class JobRequirements(BaseModel):
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)
    ats_keywords: List[str] = Field(default_factory=list)
    experience_level: Optional[str] = None
    key_responsibilities: List[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# ATS Scoring models
# ---------------------------------------------------------------------------

class ATSScore(BaseModel):
    score_percentage: int = Field(ge=0, le=100, description="Overall ATS score out of 100")
    semantic_keyword_match: int = Field(ge=0, le=100, description="Semantic keyword match score")
    impact_and_metrics: int = Field(ge=0, le=100, description="Impact & metrics usage score")
    action_oriented_language: int = Field(ge=0, le=100, description="Action-verb usage score")
    clarity_and_brevity: int = Field(ge=0, le=100, description="Clarity and brevity score")
    matched_keywords: List[str] = Field(default_factory=list)
    missing_keywords: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Engine flow request/response models (used by the API router)
# ---------------------------------------------------------------------------

class EngineFlowRequest(BaseModel):
    resume_id: str
    job_description: str


class EngineFlowResult(BaseModel):
    resume_id: str
    job_requirements: JobRequirements
    ats_score: ATSScore
    optimized_resume: dict  # ResumeData as dict (for frontend consumption)
    pdf_url: Optional[str] = None  # URL of generated PDF (Chromium fallback)
