import json
import os
from typing import Dict, Any, List
from google import genai
from google.genai import types

from src.models.trust_score import TrustScoreReport, VerifiedClaim, Discrepancy
from src.integrations.github_auditor import GitHubAuditor
from src.integrations.linkedin import LinkedInScraper

class FactChecker:
    def __init__(self):
        # Using Gemini 1.5 Pro to synthesize and analyze discrepancies
        # Requires GOOGLE_API_KEY to be set in the environment
        self.api_key = os.environ.get("GOOGLE_API_KEY")
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None
            
        self.linkedin_scraper = LinkedInScraper()
        self.github_auditor = GitHubAuditor()

    async def verify_candidate(
        self,
        candidate_name: str,
        resume_text: str,
        linkedin_url: str = None,
        github_handle: str = None
    ) -> TrustScoreReport:
        
        # 1. Fetch External Data
        linkedin_data = ""
        if linkedin_url:
            linkedin_data = await self.linkedin_scraper.fetch_profile(linkedin_url)
            
        github_data = ""
        if github_handle:
            github_data = await self.github_auditor.audit_technical_skills(github_handle)

        # 2. Mock Fallback if no LLM configured
        if not self.client:
            return self._mock_fact_check(candidate_name, resume_text, linkedin_data, github_data)

        # 3. Formulate prompt for Gemini
        prompt = f"""
You are an expert technical recruiter and background investigator. Your job is to verify candidate claims 
by cross-referencing their Resume, LinkedIn Profile, and GitHub Activity.

**Candidate Name**: {candidate_name}

**Source 1: Resume Text**
{resume_text}

**Source 2: LinkedIn Profile Summary**
{linkedin_data}

**Source 3: GitHub Activity Audit**
{github_data}

Instructions:
1. Extract 3-5 core claims from the resume (e.g., specific job titles/dates, claims of language expertise).
2. For each claim, check if the LinkedIn data or GitHub data supports it, contradicts it, or cannot verify it.
3. If there are contradictions (e.g., date gaps, missing jobs, low GitHub activity despite claiming "expertise"), flag them as discrepancies.
4. Provide an overall Trust Score (0-100) based on the consistency of the information.
5. Provide 2-3 interview questions that directly address the discovered discrepancies.

Respond ONLY with a valid JSON object matching this schema:
{{
  "candidate_name": "{candidate_name}",
  "overall_score": 85,
  "verified_claims": [
    {{
      "claim": "Worked at X Company from 2020-2022",
      "source": "Resume",
      "verified": true,
      "evidence": "Matches LinkedIn profile experience entry exactly."
    }}
  ],
  "discrepancies": [
    {{
      "issue": "Date mismatch",
      "severity": "Medium",
      "details": "Resume says 2018-2020 at StartupY, but LinkedIn shows 2019-2020."
    }}
  ],
  "interview_questions": [
    "I noticed a slight difference in your start date at StartupY on your resume vs LinkedIn. Could you clarify your timeline?"
  ]
}}
"""

        # 4. Call LLM
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                ),
            )
            
            # 5. Parse JSON back to Pydantic Model
            result_dict = json.loads(response.text)
            return TrustScoreReport(**result_dict)
            
        except Exception as e:
            print(f"Error during LLM fact-checking: {e}")
            return self._mock_fact_check(candidate_name, resume_text, linkedin_data, github_data)

    def _mock_fact_check(self, name: str, resume: str, linkedin: str, github: str) -> TrustScoreReport:
        """Fallback mock response if LLM call fails or isn't configured."""
        return TrustScoreReport(
            candidate_name=name or "Unknown Candidate",
            overall_score=80,
            verified_claims=[
                VerifiedClaim(
                    claim="Extracting basic info",
                    source="Resume",
                    verified=True,
                    evidence="Fallback logic triggered due to missing LLM configuration."
                )
            ],
            discrepancies=[
                Discrepancy(
                    issue="Missing API Key",
                    severity="High",
                    details="Could not perform deep ReAct loop, GOOGLE_API_KEY not set."
                )
            ],
            interview_questions=[
                "Could you provide more details about your recent projects, as I couldn't access your GitHub fully?"
            ]
        )
