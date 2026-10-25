from pydantic import BaseModel, Field
from enum import Enum


class FitLevel(str, Enum):
    STRONG = "strong"
    PARTIAL = "partial"
    WEAK = "weak"


class CVEdit(BaseModel):
    section: str = Field(description="Which part of the CV to change, e.g. 'Projects' or 'Skills'")
    suggestion: str = Field(description="What to change, using only experience the CV already shows. Never invent experience.")
    reason: str = Field(description="Which requirement in the job description this addresses")


class SkillGap(BaseModel):
    skill: str = Field(description="Name of a skill the job requires that the CV does not show")
    why_it_matters: str = Field(description="One short sentence on why this job needs it")


class ApplicationAnalysis(BaseModel):
    fit_reason: str = Field(description="Two or three sentences explaining the chosen fit level, comparing the CV against the job description. Be honest even if the fit is weak.")
    fit_level: FitLevel = Field(description="strong: most required skills are shown on the CV. partial: some are. weak: few or none.")
    strengths: list[str] = Field(description="Short items, each a specific strength taken from the CV that matches this job. Maximum 5.")
    cv_edits: list[CVEdit] = Field(description="Edits that make existing CV experience more visible for this job. Maximum 5.")
    skills_to_learn: list[SkillGap] = Field(description="Real gaps: skills the job requires that the CV does not show. Do not repeat anything listed in cv_edits.")
    is_track_mismatch: bool = Field(description="True only if this job is clearly outside the user's career direction")
    track_note: str = Field(description="One or two sentences. If is_track_mismatch is true, explain why. If false, briefly say what aligns.")


class Message (BaseModel):
    content: str
