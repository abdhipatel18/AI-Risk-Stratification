"""
RAG-Powered Clinical Care & Appointment Scheduling Chatbot.
Supports Google Gemini, OpenAI, Groq, and a Built-in Local Semantic RAG Fallback.
"""

import os
import re
import json
import logging
from typing import List, Dict, Any, Optional

from src.rag.knowledge_base import KnowledgeBase
from src.rag.retriever import HybridRetriever
from src.rag.appointment_scheduler import AppointmentScheduler

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are CareNavigator AI, an intelligent clinical assistant for a patient risk stratification and scheduling system.
Your mission is to help patients and healthcare teams:
1. Understand clinical risk stratification scores and risk tiers (High Risk, Medium Risk, Lower Risk).
2. Explain open care gaps (e.g. HbA1c control, blood pressure, mammography, diabetic eye exam) and why addressing them is vital.
3. Guide patients to schedule appointments with their assigned primary care provider (PCP) within their clinically recommended timeframe:
   - High Risk: Schedule within 1 Month (urgent window: 1-14 days).
   - Medium Risk: Schedule within 2 Months (30-60 days).
   - Lower Risk: Schedule within 3 Months (routine 60-90 days).
4. Strictly enforce safety: If a patient mentions emergency symptoms (chest pain, severe breathlessness, stroke signs), tell them to seek immediate emergency care (911/emergency department).

