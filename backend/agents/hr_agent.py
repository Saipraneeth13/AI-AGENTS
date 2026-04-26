"""
HR Agent
--------
Assesses soft skills, cultural fit, and behavioural competencies.
"""
from utils.groq_client import call_llm_json

HR_SYSTEM = """You are an empathetic yet rigorous HR Interviewer and Behavioural Analyst.
Your goal is to assess a candidate's soft skills and cultural fit using the STAR method (Situation, Task, Action, Result).

Guidelines:
1. Ask open-ended, behavioural questions.
2. Keep questions concise and natural.
3. Provide ideal indicators you expect in a strong answer.

CRITICAL: You MUST output valid JSON ONLY matching exactly this schema:
{
  "question": "The interview question",
  "ideal_indicators": ["indicator 1", "indicator 2"]
}
Do not include any other text, markdown blocks, or explanation."""

async def generate_hr_question(
    skill: str,
    job_context: str,
    question_number: int,
    previous_responses: list[str]
) -> dict:
    prompt = f"""
Skill to assess: {skill}
Job Context: {job_context}
Question Number: {question_number}

Previous Responses context:
{previous_responses}

Generate a behavioural interview question.
"""
    result = await call_llm_json(HR_SYSTEM, prompt)
    if not result:
        return {
            "question": f"Can you tell me about a time you demonstrated {skill} in a professional setting?",
            "ideal_indicators": ["Provides specific example", "Shows clear action taken", "Highlights positive outcome"]
        }
    return result


HR_EVAL_SYSTEM = """You are an empathetic HR Interviewer evaluating a behavioural response.
Score from 0-100 based on the STAR method presence, clarity, self-awareness, and alignment with ideal indicators.

CRITICAL: You MUST output valid JSON ONLY matching exactly this schema:
{
  "score": <int 0-100>,
  "feedback": "Constructive feedback addressed to the candidate",
  "red_flags": ["flag 1", "flag 2"]
}
Do not include any other text, markdown blocks, or explanation."""

async def evaluate_hr_answer(
    skill: str,
    question: str,
    candidate_answer: str,
    ideal_indicators: list[str]
) -> dict:
    prompt = f"""
Skill: {skill}
Question: {question}
Ideal Indicators: {', '.join(ideal_indicators)}

Candidate's Answer:
{candidate_answer}

Evaluate the response.
"""
    result = await call_llm_json(HR_EVAL_SYSTEM, prompt)
    if not result:
        return {"score": 50, "feedback": "Could not parse evaluation."}
    return result


PROFILE_SYSTEM = """You are a Talent Acquisition Lead.
Based on the candidate's HR interview responses, generate a behavioural profile.

CRITICAL: You MUST output valid JSON ONLY matching exactly this schema:
{
  "executive_summary": "Overall behavioural assessment",
  "strengths": ["strength 1", "strength 2"],
  "areas_for_growth": ["area 1", "area 2"],
  "cultural_fit_score": <int 0-100>
}
Do not include any other text, markdown blocks, or explanation."""

async def generate_candidate_profile(hr_history: list[dict]) -> dict:
    prompt = f"HR Interview History:\n{hr_history}\n\nGenerate the candidate's behavioural profile."
    result = await call_llm_json(PROFILE_SYSTEM, prompt)
    return result or {
        "executive_summary": "Insufficient data to form a complete profile.",
        "strengths": [], "areas_for_growth": [], "cultural_fit_score": 0
    }
