from typing import List, Optional
from pydantic import BaseModel, Field

class VerifiedClaim(BaseModel):
    claim: str = Field(..., description="The specific claim extracted from the resume or user input.")
    source: str = Field(..., description="The source where the claim was found (e.g., 'Resume').")
    verified: bool = Field(..., description="Whether the claim was successfully verified against external sources.")
    evidence: Optional[str] = Field(None, description="Evidence supporting the verification status.")

class Discrepancy(BaseModel):
    issue: str = Field(..., description="The nature of the discrepancy.")
    severity: str = Field(..., description="Severity of the discrepancy (e.g., 'Low', 'Medium', 'High').")
    details: str = Field(..., description="Detailed description of the conflicting information.")

class TrustScoreReport(BaseModel):
    candidate_name: str = Field(..., description="Full name of the candidate.")
    overall_score: int = Field(..., ge=0, le=100, description="Overall trust score from 0 to 100.")
    verified_claims: List[VerifiedClaim] = Field(default_factory=list, description="List of successfully verified claims.")
    discrepancies: List[Discrepancy] = Field(default_factory=list, description="List of discovered discrepancies or red flags.")
    interview_questions: List[str] = Field(default_factory=list, description="Suggested technical or behavioral questions to probe discovered discrepancies during an interview.")

class VerificationRequest(BaseModel):
    resume_text: Optional[str] = Field(None, description="Extracted text from the candidate's resume.")
    linkedin_url: Optional[str] = Field(None, description="LinkedIn profile URL of the candidate.")
    github_handle: Optional[str] = Field(None, description="GitHub username of the candidate.")