Guidelines:
- Ground your answers strictly in the provided <clinical_context>.
- Be empathetic, clear, professional, and reassuring. Avoid medical jargon when speaking to patients.
- When suggesting appointment dates, only offer dates and times that match their risk timeframe and clinic availability.
"""

class ClinicalSchedulingChatbot:
    def __init__(
        self,
        knowledge_base: Optional[KnowledgeBase] = None,
        retriever: Optional[HybridRetriever] = None,
        scheduler: Optional[AppointmentScheduler] = None,
        default_provider: str = "auto"
    ):
        self.kb = knowledge_base or KnowledgeBase()
        self.retriever = retriever or HybridRetriever(self.kb)
        self.scheduler = scheduler or AppointmentScheduler()
        self.default_provider = default_provider

    def chat(
        self,
        message: str,
        patient_id: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        api_key: Optional[str] = None,
        provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main chat interaction function.
        Returns:
            {
                "response": str,
                "retrieved_docs": List[Dict],
                "suggested_slots": List[Dict],
                "booking_result": Optional[Dict],
                "patient_info": Optional[Dict],
                "provider_used": str
            }
        """
        history = conversation_history or []
        prov = provider or self.default_provider

        # 1. Detect or standardize Patient ID
        pid = patient_id
        if not pid:
            pid_match = re.search(r"\b(PAT-\d{4})\b", message, re.IGNORECASE)
            if pid_match:
                pid = pid_match.group(1).upper()

        patient_profile = self.kb.get_patient_profile(pid) if pid else None

        # 2. Check for Appointment Booking Intent in the message
        booking_result = self._check_and_handle_booking(message, pid, patient_profile)

        # 3. Retrieve relevant clinical documents
        retrieved_docs = self.retriever.retrieve(query=message, patient_id=pid, top_k=3)

        # 4. Fetch available slots if query asks about scheduling / appointment
        suggested_slots = []
        is_scheduling_intent = any(w in message.lower() for w in ["schedule", "appointment", "book", "date", "slot", "visit", "time", "doctor", "pcp"])
        if pid and (is_scheduling_intent or (patient_profile and patient_profile.get("has_scheduled_appointment") == 0)):
            slots_data = self.scheduler.get_available_slots(pid, limit=4)
            suggested_slots = slots_data.get("slots", [])

        # 5. Determine which LLM provider to invoke
        response_text = ""
        provider_used = "local_rag"

        # Check API Keys from parameter or environment
        gemini_key = api_key if (prov == "gemini" and api_key) else os.environ.get("GEMINI_API_KEY")
        openai_key = api_key if (prov == "openai" and api_key) else os.environ.get("OPENAI_API_KEY")
        groq_key = api_key if (prov == "groq" and api_key) else os.environ.get("GROQ_API_KEY")

        # Route to provider
        if (prov == "gemini" or (prov == "auto" and gemini_key)) and gemini_key:
            try:
                response_text = self._call_gemini(message, retrieved_docs, patient_profile, suggested_slots, booking_result, history, gemini_key)
                provider_used = "google_gemini"
            except Exception as e:
                logger.warning(f"Gemini API call failed, falling back to local RAG: {e}")

        elif (prov == "openai" or (prov == "auto" and openai_key)) and openai_key:
            try:
                response_text = self._call_openai(message, retrieved_docs, patient_profile, suggested_slots, booking_result, history, openai_key)
                provider_used = "openai"
            except Exception as e:
                logger.warning(f"OpenAI API call failed, falling back to local RAG: {e}")

        elif (prov == "groq" or (prov == "auto" and groq_key)) and groq_key:
            try:
                response_text = self._call_groq(message, retrieved_docs, patient_profile, suggested_slots, booking_result, history, groq_key)
                provider_used = "groq"
            except Exception as e:
                logger.warning(f"Groq API call failed, falling back to local RAG: {e}")

        # If no cloud LLM succeeded, use our Built-in Local RAG Generator
        if not response_text:
            response_text = self._generate_local_rag_response(message, retrieved_docs, patient_profile, suggested_slots, booking_result)
            provider_used = "local_rag"

        # If booking was just made, ensure KnowledgeBase is updated
        if booking_result and booking_result.get("success"):
            self.retriever.refresh()

        return {
            "response": response_text,
            "retrieved_docs": retrieved_docs,
            "suggested_slots": suggested_slots,
            "booking_result": booking_result,
            "patient_info": patient_profile,
            "provider_used": provider_used
        }

    def _check_and_handle_booking(self, message: str, patient_id: Optional[str], patient_profile: Optional[Dict]) -> Optional[Dict[str, Any]]:
        """Detects if message specifies a booking confirmation with date & time."""
        if not patient_id:
            return None

        msg = message.lower()
        if not any(w in msg for w in ["book", "confirm", "schedule me", "schedule for", "reserve", "take the slot"]):
            return None

        # Try to find date in YYYY-MM-DD format
        date_match = re.search(r"\b(202\d-\d{2}-\d{2})\b", message)
        
        # Try to find time in HH:MM AM/PM format
        time_match = re.search(r"\b(\d{1,2}:\d{2}\s*(?:am|pm)?)\b", message, re.IGNORECASE)

        if date_match and time_match:
            date_str = date_match.group(1)
            raw_time = time_match.group(1).upper()
            if "AM" not in raw_time and "PM" not in raw_time:
                # default to AM if before 12, PM otherwise
                raw_time = raw_time + " AM"

            return self.scheduler.book_appointment(
                patient_id=patient_id,
                appointment_date=date_str,
                appointment_time=raw_time,
                reason=patient_profile.get("primary_reason_for_prioritization") if patient_profile else None,
                care_gap_addressed=patient_profile.get("highest_priority_care_gap") if patient_profile else None
            )

        return None

    def _format_context(self, retrieved_docs: List[Dict], patient_profile: Optional[Dict], suggested_slots: List[Dict], booking_result: Optional[Dict]) -> str:
        ctx_parts = []
        if patient_profile:
            ctx_parts.append("### Patient Record Details:")
            ctx_parts.append(f"- Patient ID: {patient_profile.get('patient_id')}")
            ctx_parts.append(f"- Name: {patient_profile.get('first_name')} {patient_profile.get('last_name')}")
            ctx_parts.append(f"- Risk Category: {patient_profile.get('risk_category')} (Score: {patient_profile.get('calculated_risk_score')})")
            ctx_parts.append(f"- Recommended Window: {patient_profile.get('recommended_scheduling_window')}")
            ctx_parts.append(f"- Primary Care Provider: {patient_profile.get('primary_care_provider')} at {patient_profile.get('clinic')}")
            ctx_parts.append(f"- Reason for Prioritization: {patient_profile.get('primary_reason_for_prioritization')}")
            ctx_parts.append(f"- Open Care Gaps: {patient_profile.get('num_open_care_gaps')}, Highest Gap: {patient_profile.get('highest_priority_care_gap')}")
            ctx_parts.append(f"- Next Scheduled Appointment: {patient_profile.get('next_scheduled_appointment_date')}")

        if retrieved_docs:
            ctx_parts.append("\n### Retrieved Clinical Guidelines & Policies:")
            for d in retrieved_docs:
                ctx_parts.append(f"[{d['title']}]:\n{d['content']}")

        if suggested_slots:
            ctx_parts.append("\n### Available Appointment Slots:")
            for s in suggested_slots:
                ctx_parts.append(f"- {s['display']} with {s['provider']} at {s['clinic']}")

        if booking_result:
            ctx_parts.append(f"\n### Action Result: {booking_result.get('message')}")

        return "\n".join(ctx_parts)

    def _call_gemini(self, message: str, docs: List[Dict], patient: Optional[Dict], slots: List[Dict], booking: Optional[Dict], history: List[Dict], api_key: str) -> str:
        """Invokes Google Gemini via google-genai SDK."""
        from google import genai
        client = genai.Client(api_key=api_key)

        context_str = self._format_context(docs, patient, slots, booking)
        full_prompt = f"{SYSTEM_PROMPT}\n\n<clinical_context>\n{context_str}\n</clinical_context>\n\nUser Question: {message}"

        # Using gemini-2.0-flash or gemini-1.5-flash
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=full_prompt
            )
            return response.text
        except Exception:
            # Fallback to gemini-1.5-flash if 2.0-flash is unavailable
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=full_prompt
            )
            return response.text

    def _call_openai(self, message: str, docs: List[Dict], patient: Optional[Dict], slots: List[Dict], booking: Optional[Dict], history: List[Dict], api_key: str) -> str:
        """Invokes OpenAI GPT model."""
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        context_str = self._format_context(docs, patient, slots, booking)
        messages = [
            {"role": "system", "content": f"{SYSTEM_PROMPT}\n\n<clinical_context>\n{context_str}\n</clinical_context>"}
        ]
        for h in history[-4:]:
            messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})
        messages.append({"role": "user", "content": message})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.3
        )
        return response.choices[0].message.content

    def _call_groq(self, message: str, docs: List[Dict], patient: Optional[Dict], slots: List[Dict], booking: Optional[Dict], history: List[Dict], api_key: str) -> str:
        """Invokes Groq Llama-3 model."""
        from openai import OpenAI
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=api_key)

        context_str = self._format_context(docs, patient, slots, booking)
        messages = [
            {"role": "system", "content": f"{SYSTEM_PROMPT}\n\n<clinical_context>\n{context_str}\n</clinical_context>"}
        ]
        for h in history[-4:]:
            messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})
        messages.append({"role": "user", "content": message})

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.3
        )
        return response.choices[0].message.content

    def _generate_local_rag_response(
        self,
        message: str,
        docs: List[Dict],
        patient: Optional[Dict],
        slots: List[Dict],
        booking: Optional[Dict]
    ) -> str:
        """
        Offline / Built-in Local RAG Generator.
        Delivers deterministic, high-quality, clinical responses grounded in retrieved knowledge chunks.
        """
        q = message.lower()

        # 1. Booking Action Handled
        if booking:
            if booking.get("success"):
                return (
                    f"✅ **Appointment Confirmed!**\n\n"
                    f"Your appointment has been successfully scheduled:\n"
                    f"- **Appointment ID**: `{booking['appointment_id']}`\n"
                    f"- **Patient**: {booking['patient_name']} (ID: {booking['patient_id']})\n"
                    f"- **Doctor**: {booking['provider']}\n"
                    f"- **Clinic**: {booking['clinic']}\n"
                    f"- **Date & Time**: **{booking['appointment_date']} at {booking['appointment_time']}**\n"
                    f"- **Care Gap Addressed**: {booking['care_gap_addressed']}\n\n"
                    f"Please arrive 15 minutes before your scheduled time. If you require lab work, remember to follow pre-visit fasting instructions."
                )
            else:
                return f"⚠️ **Scheduling Update**: {booking.get('message')}"

        # 2. Red-Flag Emergency Triage
        emergency_words = ["chest pain", "shortness of breath", "severe dizzy", "stroke", "paralysis", "bleeding", "collapse"]
        if any(w in q for w in emergency_words):
            return (
                "🚨 **URGENT MEDICAL NOTICE**:\n\n"
                "The symptoms you described may indicate an acute medical emergency. "
                "**Please do NOT wait for an outpatient appointment.**\n\n"
                "- Call **911** (or your local emergency response) immediately.\n"
                "- Or proceed to the nearest Hospital Emergency Department right away."
            )

        # 3. Patient Specific Inquiry (Why High Risk / Care Gaps)
        if patient:
            name = f"{patient.get('first_name')} {patient.get('last_name')}"
            risk_tier = patient.get("risk_category", "Unknown")
            score = patient.get("calculated_risk_score", 0.0)
            window = patient.get("recommended_scheduling_window", "Schedule Within One Month")
            pcp = patient.get("primary_care_provider", "your primary care doctor")
            clinic = patient.get("clinic", "our clinic")
            reason = patient.get("primary_reason_for_prioritization", "Clinical follow-up")
            gaps = patient.get("num_open_care_gaps", 0)
            highest_gap = patient.get("highest_priority_care_gap", "None")

            # Risk inquiry
            if any(w in q for w in ["why", "risk", "level", "score", "category", "high risk", "tier"]):
                resp = [
                    f"Hello {name}, here is your clinical risk profile overview:\n",
                    f"- **Clinical Risk Tier**: **{risk_tier}** (Overall Risk Score: **{score:.1f}**)",
                    f"- **Primary Reason**: {reason}",
                    f"- **Open Care Gaps**: {gaps} gap(s) identified (Highest Priority: *{highest_gap}*)",
                    f"- **Recommended Outreach Window**: **{window}**",
                    f"- **Assigned Provider**: {pcp} at {clinic}\n"
                ]
                if "high" in risk_tier.lower():
                    resp.append("⚠️ Because of your **High Risk** status, clinical guidelines advise scheduling a comprehensive visit **within 1 month** (target: 1-14 days) to prevent complications and adjust medications.")
                elif "medium" in risk_tier.lower():
                    resp.append("ℹ️ As a **Medium Risk** patient, it is recommended to complete a follow-up **within 1 to 2 months** to review your care gaps and routine laboratory progress.")
                else:
                    resp.append("✅ You are currently in the **Lower Risk** category. A routine checkup is recommended **within 2 to 3 months**.")

                if slots:
                    resp.append("\n**Available Appointment Slots for You:**")
                    for s in slots[:3]:
                        resp.append(f"• **{s['date']} ({s['day']}) at {s['time']}** with {s['provider']}")
                    resp.append("\n*To book one of these slots, simply reply with: `Book <Date> at <Time>` (for example: `Book " + slots[0]['date'] + " at " + slots[0]['time'] + "`)*.")

                return "\n".join(resp)

            # Care Gap inquiry
            if any(w in q for w in ["care gap", "gap", "test", "hba1c", "blood pressure", "exam", "mammogram", "eye"]):
                resp = [
                    f"**Care Gap Information for {name}**:\n",
                    f"- **Open Care Gaps**: {gaps}",
                    f"- **Primary Care Gap**: **{highest_gap}**\n"
                ]
                # Look for matching protocol in retrieved docs
                for d in docs:
                    if d.get("category") == "care_gap_protocol":
                        resp.append(f"📋 **Clinical Protocol Guidelines**:\n{d['content']}\n")
                        break

                if slots:
                    resp.append(f"Would you like to schedule an appointment with **{pcp}** to complete your care gap review?")
                    resp.append(f"Earliest available slot: **{slots[0]['display']}**.")
                return "\n".join(resp)

            # Scheduling / Booking inquiry
            if any(w in q for w in ["schedule", "appointment", "book", "slot", "when", "time", "date"]):
                resp = [
                    f"📅 **Appointment Scheduling for {name} ({risk_tier})**:\n",
                    f"Based on your risk stratification, your recommended window is: **{window}**.\n"
                ]
                if patient.get("has_scheduled_appointment") == 1:
                    resp.append(f"ℹ️ You already have an appointment scheduled on **{patient.get('next_scheduled_appointment_date')}**.")
                    resp.append("If you need to reschedule or book an additional slot, here are available openings:\n")
                else:
                    resp.append(f"Here are the earliest available openings with **{pcp}** at **{clinic}**:\n")

                if slots:
                    for s in slots:
                        resp.append(f"• **{s['date']} ({s['day']}) at {s['time']}**")
                    resp.append("\n💬 *To confirm your slot, reply with: `Book <Date> at <Time>` (e.g. `Book " + slots[0]['date'] + " at " + slots[0]['time'] + "`)*.")
                else:
                    resp.append("No open slots found in the immediate window. Please contact the clinic coordinator directly.")

                return "\n".join(resp)

        # 4. General Queries (Clinic hours, general guidelines)
        if any(w in q for w in ["hour", "clinic", "location", "open", "time"]):
            for d in docs:
                if d.get("id") == "policy_clinics_hours":
                    return f"🏥 **Clinic Hours and Locations**:\n\n{d['content']}"

        # 5. Fallback Default using retrieved documents
        if docs:
            top_doc = docs[0]
            return (
                f"**CareNavigator Information** ({top_doc['title']}):\n\n"
                f"{top_doc['content']}\n\n"
                f"*Please let me know if you would like me to retrieve specific patient records or schedule an appointment!*"
            )

        return (
            "Hello! I am CareNavigator AI. I can help you review patient risk stratification, explain open care gaps, "
            "and schedule appointments tailored to clinical risk tiers.\n\n"
            "Please provide a Patient ID (such as `PAT-0001`) or ask a clinical question to get started."
        )
