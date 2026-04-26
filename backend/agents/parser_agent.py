"""
Parser Agent
------------
Extracts structured data from Job Description texts and Resume texts.
"""
from utils.groq_client import call_llm_json

JD_PARSER_SYSTEM = """You are an expert HR Data Analyst. 
Extract key requirements from the provided Job Description text.

Output valid JSON ONLY matching this schema:
{
  "job_title": "Extracted Title",
  "jd_summary": "1-2 sentence summary of the role",
  "required_skills": [
    {
      "skill": "Name of skill",
      "category": "technical|soft|domain",
      "priority": "must_have|nice_to_have",
      "description": "How the skill is used in this role"
    }
  ]
}"""

async def parse_job_description(jd_text: str) -> dict:
    prompt = f"Extract structured data from this Job Description:\n\n{jd_text}"
    result = await call_llm_json(JD_PARSER_SYSTEM, prompt)
    if not result:
        # Fallback
        return {
            "job_title": "Unknown Role",
            "jd_summary": "Failed to parse JD.",
            "required_skills": [{"skill": "Communication", "category": "soft", "priority": "must_have"}]
        }
    return result


RESUME_PARSER_SYSTEM = """You are an expert IT Recruiter.
Extract the candidate's profile and claimed skills from their resume text.

For claimed_proficiency, estimate 'beginner', 'intermediate', or 'expert' based on years of experience or context clues.

Output valid JSON ONLY matching this schema:
{
  "candidate_name": "Name",
  "resume_summary": "1-2 sentence summary of their background",
  "claimed_skills": [
    {
      "skill": "Name of skill",
      "category": "technical|soft|domain",
      "claimed_proficiency": "intermediate"
    }
  ]
}"""

async def parse_resume(resume_text: str) -> dict:
    prompt = f"Extract structured data from this Resume:\n\n{resume_text}"
    result = await call_llm_json(RESUME_PARSER_SYSTEM, prompt)
    if not result:
        return {
            "candidate_name": "Candidate",
            "resume_summary": "Failed to parse Resume.",
            "claimed_skills": []
        }
    return result
