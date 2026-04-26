"""
Technical Agent
---------------
Handles deep-dive technical questioning, coding prompts, and evaluation.
"""
from utils.groq_client import call_llm_json

TECH_SYSTEM = """You are an expert Senior Technical Interviewer.
Your goal is to accurately assess a candidate's proficiency in a specific technical skill.

Guidelines for question generation:
1. Ensure the difficulty matches the `bloom_taxonomy_level` requested.
2. Provide a practical scenario or coding problem, not just trivia.
3. If coding is required, include a `code_prompt` and specify the `language`.
4. Provide `expected_concepts` that should be present in a good answer.

Output valid JSON ONLY matching this schema:
{
  "question": "The interview question (spoken/text to the candidate)",
  "code_prompt": "Optional. The starting code snippet for the Monaco editor",
  "language": "python|javascript|typescript|java|cpp (optional)",
  "expected_concepts": ["concept 1", "concept 2"]
}"""

async def generate_technical_question(
    skill: str,
    skill_description: str,
    claimed_proficiency: str,
    question_number: int,
    previous_score: int | None = None,
    context: str = "",
    whiteboard_mode: bool = False,
    force_conceptual: bool = False,
    target_level: str | None = None
) -> dict:
    
    # Use dynamic target level if provided, otherwise compute it
    if not target_level:
        target_level = _determine_bloom_level(question_number, previous_score)

    prompt = f"""
Skill to assess: {skill}
Candidate's claimed proficiency: {claimed_proficiency}
Context/JD: {skill_description}
Question Number: {question_number} (Global)
Target Difficulty (Bloom's): {target_level}

Previous Interview Context:
{context}

Generate a technical question.
"""
    if force_conceptual:
        prompt += "\nCONCEPTUAL PHASE: You MUST NOT provide a `code_prompt` or ask the candidate to write code. Focus entirely on architectural basics, theoretical trade-offs, and 'how-it-works' questions in the context of the Job Description."

    if whiteboard_mode and not force_conceptual:
        prompt += "\nWHITEBOARD MODE: Instead of a standard question, generate a broken or suboptimal code snippet for this skill. Ask the candidate to 1) Identify the bug/issue, 2) Fix it, and 3) Optimise or explain the time complexity. Ensure the `code_prompt` JSON field contains the broken code snippet."
    return await call_llm_json(TECH_SYSTEM, prompt)


EVAL_SYSTEM = """You are an expert Senior Technical Interviewer evaluating a candidate's answer.
Score the answer from 0-100 based on technical accuracy, clarity, and coverage of expected concepts.

Output valid JSON ONLY matching this schema:
{
  "score": <int 0-100>,
  "feedback": "Short, constructive feedback addressed to the candidate",
  "missing_concepts": ["concept 1", "concept 2"]
}"""

async def evaluate_technical_answer(
    skill: str,
    question: str,
    expected_concepts: list[str],
    candidate_answer: str
) -> dict:
    prompt = f"""
Skill: {skill}
Question asked: {question}
Expected concepts: {', '.join(expected_concepts)}

Candidate's Answer:
{candidate_answer}

Evaluate the answer.
"""
    result = await call_llm_json(EVAL_SYSTEM, prompt)
    if not result:
        return {"score": 50, "feedback": "Could not parse evaluation.", "missing_concepts": []}
    return result


CODE_SYSTEM = """You are an expert Code Reviewer.
Evaluate the candidate's code submission.
Check for correctness, edge cases, efficiency, and readability.

Output valid JSON ONLY matching this schema:
{
  "score": <int 0-100>,
  "feedback": "Short, constructive code review feedback",
  "issues_found": ["issue 1", "issue 2"]
}"""

async def evaluate_code_submission(code: str, language: str, prompt_context: str) -> dict:
    prompt = f"""
Language: {language}
Prompt/Task: {prompt_context}

Candidate's Code:
```
{code}
```

Evaluate the code.
"""
    return await call_llm_json(CODE_SYSTEM, prompt)


def _determine_bloom_level(question_num: int, prev_score: int | None) -> str:
    """Adaptive difficulty logic based on Bloom's Taxonomy."""
    levels = ["Remember/Understand", "Apply/Analyse", "Evaluate/Create"]
    if question_num == 1:
        return levels[1]  # Start at Apply/Analyse
    
    # Adapt based on score
    idx = 1
    if prev_score is not None:
        if prev_score < 40:
            idx = 0  # Drop down
        elif prev_score > 80:
            idx = 2  # Step up
    
    return levels[idx]
