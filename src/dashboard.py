import os
import pandas as pd
import streamlit as st
import plotly.express as px

def run_dashboard(data_file="data/output/patient_risk_prioritization_results.csv"):
    st.set_page_config(page_title="Patient Risk & Scheduling Dashboard", layout="wide", page_icon="🏥")

    st.title("🏥 AI-Based Patient Risk Stratification & Scheduling Prioritization")
    st.markdown("Interactive decision support dashboard for healthcare teams to prioritize patient outreach and scheduling.")

    if not os.path.exists(data_file):
        st.error(f"Processed dataset not found at '{data_file}'. Please run `python src/main.py` first to process data.")
        return

    df = pd.read_csv(data_file)

    # --- SIDEBAR FILTERS ---
    st.sidebar.header("🔍 Filter Patient Cohort")

    clinics = ["All"] + sorted(list(df["clinic"].dropna().unique()))
    selected_clinic = st.sidebar.selectbox("Clinic", clinics)

    providers = ["All"] + sorted(list(df["primary_care_provider"].dropna().unique()))
    selected_provider = st.sidebar.selectbox("Primary Care Provider", providers)

    payers = ["All"] + sorted(list(df["insurance_or_payer"].dropna().unique()))
    selected_payer = st.sidebar.selectbox("Insurance / Payer", payers)

    categories = ["All"] + sorted(list(df["risk_category"].dropna().unique()))
    selected_category = st.sidebar.selectbox("Risk Category", categories)

    windows = ["All"] + sorted(list(df["recommended_scheduling_window"].dropna().unique()))
    selected_window = st.sidebar.selectbox("Scheduling Window", windows)

    # Apply Filters
    df_filtered = df.copy()
    if selected_clinic != "All":
        df_filtered = df_filtered[df_filtered["clinic"] == selected_clinic]
    if selected_provider != "All":
        df_filtered = df_filtered[df_filtered["provider"] == selected_provider if "provider" in df_filtered else df_filtered["primary_care_provider"] == selected_provider]
    if selected_payer != "All":
        df_filtered = df_filtered[df_filtered["insurance_or_payer"] == selected_payer]
    if selected_category != "All":
        df_filtered = df_filtered[df_filtered["risk_category"] == selected_category]
    if selected_window != "All":
        df_filtered = df_filtered[df_filtered["recommended_scheduling_window"] == selected_window]

    # --- KPI SUMMARY CARDS ---
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Patients", len(df_filtered))
    col2.metric("High Risk", len(df_filtered[df_filtered["risk_category"] == "High Risk"]))
    col3.metric("Schedule 1-Month", len(df_filtered[df_filtered["recommended_scheduling_window"] == "Schedule Within One Month"]))
    col4.metric("Overdue Care Gaps", int(df_filtered["num_overdue_care_gaps"].sum()))
    col5.metric("Unscheduled High-Risk", len(df_filtered[(df_filtered["risk_category"] == "High Risk") & (df_filtered["has_scheduled_appointment"] == 0)]))

    st.markdown("---")

    # --- CHARTS ROW 1 ---
    row1_col1, row1_col2 = st.columns(2)

    with row1_col1:
        st.subheader("📊 Patients by Risk Category")
        fig_risk = px.pie(df_filtered, names="risk_category", hole=0.4, color="risk_category",
                          color_discrete_map={
                              "High Risk": "#E74C3C",
                              "Medium Risk": "#F39C12",
                              "Lower Risk": "#2ECC71",
                              "No Immediate Action or Already Scheduled": "#3498DB"
                          })
        st.plotly_chart(fig_risk, use_container_width=True)

    with row1_col2:
        st.subheader("📅 Recommended Scheduling Windows")
        fig_sched = px.bar(df_filtered, x="recommended_scheduling_window", color="recommended_scheduling_window",
                           text_auto=True, color_discrete_sequence=px.colors.qualitative.Bold)
        fig_sched.update_layout(xaxis_title="", yaxis_title="Patient Count", showlegend=False)
        st.plotly_chart(fig_sched, use_container_width=True)

    # --- CHARTS ROW 2 ---
    row2_col1, row2_col2 = st.columns(2)

    with row2_col1:
        st.subheader("🏥 Risk Distribution by Clinic")
        fig_clinic = px.histogram(df_filtered, x="clinic", color="risk_category", barmode="group",
                                  color_discrete_map={"High Risk": "#E74C3C", "Medium Risk": "#F39C12", "Lower Risk": "#2ECC71"})
        fig_clinic.update_layout(xaxis_title="", yaxis_title="Count")
        st.plotly_chart(fig_clinic, use_container_width=True)

    with row2_col2:
        st.subheader("⚠️ High Risk Patients Without Appointment")
        high_no_appt = df_filtered[(df_filtered["risk_category"] == "High Risk") & (df_filtered["has_scheduled_appointment"] == 0)]
        if not high_no_appt.empty:
            st.dataframe(high_no_appt[["patient_id", "first_name", "last_name", "clinic", "primary_care_provider", "calculated_risk_score", "highest_priority_care_gap", "primary_reason_for_prioritization"]], use_container_width=True)
        else:
            st.success("No un-scheduled high-risk patients in selected filter view!")

    # --- PATIENT DETAIL TABLE ---
    st.subheader("📋 Patient Priority Master List")
    st.dataframe(df_filtered, use_container_width=True)

if __name__ == "__main__":
    run_dashboard()
