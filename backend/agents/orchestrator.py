"""
Assessment Orchestrator (LangGraph-inspired state machine)
----------------------------------------------------------
Coordinates Parser → Technical → HR → Gap Analysis → Learning Plan agents.
Maintains session state and routes questions appropriately.
"""
import asyncio
from typing import Any

from agents.parser_agent import parse_job_description, parse_resume
from agents.technical_agent import (
    generate_technical_question,
    evaluate_technical_answer,
    evaluate_code_submission,
)
from agents.hr_agent import generate_hr_question, evaluate_hr_answer, generate_candidate_profile
from agents.gap_learning_agent import run_gap_analysis, generate_learning_plan


class AssessmentOrchestrator:
    """
    State machine for a single candidate assessment session.

    State transitions:
      INIT → PARSING → ASSESSING → GAP_ANALYSIS → LEARNING_PLAN → COMPLETE
    """

    CONCEPTUAL_LIMIT = 12 # TODO: restore to 10 for production
    CODING_LIMIT = 3      # TODO: restore to 3 for production

    def __init__(self, session_id: str, jd_text: str, resume_text: str):
        self.session_id = session_id
        self.jd_text = jd_text
        self.resume_text = resume_text
        self.state: dict[str, Any] = {
            "phase": "INIT",
            "current_phase": "CONCEPTUAL",
            "total_questions_asked": 0,
            "candidate_name": "",
            "required_skills": [],
            "claimed_skills": [],
            "jd_summary": "",
            "resume_summary": "",
            "skill_queue": [],          # skills left to assess
            "current_skill": None,
            "current_question_number": 0,
            "skill_scores": {},         # skill → list of scores
            "skill_history": {},        # skill → list of {q, a, score}
            "current_question": None,
            "conversation_context": "",
            "hr_responses": [],
            "assessment_complete": False,
        }

    async def initialise(self):
        """Parse JD + Resume concurrently and set up the skill queue."""
        self.state["phase"] = "PARSING"

        jd_data, resume_data = await asyncio.gather(
            parse_job_description(self.jd_text),
            parse_resume(self.resume_text),
        )

        self.state["jd_summary"] = jd_data.get("jd_summary", "")
        self.state["resume_summary"] = resume_data.get("resume_summary", "")
        self.state["candidate_name"] = resume_data.get("candidate_name", "Candidate")
        self.state["claimed_skills"] = resume_data.get("claimed_skills", [])
        self.state["jd_data"] = jd_data
        self.state["resume_data"] = resume_data

        # Build skill queue from JD requirements
        required = jd_data.get("required_skills", [])
        self.state["required_skills"] = [s["skill"] for s in required]

        # Prioritise must-have skills, then nice-to-have
        must_have = [s for s in required if s.get("priority") == "must_have"]
        nice_to_have = [s for s in required if s.get("priority") != "must_have"]
        # Separate technical and soft skills
        tech_skills = [s for s in must_have if s.get("category") == "technical"]
        soft_skills = [s for s in must_have if s.get("category") in ("soft", "domain")]

        # Queue: tech first (max 4), then soft (max 2), then nice-to-have (max 2)
        queue = tech_skills[:4] + soft_skills[:2] + nice_to_have[:2]
        self.state["skill_queue"] = queue
        self.state["phase"] = "ASSESSING"

    async def get_next_question(self) -> dict:
        """Advance state to next question using global phase transition."""
        total = self.state.get("total_questions_asked", 0)

        # Phase Transition Logic
        if total < self.CONCEPTUAL_LIMIT:
            self.state["current_phase"] = "CONCEPTUAL"
        elif total < (self.CONCEPTUAL_LIMIT + self.CODING_LIMIT):
            self.state["current_phase"] = "CODING"
        else:
            self.state["assessment_complete"] = True
            return {"assessment_complete": True}

        current_skill_data = self._pick_skill_for_phase()
        if not current_skill_data:
            self.state["assessment_complete"] = True
            return {"assessment_complete": True}

        self.state["current_skill"] = current_skill_data
        skill = current_skill_data.get("skill", "")
        category = current_skill_data.get("category", "technical")
        
        is_coding_request = (self.state["current_phase"] == "CODING")

        if category == "soft":
            q_data = await generate_hr_question(
                skill=skill,
                job_context=self.state["jd_summary"],
                question_number=total + 1,
                previous_responses=self.state["hr_responses"][-4:],
            )
            q_data["agent"] = "HR"
        else:
            claimed_prof = self._get_claimed_proficiency(skill)
            # Use dynamic target_level based on global question number
            if is_coding_request:
                target_level = "Evaluate/Create"
            else:
                target_level = "Remember/Understand" if total < 5 else "Apply/Analyse"

            q_data = await generate_technical_question(
                skill=skill,
                skill_description=current_skill_data.get("description", ""),
                claimed_proficiency=claimed_prof,
                question_number=total + 1,
                previous_score=None,
                context=self.state["conversation_context"][-500:],
                whiteboard_mode=is_coding_request,
                force_conceptual=not is_coding_request,
                target_level=target_level
            )
            q_data["agent"] = "Technical"

        q_data["skill"] = skill
        q_data["skill_category"] = category
        q_data["progress"] = self._compute_progress()

        self.state["current_question"] = q_data
        self.state["total_questions_asked"] += 1

        return q_data

    async def process_answer(self, answer: str) -> dict:
        """Evaluate candidate's answer and update skill scores."""
        if not answer.strip():
            return {"score": 0, "feedback": "No answer provided.", "assessment_complete": False}

        current = self.state["current_skill"]
        q = self.state["current_question"]
        skill = current.get("skill", "")
        category = current.get("category", "technical")

        if category == "soft":
            eval_result = await evaluate_hr_answer(
                skill=skill,
                question=q.get("question", ""),
                candidate_answer=answer,
                ideal_indicators=q.get("ideal_indicators", []),
            )
            self.state["hr_responses"].append(answer)
        else:
            eval_result = await evaluate_technical_answer(
                skill=skill,
                question=q.get("question", ""),
                expected_concepts=q.get("expected_concepts", []),
                candidate_answer=answer,
            )

        score = eval_result.get("score", 50)

        # Update skill scores
        if skill not in self.state["skill_scores"]:
            self.state["skill_scores"][skill] = []
        self.state["skill_scores"][skill].append(score)

        # DYNAMIC ADAPTATION LOGIC: If candidate is struggling, add a foundational question
        if category == "technical" and score < 50:
            foundational_skill_name = f"Foundations of {skill}"
            already_in_queue = any(s.get("skill") == foundational_skill_name for s in self.state["skill_queue"])
            already_assessed = foundational_skill_name in self.state["skill_scores"]
            
            if not already_in_queue and not already_assessed:
                self.state["skill_queue"].insert(0, {
                    "skill": foundational_skill_name,
                    "category": "technical",
                    "description": f"Fundamental underlying concepts and mechanisms for {skill}",
                    "priority": "must_have"
                })

        # Update conversation context
        self.state["conversation_context"] += (
            f"\n[{skill}] Q: {q.get('question', '')} | A: {answer[:200]} | Score: {score}"
        )

        total = self.state.get("total_questions_asked", 0)
        assessment_complete = total >= (self.CONCEPTUAL_LIMIT + self.CODING_LIMIT)
        self.state["assessment_complete"] = assessment_complete

        return {
            **eval_result,
            "skill": skill,
            "assessment_complete": assessment_complete,
            "progress": self._compute_progress(),
        }

    async def evaluate_code(self, code: str, language: str) -> dict:
        """Evaluate a code submission."""
        q = self.state["current_question"] or {}
        return await evaluate_code_submission(
            code=code,
            language=language,
            prompt_context=q.get("code_prompt", q.get("question", "")),
        )

    async def run_gap_analysis(self) -> dict:
        """Compute skill gaps once assessment is complete."""
        self.state["phase"] = "GAP_ANALYSIS"

        # Aggregate scores: average per skill
        avg_scores = {
            skill: sum(scores) / len(scores)
            for skill, scores in self.state["skill_scores"].items()
            if scores
        }

        result = await run_gap_analysis(
            required_skills=self.state.get("jd_data", {}).get("required_skills", []),
            claimed_skills=self.state.get("claimed_skills", []),
            assessment_scores=avg_scores,
            conversation_context=self.state.get("conversation_context", "")
        )
        self.state["gap_analysis"] = result
        return result

    async def generate_learning_plan(self) -> dict:
        """Generate personalised learning plan from gap analysis."""
        self.state["phase"] = "LEARNING_PLAN"
        resume_data = self.state.get("resume_data", {})
        gap = self.state.get("gap_analysis", {})

        plan = await generate_learning_plan(
            candidate_info=resume_data,
            gap_analysis=gap,
            job_context=self.state.get("jd_summary", ""),
        )
        self.state["learning_plan"] = plan
        self.state["phase"] = "COMPLETE"
        return plan

    def skip_current_skill(self):
        """Mark current skill as skipped (score 0)."""
        current = self.state.get("current_skill")
        if current:
            skill = current.get("skill", "")
            self.state["skill_scores"][skill] = [0]
            self.state["current_skill"] = None
            
    def _pick_skill_for_phase(self):
        queue = self.state["skill_queue"]
        if not queue:
            return None
        phase = self.state.get("current_phase", "CONCEPTUAL")
        
        if phase == "CONCEPTUAL":
            # Round-robin
            skill = queue.pop(0)
            queue.append(skill)
            return skill
        else:
            # Pick a tech skill
            tech_skills = [s for s in queue if s.get("category") == "technical"]
            if tech_skills:
                skill = tech_skills.pop(0)
                queue.remove(skill)
                queue.append(skill)
                return skill
            return queue[0]

    def _get_claimed_proficiency(self, skill: str) -> str:
        for cs in self.state.get("claimed_skills", []):
            if cs.get("skill", "").lower() == skill.lower():
                return cs.get("claimed_proficiency", "intermediate")
        return "beginner"

    def _compute_progress(self) -> dict:
        total_skills = len(self.state.get("required_skills", [])) or 1
        assessed = len(self.state["skill_scores"])
        return {
            "assessed_skills": assessed,
            "total_skills": total_skills,
            "percent": int((self.state.get("total_questions_asked", 0) / (self.CONCEPTUAL_LIMIT + self.CODING_LIMIT)) * 100),
            "current_skill": self.state.get("current_skill", {}).get("skill", ""),
        }
