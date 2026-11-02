"""
Demo script showcasing how the CareNavigator RAG Chatbot and Appointment Scheduler work.
"""

import sys
sys.stdout.reconfigure(encoding="utf-8")

from src.rag.knowledge_base import KnowledgeBase
from src.rag.retriever import HybridRetriever
from src.rag.appointment_scheduler import AppointmentScheduler
from src.rag.chatbot import ClinicalSchedulingChatbot

def run_demo():
    kb = KnowledgeBase()
    retriever = HybridRetriever(kb)
    scheduler = AppointmentScheduler()
    bot = ClinicalSchedulingChatbot(kb, retriever, scheduler)

    pid = "PAT-0001"
    patient = kb.get_patient_profile(pid)

    print("\n" + "=" * 75)
    print(f"🏥 ACTIVE PATIENT CONTEXT: {patient['first_name']} {patient['last_name']} (ID: {pid})")
    print(f"Risk Category: {patient['risk_category']} | Calculated Risk Score: {patient['calculated_risk_score']}")
    print(f"Assigned PCP:  {patient['primary_care_provider']} at {patient['clinic']}")
    print(f"Care Gaps:     {patient['num_open_care_gaps']} open ({patient['num_overdue_care_gaps']} overdue) | Top: {patient['highest_priority_care_gap']}")
    print("=" * 75)

    # Fetch initial available slots for this patient
    slots_info = scheduler.get_available_slots(pid, limit=3)
    first_slot = slots_info["slots"][0] if slots_info["slots"] else {"date": "2026-11-04", "time": "09:45 AM"}
    booking_command = f"Book {first_slot['date']} at {first_slot['time']}"

    interactions = [
        ("Step 1: Clinical Risk Inquiry", "Why was I assigned to the High Risk tier and what does it mean?"),
        ("Step 2: Care Gap & Preparation Inquiry", "What care gaps do I need to address, and how should I prepare for tests?"),
        ("Step 3: Risk-Based Scheduling Inquiry", "What appointment dates and times are available for my doctor?"),
        ("Step 4: Real-Time Appointment Booking", booking_command),
        ("Step 5: Emergency Safety Triage", "I have severe crushing chest pain and trouble breathing")
    ]

    for label, query in interactions:
        print(f"\n💬 [{label}]")
        print(f"Patient Prompt: \"{query}\"")
        res = bot.chat(query, patient_id=pid)
        print(f"🤖 CareNavigator AI (Engine: {res['provider_used']}):")
        print("-" * 65)
        print(res["response"])
        print("-" * 65)

if __name__ == "__main__":
    run_demo()
