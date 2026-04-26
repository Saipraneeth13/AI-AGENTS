"""
Gap Analysis Agent
------------------
Computes skill gaps and generates personalised learning plans.
"""
from utils.groq_client import call_llm_json

GAP_SYSTEM = """You are an expert Career Coach and Technical Skills Analyst.
Compare the required skills from the Job Description against the assessed scores of the candidate.
CRITICAL: You must explicitly identify "adjacent skills" the candidate already possesses that can be leveraged to quickly learn the missing required skills.
Read the provided interview transcript (Q&A) to determine specific strengths and weaknesses demonstrated by the candidate, calculate overall technical and communication scores, and list any required JD skills that the candidate completely lacks.

Categories for gap_severity: "none", "minor", "moderate", "significant", "critical".

Output valid JSON ONLY matching this schema:
{
  "overall_readiness_score": <int 0-100>,
  "overall_technical_score": <int 0-100>,
  "overall_communication_score": <int 0-100>,
  "skill_scores": [
    {
      "skill": "Skill Name",
      "required_proficiency": "intermediate",
      "assessed_score": <int 0-100>,
      "gap_severity": "moderate",
      "time_to_close_weeks": <int>,
      "adjacent_skills_leveraged": ["existing skill 1", "existing skill 2"]
    }
  ],
  "critical_gaps": ["gap 1", "gap 2"],
  "missing_skills_from_jd": ["skill A", "skill B"],
  "strength_areas": ["strength 1", "strength 2"],
  "qa_strengths_summary": "A detailed paragraph summarizing the candidate's strong points based explicitly on their answers in the transcript.",
  "qa_weaknesses_summary": "A detailed paragraph summarizing where the candidate struggled, faltered, or lacked depth based explicitly on their answers in the transcript.",
  "quick_wins": ["quick win 1"],
  "strategic_recommendation": "Overall advice focusing on realistic acquisition via adjacent skills"
}"""

async def run_gap_analysis(
    required_skills: list[dict],
    claimed_skills: list[dict],
    assessment_scores: dict[str, float],
    conversation_context: str = ""
) -> dict:
    prompt = f"""
Required Skills (JD):
{required_skills}

Candidate's Claimed Skills (Resume):
{claimed_skills}

Actual Assessed Scores (0-100) from Interview:
{assessment_scores}

Interview Transcript (Q&A):
{conversation_context}

Generate the comprehensive gap analysis based on the candidate's actual performance in the transcript.
"""
    result = await call_llm_json(GAP_SYSTEM, prompt)
    return result or {"overall_readiness_score": 0, "overall_technical_score": 0, "overall_communication_score": 0, "skill_scores": []}


PLAN_SYSTEM = """You are an expert Technical Educator and Curriculum Designer.
Based on the candidate's gap analysis, generate a highly structured, personalised learning plan.
CRITICAL: The plan MUST focus on leveraging the candidate's existing "adjacent skills" to realistically acquire the missing skills. Highlight why this transition is realistic.

Make sure the plan is realistic and specifies actual resources (real books, popular courses, official docs).

Output valid JSON ONLY matching this schema:
{
  "plan_title": "Plan title",
  "total_duration_weeks": <int>,
  "time_commitment_hours_per_week": <int>,
  "learning_phases": [
    {
      "phase": 1,
      "title": "Phase title",
      "duration_weeks": <int>,
      "focus_skills": ["skill 1", "skill 2"],
      "adjacent_skills_leveraged": ["existing skill 1"],
      "why_this_is_realistic": "Short explanation of how existing knowledge accelerates this phase",
      "weekly_breakdown": [
        {
          "week": 1,
          "theme": "Week theme",
          "goals": ["goal 1"],
          "resources": [
            {
              "type": "Course|Book|Video|Article|Project",
              "title": "Resource Name",
              "provider": "Platform/Author",
              "url": "optional url",
              "time_hours": <int>,
              "free": true/false
            }
          ],
          "milestone": "End of week milestone/deliverable"
        }
      ]
    }
  ],
  "capstone_project": {
    "title": "Project Title",
    "description": "What they will build to prove mastery using both existing and newly acquired skills"
  }
}"""

async def generate_learning_plan(
    candidate_info: dict,
    gap_analysis: dict,
    job_context: str
) -> dict:
    prompt = f"""
Candidate Info: {candidate_info}
Job Context: {job_context}

Gap Analysis Results:
{gap_analysis}

Generate a structured learning plan to close the critical and moderate gaps.
"""
    result = await call_llm_json(PLAN_SYSTEM, prompt)
    return result or {"plan_title": "Learning Plan Generation Failed", "learning_phases": []}
