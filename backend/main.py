"""
AI Skill Assessment & Personalised Learning Plan — FastAPI Backend
Multi-agent: Parser · Technical · HR · Gap Analysis · Learning Plan
"""
import json
import uuid
import asyncio
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, Form, UploadFile, WebSocket, WebSocketDisconnect, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from pydantic import BaseModel

from agents.orchestrator import AssessmentOrchestrator
from utils.pdf_parser import extract_text_from_pdf

app = FastAPI(title="Skill Assessment Agent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store
sessions: dict[str, AssessmentOrchestrator] = {}


@app.post("/api/start-session")
async def start_session(
    jd_file: UploadFile = File(None),
    jd_text: str = Form(""),
    resume_file: UploadFile = File(...),
):
    """Upload JD + Resume, parse them, kick off orchestrator."""
    session_id = str(uuid.uuid4())

    # Parse resume PDF
    resume_bytes = await resume_file.read()
    resume_text = extract_text_from_pdf(resume_bytes)

    # Parse JD — either uploaded PDF or raw text
    if jd_file and jd_file.filename:
        jd_bytes = await jd_file.read()
        jd_text = extract_text_from_pdf(jd_bytes)

    if not jd_text.strip():
        return JSONResponse({"error": "Job description is required"}, status_code=400)

    # Create orchestrator for this session
    orch = AssessmentOrchestrator(session_id, jd_text, resume_text)
    await orch.initialise()
    sessions[session_id] = orch

    return {
        "session_id": session_id,
        "candidate_name": orch.state.get("candidate_name", "Candidate"),
        "skills_to_assess": orch.state.get("required_skills", []),
        "resume_summary": orch.state.get("resume_summary", ""),
        "jd_summary": orch.state.get("jd_summary", ""),
    }


@app.websocket("/ws/{session_id}")
async def assessment_ws(ws: WebSocket, session_id: str):
    """Real-time conversational assessment over WebSocket."""
    await ws.accept()

    orch = sessions.get(session_id)
    if not orch:
        await ws.send_json({"type": "error", "message": "Session not found"})
        await ws.close()
        return

    # Send first question
    first_q = await orch.get_next_question()
    await ws.send_json({"type": "question", **first_q})

    try:
        while True:
            data = await ws.receive_json()
            msg_type = data.get("type")

            if msg_type == "answer":
                result = await orch.process_answer(data.get("content", ""))
                await ws.send_json({"type": "evaluation", **result})

                if result.get("assessment_complete"):
                    # Run gap analysis + learning plan
                    await ws.send_json({"type": "status", "message": "Analysing skill gaps…"})
                    gap_result = await orch.run_gap_analysis()
                    await ws.send_json({"type": "gap_analysis", **gap_result})

                    await ws.send_json({"type": "status", "message": "Generating learning plan…"})
                    plan_result = await orch.generate_learning_plan()
                    await ws.send_json({"type": "learning_plan", **plan_result})
                    break
                else:
                    next_q = await orch.get_next_question()
                    await ws.send_json({"type": "question", **next_q})

            elif msg_type == "skip":
                orch.skip_current_skill()
                next_q = await orch.get_next_question()
                if next_q:
                    await ws.send_json({"type": "question", **next_q})

            elif msg_type == "code_submission":
                result = await orch.evaluate_code(data.get("code", ""), data.get("language", "python"))
                await ws.send_json({"type": "code_evaluation", **result})
                
            elif msg_type == "code_buffer":
                orch.state["code_buffer"] = data.get("code", "")

    except WebSocketDisconnect:
        pass
    finally:
        # Clean up session after a delay
        asyncio.create_task(_cleanup_session(session_id, delay=3600))


async def _cleanup_session(session_id: str, delay: int):
    await asyncio.sleep(delay)
    sessions.pop(session_id, None)


@app.get("/api/session/{session_id}/state")
async def get_session_state(session_id: str):
    orch = sessions.get(session_id)
    if not orch:
        return JSONResponse({"error": "Not found"}, status_code=404)
    return orch.state


# --- New: HTTP polling endpoints for Vercel (WebSocket fallback) ---

class AnswerPayload(BaseModel):
    content: str


class CodePayload(BaseModel):
    code: str
    language: str = "python"


@app.get("/api/session/{session_id}/next-question")
async def http_next_question(session_id: str):
    orch = sessions.get(session_id)
    if not orch:
        return JSONResponse({"error": "Session not found"}, status_code=404)
    q = await orch.get_next_question()
    return q or {}


@app.post("/api/session/{session_id}/answer")
async def http_answer(session_id: str, payload: AnswerPayload):
    orch = sessions.get(session_id)
    if not orch:
        return JSONResponse({"error": "Session not found"}, status_code=404)
    result = await orch.process_answer(payload.content)
    response = {"evaluation": result}
    if result.get("assessment_complete"):
        # Run gap analysis + learning plan (long-running; still run synchronously here)
        gap_result = await orch.run_gap_analysis()
        plan_result = await orch.generate_learning_plan()
        response.update({"gap_analysis": gap_result, "learning_plan": plan_result})
    else:
        next_q = await orch.get_next_question()
        response["next_question"] = next_q
    return response


@app.post("/api/session/{session_id}/skip")
async def http_skip(session_id: str):
    orch = sessions.get(session_id)
    if not orch:
        return JSONResponse({"error": "Session not found"}, status_code=404)
    orch.skip_current_skill()
    next_q = await orch.get_next_question()
    return {"next_question": next_q}


@app.post("/api/session/{session_id}/code-eval")
async def http_code_eval(session_id: str, payload: CodePayload):
    orch = sessions.get(session_id)
    if not orch:
        return JSONResponse({"error": "Session not found"}, status_code=404)
    result = await orch.evaluate_code(payload.code, payload.language)
    return result


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
