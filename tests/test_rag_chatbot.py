"""
Unit and Integration Tests for RAG Chatbot, Appointment Scheduler, and REST API.
"""

import os
import json
import pytest
from fastapi.testclient import TestClient

from src.rag.knowledge_base import KnowledgeBase
from src.rag.retriever import HybridRetriever
from src.rag.appointment_scheduler import AppointmentScheduler
from src.rag.chatbot import ClinicalSchedulingChatbot
from src.api.app import app

TEST_RESULTS_FILE = "data/output/patient_risk_prioritization_results.csv"

@pytest.fixture(scope="module")
def shared_components():
    kb = KnowledgeBase(patient_data_file=TEST_RESULTS_FILE)
    retriever = HybridRetriever(kb)
    scheduler = AppointmentScheduler(results_file=TEST_RESULTS_FILE)
    bot = ClinicalSchedulingChatbot(knowledge_base=kb, retriever=retriever, scheduler=scheduler)
    return kb, retriever, scheduler, bot

def test_knowledge_base_loading(shared_components):
    kb, _, _, _ = shared_components
    assert len(kb.documents) > 10
    patients = kb.get_all_patients()
    assert len(patients) > 0
    # Test profile retrieval
    first_pid = patients[0]["patient_id"]
    prof = kb.get_patient_profile(first_pid)
    assert prof is not None
    assert prof["patient_id"] == first_pid

def test_appointment_scheduler_slots(shared_components):
    _, _, scheduler, _ = shared_components
    slots_data = scheduler.get_available_slots("PAT-0001", limit=4)
    assert "slots" in slots_data
    assert len(slots_data["slots"]) == 4
    for slot in slots_data["slots"]:
        assert "date" in slot
        assert "time" in slot
        assert "provider" in slot
        assert "clinic" in slot

def test_appointment_booking_and_cancellation(shared_components):
    _, _, scheduler, _ = shared_components
    # Book a test slot
    test_pid = "PAT-0002"
    slots = scheduler.get_available_slots(test_pid, limit=1)["slots"]
    assert len(slots) > 0
    target_date = slots[0]["date"]
    target_time = slots[0]["time"]

    booking = scheduler.book_appointment(
        patient_id=test_pid,
        appointment_date=target_date,
        appointment_time=target_time,
        reason="Test booking",
        care_gap_addressed="Routine Check"
    )
    assert booking["success"] is True
    appt_id = booking["appointment_id"]
    assert appt_id.startswith("APT-")

    # Duplicate booking prevention test
    dup_booking = scheduler.book_appointment(
        patient_id=test_pid,
        appointment_date=target_date,
        appointment_time=target_time
    )
    assert dup_booking["success"] is False

    # List appointments test
    active_appts = scheduler.list_appointments(patient_id=test_pid)
    assert any(a["appointment_id"] == appt_id for a in active_appts)

    # Cancel appointment test
    cancel_res = scheduler.cancel_appointment(appt_id)
    assert cancel_res["success"] is True

def test_hybrid_retriever(shared_components):
    _, retriever, _, _ = shared_components
    # Test care gap retrieval
    docs = retriever.retrieve("HbA1c blood glucose level protocol", top_k=2)
    assert len(docs) > 0
    assert any("CG001" in d["title"] or "HbA1c" in d["content"] for d in docs)

    # Test emergency prioritization
    em_docs = retriever.retrieve("I have severe acute chest pain and dizziness", top_k=2)
    assert len(em_docs) > 0
    assert any("Emergency" in em_docs[0]["title"] or "emergency" in em_docs[0]["content"].lower() for em_docs in [em_docs])

def test_chatbot_local_rag(shared_components):
    _, _, _, bot = shared_components
    # 1. Ask about risk
    res_risk = bot.chat("Why am I considered high risk?", patient_id="PAT-0001")
    assert "Risk" in res_risk["response"]
    assert res_risk["provider_used"] in ["local_rag", "google_gemini", "openai"]

    # 2. Emergency triage check
    res_em = bot.chat("I have severe crushing chest pain", patient_id="PAT-0001")
    assert "911" in res_em["response"] or "Emergency" in res_em["response"]

def test_fastapi_endpoints():
    client = TestClient(app)
    # Health check
    res_health = client.get("/api/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "healthy"

    # Patient list
    res_pats = client.get("/api/patients")
    assert res_pats.status_code == 200
    assert res_pats.json()["count"] > 0

    # Patient profile
    res_pat = client.get("/api/patient/PAT-0001")
    assert res_pat.status_code == 200
    assert res_pat.json()["patient_id"] == "PAT-0001"

    # Available slots
    res_slots = client.get("/api/patient/PAT-0001/slots?limit=3")
    assert res_slots.status_code == 200
    assert len(res_slots.json()["slots"]) == 3

    # Chat API
    res_chat = client.post("/api/chat", json={
        "message": "What is my recommended scheduling timeframe?",
        "patient_id": "PAT-0001"
    })
    assert res_chat.status_code == 200
    data = res_chat.json()
    assert "response" in data
    assert len(data["response"]) > 10
