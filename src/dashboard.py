"""
Streamlit Web Application:
1. Patient Risk Stratification & Prioritization Analytics Dashboard
2. RAG-Powered AI CareNavigator & Appointment Scheduling Chatbot
3. Confirmed Appointments Master Schedule
"""

import os
import sys
import pandas as pd
import streamlit as st
import plotly.express as px

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.rag.knowledge_base import KnowledgeBase
from src.rag.retriever import HybridRetriever
from src.rag.appointment_scheduler import AppointmentScheduler
from src.rag.chatbot import ClinicalSchedulingChatbot

@st.cache_resource
def get_chatbot_components(data_file="data/output/patient_risk_prioritization_results.csv"):
    kb = KnowledgeBase(patient_data_file=data_file)
    retriever = HybridRetriever(kb)
    scheduler = AppointmentScheduler(results_file=data_file)
    bot = ClinicalSchedulingChatbot(knowledge_base=kb, retriever=retriever, scheduler=scheduler)
    return kb, retriever, scheduler, bot

def run_dashboard(data_file="data/output/patient_risk_prioritization_results.csv"):
    st.set_page_config(
        page_title="AI Patient Risk & Scheduling System",
        layout="wide",
        page_icon="🏥",
        initial_sidebar_state="expanded"
    )

    st.title("🏥 AI-Based Patient Risk Stratification & Scheduling System")
    st.markdown("Decision support analytics, clinical care gap tracking, and RAG-powered appointment scheduling.")

    if not os.path.exists(data_file):
        st.error(f"Processed dataset not found at '{data_file}'. Please run `python src/main.py` first to process data.")
        return

    # Load components
    kb, retriever, scheduler, bot = get_chatbot_components(data_file)
    df = pd.read_csv(data_file)

    # --- SIDEBAR CONFIGURATION ---
    st.sidebar.title("⚙️ System Settings")

    llm_provider = st.sidebar.selectbox(
        "AI Chatbot LLM Provider",
        ["Auto / Built-in Local RAG (Zero API Key)", "Google Gemini", "OpenAI", "Groq"]
    )

    api_key_input = ""
    provider_code = "local"

    if "Gemini" in llm_provider:
        provider_code = "gemini"
        api_key_input = st.sidebar.text_input(
            "Gemini API Key",
            value=os.environ.get("GEMINI_API_KEY", ""),
            type="password",
            help="Get your key at https://aistudio.google.com/app/apikey"
        )
    elif "OpenAI" in llm_provider:
        provider_code = "openai"
        api_key_input = st.sidebar.text_input(
            "OpenAI API Key",
            value=os.environ.get("OPENAI_API_KEY", ""),
            type="password",
            help="Get your key at https://platform.openai.com/api-keys"
        )
    elif "Groq" in llm_provider:
        provider_code = "groq"
        api_key_input = st.sidebar.text_input(
            "Groq API Key",
            value=os.environ.get("GROQ_API_KEY", ""),
            type="password",
            help="Get your key at https://console.groq.com/keys"
        )
    else:
        provider_code = "local"
        st.sidebar.info("💡 Built-in semantic RAG engine is active. Runs 100% offline with zero external API key needed!")

    st.sidebar.markdown("---")

    # --- MAIN NAVIGATION TABS ---
    tab_analytics, tab_chatbot, tab_appointments = st.tabs([
        "📊 Risk Stratification Analytics",
        "🤖 AI CareNavigator Chatbot & Scheduling",
        "📅 Confirmed Appointments Master Schedule"
    ])

    # =========================================================================
    # TAB 1: ANALYTICS DASHBOARD
    # =========================================================================
    with tab_analytics:
        st.sidebar.header("🔍 Cohort Filter")
        clinics = ["All"] + sorted(list(df["clinic"].dropna().unique()))
        selected_clinic = st.sidebar.selectbox("Filter Clinic", clinics)

        providers = ["All"] + sorted(list(df["primary_care_provider"].dropna().unique()))
        selected_provider = st.sidebar.selectbox("Filter PCP", providers)

        payers = ["All"] + sorted(list(df["insurance_or_payer"].dropna().unique()))
        selected_payer = st.sidebar.selectbox("Filter Payer", payers)

        categories = ["All"] + sorted(list(df["risk_category"].dropna().unique()))
        selected_category = st.sidebar.selectbox("Filter Risk Category", categories)

        windows = ["All"] + sorted(list(df["recommended_scheduling_window"].dropna().unique()))
        selected_window = st.sidebar.selectbox("Filter Scheduling Window", windows)

        # Apply Filters
        df_filtered = df.copy()
        if selected_clinic != "All":
            df_filtered = df_filtered[df_filtered["clinic"] == selected_clinic]
        if selected_provider != "All":
            df_filtered = df_filtered[df_filtered["primary_care_provider"] == selected_provider]
        if selected_payer != "All":
            df_filtered = df_filtered[df_filtered["insurance_or_payer"] == selected_payer]
        if selected_category != "All":
            df_filtered = df_filtered[df_filtered["risk_category"] == selected_category]
        if selected_window != "All":
            df_filtered = df_filtered[df_filtered["recommended_scheduling_window"] == selected_window]

        # KPI Metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total Patients", len(df_filtered))
        col2.metric("High Risk", len(df_filtered[df_filtered["risk_category"] == "High Risk"]))
        col3.metric("Schedule 1-Month", len(df_filtered[df_filtered["recommended_scheduling_window"] == "Schedule Within One Month"]))
        col4.metric("Overdue Care Gaps", int(df_filtered["num_overdue_care_gaps"].sum()))
        col5.metric("Unscheduled High-Risk", len(df_filtered[(df_filtered["risk_category"] == "High Risk") & (df_filtered["has_scheduled_appointment"] == 0)]))

        st.markdown("---")

        # Row 1 Charts
        r1_c1, r1_c2 = st.columns(2)
        with r1_c1:
            st.subheader("📊 Patients by Risk Category")
            fig_risk = px.pie(
                df_filtered,
                names="risk_category",
                hole=0.4,
                color="risk_category",
                color_discrete_map={
                    "High Risk": "#E74C3C",
                    "Medium Risk": "#F39C12",
                    "Lower Risk": "#2ECC71",
                    "No Immediate Action or Already Scheduled": "#3498DB"
                }
            )
            st.plotly_chart(fig_risk, use_container_width=True)

        with r1_c2:
            st.subheader("📅 Recommended Scheduling Windows")
            fig_sched = px.bar(
                df_filtered,
                x="recommended_scheduling_window",
                color="recommended_scheduling_window",
                text_auto=True,
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            fig_sched.update_layout(xaxis_title="", yaxis_title="Patient Count", showlegend=False)
            st.plotly_chart(fig_sched, use_container_width=True)

        # Row 2 Charts
        r2_c1, r2_c2 = st.columns(2)
        with r2_c1:
            st.subheader("🏥 Risk Distribution by Clinic")
            fig_clinic = px.histogram(
                df_filtered,
                x="clinic",
                color="risk_category",
                barmode="group",
                color_discrete_map={"High Risk": "#E74C3C", "Medium Risk": "#F39C12", "Lower Risk": "#2ECC71"}
            )
            fig_clinic.update_layout(xaxis_title="", yaxis_title="Count")
            st.plotly_chart(fig_clinic, use_container_width=True)

        with r2_c2:
            st.subheader("⚠️ High-Risk Patients Requiring Outreach")
            high_no_appt = df_filtered[(df_filtered["risk_category"] == "High Risk") & (df_filtered["has_scheduled_appointment"] == 0)]
            if not high_no_appt.empty:
                st.dataframe(
                    high_no_appt[["patient_id", "first_name", "last_name", "clinic", "primary_care_provider", "calculated_risk_score", "highest_priority_care_gap", "primary_reason_for_prioritization"]],
                    use_container_width=True
                )
            else:
                st.success("No un-scheduled high-risk patients in current filter view!")

        st.subheader("📋 Patient Priority Master List")
        st.dataframe(df_filtered, use_container_width=True)

    # =========================================================================
    # TAB 2: RAG CHATBOT & APPOINTMENT SCHEDULING
    # =========================================================================
    with tab_chatbot:
        st.subheader("🤖 AI CareNavigator: Clinical Guidance & Risk-Based Scheduling")
        st.caption("Ask questions regarding clinical risk factors, care gaps, clinic instructions, and book real-time appointments.")

        # Patient Selector Bar
        all_patients = kb.get_all_patients()
        patient_options = {
            f"{p['patient_id']} - {p['first_name']} {p['last_name']} [{p.get('risk_category', 'Unknown')}]": p['patient_id']
            for p in all_patients
        }
        
        c_pat_select, c_pat_status = st.columns([2, 1])
        with c_pat_select:
            selected_patient_label = st.selectbox("Select Patient Context:", list(patient_options.keys()))
            active_pid = patient_options[selected_patient_label]

        patient_profile = kb.get_patient_profile(active_pid)

        with c_pat_status:
            if patient_profile:
                risk_tier = patient_profile.get("risk_category", "Lower Risk")
                color = "red" if "High" in risk_tier else ("orange" if "Medium" in risk_tier else "green")
                st.markdown(f"### Priority: :{color}[{risk_tier}]")
                st.caption(f"Risk Score: **{patient_profile.get('calculated_risk_score', 0):.1f}** | Window: **{patient_profile.get('recommended_scheduling_window')}**")

        # Patient Info Card
        if patient_profile:
            with st.expander("👤 View Active Patient Clinical Profile & Care Gaps", expanded=False):
                p_col1, p_col2, p_col3 = st.columns(3)
                p_col1.markdown(f"**Name:** {patient_profile.get('first_name')} {patient_profile.get('last_name')}")
                p_col1.markdown(f"**Age / Gender:** {patient_profile.get('age')} / {patient_profile.get('gender')}")
                p_col1.markdown(f"**Insurance:** {patient_profile.get('insurance_or_payer')}")

                p_col2.markdown(f"**Clinic:** {patient_profile.get('clinic')}")
                p_col2.markdown(f"**Primary Care Doctor:** {patient_profile.get('primary_care_provider')}")
                p_col2.markdown(f"**Last Visit Date:** {patient_profile.get('last_visit_date')}")

                p_col3.markdown(f"**Open Care Gaps:** {patient_profile.get('num_open_care_gaps')} ({patient_profile.get('num_overdue_care_gaps')} overdue)")
                p_col3.markdown(f"**Top Care Gap:** {patient_profile.get('highest_priority_care_gap')}")
                appt_disp = f"✅ Scheduled for {patient_profile.get('next_scheduled_appointment_date')}" if patient_profile.get("has_scheduled_appointment") == 1 else "⚠️ Unscheduled"
                p_col3.markdown(f"**Appointment Status:** {appt_disp}")

        # Live Appointment Slot Booking Widget
        st.markdown("#### 📅 Risk-Prioritized Scheduling Options")
        slots_data = scheduler.get_available_slots(active_pid, limit=6)
        slots_list = slots_data.get("slots", [])

        if slots_list:
            slot_choices = [s["display"] for s in slots_list]
            c_slot, c_book_btn = st.columns([3, 1])
            with c_slot:
                chosen_slot_display = st.selectbox("Recommended Slots matching clinical timeframe:", slot_choices, key="slot_picker")
            with c_book_btn:
                st.write("") # spacing
                if st.button("📌 Confirm & Book Slot", type="primary", use_container_width=True):
                    # Find chosen slot details
                    matched_slot = next(s for s in slots_list if s["display"] == chosen_slot_display)
                    book_res = scheduler.book_appointment(
                        patient_id=active_pid,
                        appointment_date=matched_slot["date"],
                        appointment_time=matched_slot["time"],
                        reason=patient_profile.get("primary_reason_for_prioritization") if patient_profile else None,
                        care_gap_addressed=patient_profile.get("highest_priority_care_gap") if patient_profile else None
                    )
                    if book_res and book_res.get("success"):
                        st.success(f"🎉 {book_res['message']} (ID: `{book_res['appointment_id']}`)")
                        retriever.refresh()
                        st.rerun()
                    else:
                        st.error(book_res.get("message") if book_res else "Failed to book appointment.")
        else:
            st.info("No open slots found for this patient.")

        st.markdown("---")

        # Chat Message History in Session State
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": (
                        "Hello! I am **CareNavigator AI**. I can explain your clinical risk stratification, "
                        "review your open care gaps (like blood pressure or HbA1c tests), and schedule appointments "
                        "with your primary care physician according to your risk window.\n\n"
                        "How can I assist you today?"
                    )
                }
            ]

        # Quick Action Buttons
        st.markdown("**Quick Inquiries:**")
        q1, q2, q3, q4 = st.columns(4)
        quick_query = None
        if q1.button("🔴 Why am I High Risk?", use_container_width=True):
            quick_query = "Why am I categorized in this risk tier?"
        if q2.button("📋 What Care Gaps do I have?", use_container_width=True):
            quick_query = "What care gaps and tests do I need to complete?"
        if q3.button("📅 When should I schedule?", use_container_width=True):
            quick_query = "What appointment slots are available for my risk level?"
        if q4.button("🏥 Clinic hours & preparation", use_container_width=True):
            quick_query = "What are the clinic hours and pre-appointment instructions?"

        # Display Chat History
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Input from Chat Box or Quick Prompt
        user_input = st.chat_input("Ask a clinical question or type 'Book <date> at <time>'...")
        final_prompt = quick_query or user_input

        if final_prompt:
            # Append user message
            st.session_state.messages.append({"role": "user", "content": final_prompt})
            with st.chat_message("user"):
                st.markdown(final_prompt)

            # Generate Assistant Response
            with st.chat_message("assistant"):
                with st.spinner("CareNavigator is retrieving clinical records & analyzing risk..."):
                    chat_res = bot.chat(
                        message=final_prompt,
                        patient_id=active_pid,
                        conversation_history=st.session_state.messages,
                        api_key=api_key_input,
                        provider=provider_code
                    )

                    st.markdown(chat_res["response"])
                    st.caption(f"Engine: `{chat_res['provider_used']}`")

                    # If RAG retrieved documents, show source accordion
                    if chat_res.get("retrieved_docs"):
                        with st.expander("📚 Retrieved Clinical Guidelines & Policy Chunks", expanded=False):
                            for doc in chat_res["retrieved_docs"]:
                                st.markdown(f"**{doc['title']}** (Relevance: `{doc['score']:.2f}`)")
                                st.text(doc["content"])

            st.session_state.messages.append({"role": "assistant", "content": chat_res["response"]})

            # If an appointment was booked via chat, reload
            booking_info = chat_res.get("booking_result")
            if booking_info and booking_info.get("success"):
                st.balloons()
                st.rerun()

    # =========================================================================
    # TAB 3: CONFIRMED APPOINTMENTS MASTER SCHEDULE
    # =========================================================================
    with tab_appointments:
        st.subheader("📅 Confirmed Appointments Master Schedule")
        st.caption("Live appointment registry managed by the AI scheduling engine.")

        appts = scheduler.load_appointments()
        if appts:
            df_appts = pd.DataFrame(appts)
            
            # Summary metrics
            a_col1, a_col2, a_col3 = st.columns(3)
            a_col1.metric("Total Bookings", len(df_appts))
            a_col2.metric("Confirmed Bookings", len(df_appts[df_appts["status"] == "Confirmed"]))
            a_col3.metric("High-Risk Bookings", len(df_appts[df_appts["risk_category"] == "High Risk"]) if "risk_category" in df_appts else 0)

            st.dataframe(df_appts, use_container_width=True)

            # Cancellation tool
            st.markdown("#### 🗑️ Manage / Cancel Appointment")
            confirmed_ids = df_appts[df_appts["status"] == "Confirmed"]["appointment_id"].tolist()
            if confirmed_ids:
                c_sel, c_btn = st.columns([2, 1])
                with c_sel:
                    target_id = st.selectbox("Select Appointment to Cancel:", confirmed_ids)
                with c_btn:
                    st.write("")
                    if st.button("Cancel Appointment", type="secondary"):
                        cancel_res = scheduler.cancel_appointment(target_id)
                        if cancel_res.get("success"):
                            st.warning(cancel_res["message"])
                            retriever.refresh()
                            st.rerun()
                        else:
                            st.error(cancel_res.get("message"))
        else:
            st.info("No appointments currently booked. Use Tab 2 to schedule an appointment for any patient!")

if __name__ == "__main__":
    run_dashboard()
