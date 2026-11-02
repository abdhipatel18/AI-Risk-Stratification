"""
FastAPI REST API Backend for AI Patient Risk Stratification RAG Chatbot & Appointment Scheduling.
"""

import os
import sys
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Ensure root directory is on python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.rag.knowledge_base import KnowledgeBase
from src.rag.retriever import HybridRetriever
from src.rag.appointment_scheduler import AppointmentScheduler
from src.rag.chatbot import ClinicalSchedulingChatbot

app = FastAPI(
    title="AI Patient Risk Stratification & Scheduling RAG API",
    description="RESTful API for clinical risk evaluation, RAG conversational navigation, and intelligent appointment booking.",
    version="1.0.0"
)

# Enable CORS for external frontends and web widgets
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize singletons
kb = KnowledgeBase()
retriever = HybridRetriever(kb)
scheduler = AppointmentScheduler()
chatbot = ClinicalSchedulingChatbot(knowledge_base=kb, retriever=retriever, scheduler=scheduler)


# --- REQUEST & RESPONSE SCHEMAS ---

class ChatRequest(BaseModel):
    message: str = Field(..., description="User message or query")
    patient_id: Optional[str] = Field(None, description="Patient ID (e.g., PAT-0001)")
    conversation_history: Optional[List[Dict[str, str]]] = Field(default=[], description="Prior messages for context")
    api_key: Optional[str] = Field(None, description="Optional LLM API key (Gemini, OpenAI, or Groq)")
    provider: Optional[str] = Field("auto", description="LLM provider: auto, gemini, openai, groq, or local")

class ChatResponse(BaseModel):
    response: str
    retrieved_docs: List[Dict[str, Any]]
    suggested_slots: List[Dict[str, Any]]
    booking_result: Optional[Dict[str, Any]]
    patient_info: Optional[Dict[str, Any]]
    provider_used: str

class BookingRequest(BaseModel):
    patient_id: str = Field(..., description="Unique Patient Identifier (e.g., PAT-0001)")
    appointment_date: str = Field(..., description="Target date in YYYY-MM-DD format")
    appointment_time: str = Field(..., description="Target time slot (e.g., 09:00 AM)")
    reason: Optional[str] = Field(None, description="Clinical reason or primary chief complaint")
    care_gap_addressed: Optional[str] = Field(None, description="Care gap code or description being addressed")

class BookingResponse(BaseModel):
    success: bool
    appointment_id: Optional[str] = None
    patient_id: str
    patient_name: Optional[str] = None
    provider: Optional[str] = None
    clinic: Optional[str] = None
    appointment_date: Optional[str] = None
    appointment_time: Optional[str] = None
    risk_category: Optional[str] = None
    message: str


# --- API ENDPOINTS ---

@app.get("/")
def root():
    return {
        "service": "AI Patient Risk Stratification & Scheduling RAG API",
        "status": "online",
        "docs_url": "/docs",
        "version": "1.0.0"
    }

@app.get("/api/health")
def health_check():
    patients = kb.get_all_patients()
    return {
        "status": "healthy",
        "total_patients_indexed": len(patients),
        "total_knowledge_docs": len(kb.documents),
        "active_appointments": len(scheduler.load_appointments())
    }

@app.get("/api/patients")
def list_patients(
    risk_category: Optional[str] = Query(None, description="Filter by High Risk, Medium Risk, or Lower Risk"),
    clinic: Optional[str] = Query(None, description="Filter by clinic name")
):
    patients = kb.get_all_patients()
    if risk_category:
        patients = [p for p in patients if str(p.get("risk_category", "")).lower() == risk_category.lower()]
    if clinic:
        patients = [p for p in patients if str(p.get("clinic", "")).lower() == clinic.lower()]
    return {"count": len(patients), "patients": patients}

@app.get("/api/patient/{patient_id}")
def get_patient(patient_id: str):
    profile = kb.get_patient_profile(patient_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Patient with ID '{patient_id}' not found.")
    return profile

@app.get("/api/patient/{patient_id}/slots")
def get_slots(patient_id: str, limit: int = Query(6, ge=1, le=20)):
    slots_data = scheduler.get_available_slots(patient_id=patient_id, limit=limit)
    if "error" in slots_data:
        raise HTTPException(status_code=404, detail=slots_data["error"])
    return slots_data

@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    try:
        result = chatbot.chat(
            message=req.message,
            patient_id=req.patient_id,
            conversation_history=req.conversation_history,
            api_key=req.api_key,
            provider=req.provider
        )
        return result
    except Exception as e:
        logger.error(f"Error handling chat request: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/appointments/schedule", response_model=BookingResponse)
def schedule_appointment(req: BookingRequest):
    result = scheduler.book_appointment(
        patient_id=req.patient_id,
        appointment_date=req.appointment_date,
        appointment_time=req.appointment_time,
        reason=req.reason,
        care_gap_addressed=req.care_gap_addressed
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    
    # Refresh retriever and knowledge base
    retriever.refresh()
    return result

@app.get("/api/appointments")
def list_appointments(patient_id: Optional[str] = None):
    return {"appointments": scheduler.list_appointments(patient_id=patient_id)}

@app.delete("/api/appointments/{appointment_id}")
def cancel_appointment(appointment_id: str):
    res = scheduler.cancel_appointment(appointment_id)
    if not res.get("success"):
        raise HTTPException(status_code=404, detail=res.get("message"))
    retriever.refresh()
    return res

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.app:app", host="0.0.0.0", port=8000, reload=True)
