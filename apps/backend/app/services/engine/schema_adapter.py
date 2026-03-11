"""Schema adapter: converts between Resume-Matcher and ResumeEngine data models."""

from __future__ import annotations

from typing import Any

from app.schemas.models import (
    ResumeData,
    PersonalInfo,
    Experience,
    Education,
    Project,
    AdditionalInfo,
)
from app.services.engine.models import (
    ResumeEngineData,
    PersonalInformation,
    SkillRecord,
    EngineExperience,
    EngineEducation,
    EngineProject,
)


def rm_to_engine(rm: ResumeData) -> ResumeEngineData:
    """Convert Resume-Matcher ResumeData → ResumeEngine ResumeEngineData."""
    pi = rm.personalInfo

    personal_info = PersonalInformation(
        name=pi.name or "Unknown",
        title=pi.title or None,
        email=pi.email or "",
        phone=pi.phone or None,
        linkedin=pi.linkedin or None,
        github=pi.github or None,
        website=pi.website or None,
        location=pi.location or None,
        summary=rm.summary or None,
    )

    # Skills: flatten additional skills into skill records
    skills: list[SkillRecord] = []
    add = rm.additional
    if add.technicalSkills:
        skills.append(SkillRecord(category="Technical Skills", skills=add.technicalSkills))
    if add.languages:
        skills.append(SkillRecord(category="Languages", skills=add.languages))
    if add.certificationsTraining:
        skills.append(SkillRecord(category="Certifications", skills=add.certificationsTraining))
    if add.awards:
        skills.append(SkillRecord(category="Awards", skills=add.awards))

    # Work experience: description list[str] → bullets list[str]
    experience: list[EngineExperience] = [
        EngineExperience(
            title=e.title,
            company=e.company,
            location=e.location,
            start_date=_split_years(e.years)[0],
            end_date=_split_years(e.years)[1],
            bullets=e.description,
        )
        for e in rm.workExperience
    ]

    # Education
    education: list[EngineEducation] = [
        EngineEducation(
            degree=e.degree,
            institution=e.institution,
            location=getattr(e, "location", None),
            start_date=_split_years(e.years)[0],
            end_date=_split_years(e.years)[1],
            gpa=None,
        )
        for e in rm.education
    ]

    # Projects
    projects: list[EngineProject] = [
        EngineProject(
            name=p.name,
            description=p.role or None,
            technologies=[],
            bullets=p.description,
            link=p.website or p.github or None,
        )
        for p in rm.personalProjects
    ]

    return ResumeEngineData(
        personal_info=personal_info,
        skills=skills,
        experience=experience,
        education=education,
        projects=projects,
    )


def engine_to_rm(engine: ResumeEngineData, original: ResumeData) -> ResumeData:
    """Convert optimized ResumeEngine data back into Resume-Matcher ResumeData.

    Merges the AI-optimized content back while preserving structural fields
    (IDs, section metadata, custom sections) from the original.
    """
    pi = engine.personal_info
    personal_info = PersonalInfo(
        name=pi.name,
        title=pi.title or "",
        email=pi.email,
        phone=pi.phone or "",
        location=pi.location or "",
        website=pi.website,
        linkedin=pi.linkedin,
        github=pi.github,
    )

    summary = pi.summary or original.summary

    # Work experience — merge bullets back into description
    work_exp: list[Experience] = []
    for i, e in enumerate(engine.experience):
        orig_id = original.workExperience[i].id if i < len(original.workExperience) else i + 1
        work_exp.append(
            Experience(
                id=orig_id,
                title=e.title,
                company=e.company,
                location=e.location,
                years=f"{e.start_date} – {e.end_date}",
                description=e.bullets,
            )
        )

    # Education
    edus: list[Education] = []
    for i, e in enumerate(engine.education):
        orig_id = original.education[i].id if i < len(original.education) else i + 1
        edus.append(
            Education(
                id=orig_id,
                institution=e.institution,
                degree=e.degree,
                years=f"{e.start_date or ''} – {e.end_date}".strip(" –"),
                description=None,
            )
        )

    # Projects
    projs: list[Project] = []
    for i, p in enumerate(engine.projects):
        orig_id = original.personalProjects[i].id if i < len(original.personalProjects) else i + 1
        projs.append(
            Project(
                id=orig_id,
                name=p.name,
                role=p.description or "",
                years="",
                github=None,
                website=p.link,
                description=p.bullets,
            )
        )

    # Rebuild additional from skill records
    tech: list[str] = []
    langs: list[str] = []
    certs: list[str] = []
    awards: list[str] = []
    for sr in engine.skills:
        cat = sr.category.lower()
        if "technical" in cat or "skill" in cat:
            tech.extend(sr.skills)
        elif "language" in cat:
            langs.extend(sr.skills)
        elif "cert" in cat:
            certs.extend(sr.skills)
        elif "award" in cat:
            awards.extend(sr.skills)
        else:
            tech.extend(sr.skills)

    additional = AdditionalInfo(
        technicalSkills=tech or original.additional.technicalSkills,
        languages=langs or original.additional.languages,
        certificationsTraining=certs or original.additional.certificationsTraining,
        awards=awards or original.additional.awards,
    )

    return ResumeData(
        personalInfo=personal_info,
        summary=summary,
        workExperience=work_exp,
        education=edus,
        personalProjects=projs,
        additional=additional,
        sectionMeta=original.sectionMeta,
        customSections=original.customSections,
    )


def _split_years(years: str) -> tuple[str, str]:
    """Split '2020 – 2023' or '2020-2023' into (start, end)."""
    if not years:
        return ("", "Present")
    for sep in [" – ", " - ", "–", "-", " to "]:
        if sep in years:
            parts = years.split(sep, 1)
            return parts[0].strip(), parts[1].strip()
    return ("", years.strip())
