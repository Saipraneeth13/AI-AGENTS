from fastapi import APIRouter, UploadFile, File, Form, WebSocket, WebSocketDisconnect
from typing import Optional
import os

router = APIRouter()

# In-memory storage for MVP. In production, use SQLite/Postgres.
sessions = {}

@router.post("/upload")
async def upload_documents(
    resume: UploadFile = File(...),
    job_description: Optional[str] = Form(None),
    job_description_file: Optional[UploadFile] = File(None)
):
    """
    Endpoint to upload the Resume and Job Description.
    Returns a session_id.
    """
    # 1. Save files temporarily
    # 2. Invoke Parser Agent to extract skills
    # 3. Create a session record
    
    session_id = "test-session-123" # Mock ID
    
    sessions[session_id] = {
        "resume_filename": resume.filename,
        "status": "parsed"
    }
    
    return {
        "session_id": session_id,
        "message": "Documents uploaded and parsed successfully."
    }

@router.websocket("/ws/{session_id}")
async def assessment_websocket(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time conversational assessment.
    """
    await websocket.accept()
    if session_id not in sessions:
        await websocket.send_json({"error": "Invalid session ID"})
        await websocket.close()
        return

    try:
        # Initial greeting from the agent
        await websocket.send_json({
            "type": "message",
            "content": "Hello! I'm ready to begin the technical assessment. Let's start with a question based on your resume."
        })
        
        while True:
            # Receive user's answer (text or transcribed voice)
            data = await websocket.receive_text()
            
            # Send to Orchestrator/Technical Agent
            # (Mock response for now)
            response = f"You said: {data}. That's interesting. Here is the next question..."
            
            await websocket.send_json({
                "type": "message",
                "content": response
            })
    except WebSocketDisconnect:
        print(f"Client {session_id} disconnected")

@router.get("/report/{session_id}")
async def get_report(session_id: str):
    """
    Returns the gap analysis and learning plan.
    """
    # Mock data for frontend development
    return {
        "skills": [
            {"subject": "Python", "A": 80, "fullMark": 100},
            {"subject": "React", "A": 60, "fullMark": 100},
            {"subject": "System Design", "A": 50, "fullMark": 100},
            {"subject": "Communication", "A": 90, "fullMark": 100}
        ],
        "learning_plan": "### Week 1\nFocus on React Hooks.\n### Week 2\nSystem Design fundamentals."
    }
