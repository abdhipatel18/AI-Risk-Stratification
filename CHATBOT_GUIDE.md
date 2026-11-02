# 🤖 AI CareNavigator RAG Chatbot & Appointment Scheduling Guide

This guide walks you through the **Retrieval-Augmented Generation (RAG) Chatbot** and **Risk-Prioritized Appointment Scheduling Engine** integrated into your Patient Risk Stratification system.

---

## 🌟 Features Overview

1. **RAG Clinical Knowledge Retrieval**:
   - Ingests and indexes:
     - Complete patient EHR profiles (risk category, risk score, open/overdue care gaps, critical labs, active medications).
     - Clinical care gap protocols (`CG001` - `CG010`, including HbA1c control, uncontrolled hypertension, diabetic retinopathy eye exams, etc.).
     - Hospital risk stratification policies and triage protocols.
     - Clinic locations, PCP directory, and standard operating hours.
2. **Clinical Risk-Tier Scheduling**:
   - **High Risk**: Slots offered within **1 to 14 days** (urgent outreach within 1 month). Fasting morning slots prioritized for laboratory review.
   - **Medium Risk**: Slots offered within **15 to 45 days** (within 1-2 months).
   - **Lower Risk**: Routine wellness slots offered within **45 to 90 days** (within 2-3 months).
3. **Emergency Red-Flag Safety Filter**:
   - Automatically detects emergency symptoms (e.g., crushing chest pain, sudden numbness, severe difficulty breathing) and immediately instructs the patient to call emergency services (**911**) rather than booking an outpatient slot.
4. **Interactive Streamlit Web Chatbot**:
   - Built into the dashboard (`src/dashboard.py`) with patient profile cards, quick action inquiry pills, interactive slot picker, and real-time appointment booking.
5. **High-Performance FastAPI REST Backend**:
   - Clean endpoints for mobile apps, frontend web widgets, and EHR integration.
6. **Multi-Provider LLM Support**:
   - **Google Gemini** (Gemini 2.0 / 1.5)
   - **OpenAI** (GPT-4o-mini / GPT-4o)
   - **Groq** (Llama-3.1-8b / 3.3-70b)
   - **Built-in Local RAG Fallback**: Runs 100% offline without any API keys!

---

## 🔑 How to Get the Required API Keys

You can run the chatbot **immediately without any API key** using the built-in local semantic RAG engine. If you want to connect cloud LLMs, here is how to get each key:

### 1. Google Gemini API Key (Recommended - Free Tier Available)
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Sign in with your Google account.
3. Click **"Create API key"** and copy your generated key.
4. Set the environment variable in your terminal:
   ```powershell
   $env:GEMINI_API_KEY="your-gemini-api-key-here"
   ```
   *(Or paste it directly into the Streamlit sidebar field).*

### 2. OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys).
2. Sign in and click **"Create new secret key"**.
3. Set the environment variable:
   ```powershell
   $env:OPENAI_API_KEY="your-openai-api-key-here"
   ```

### 3. Groq API Key (Ultra-Fast & Free Tier Available)
1. Go to [Groq Console](https://console.groq.com/keys).
2. Sign in and click **"Create API Key"**.
3. Set the environment variable:
   ```powershell
   $env:GROQ_API_KEY="your-groq-api-key-here"
   ```

---

## 🖥️ How to Use the Streamlit Chatbot Interface

1. Start the Streamlit application:
   ```bash
   streamlit run src/dashboard.py
   ```
   *(Or run: `python src/main.py --dashboard`)*
2. In the web interface:
   - Navigate to **Tab 2: "🤖 AI CareNavigator Chatbot & Scheduling"**.
   - Select a patient (e.g. `PAT-0001 - Emily Smith [High Risk]`).
   - Click one of the quick inquiry buttons or type a question:
     - *"Why am I high risk?"*
     - *"What care gaps do I have?"*
     - *"When should I schedule?"*
     - *"What are the clinic hours?"*
   - To book an appointment, either:
     - Select a slot from the dropdown and click **"📌 Confirm & Book Slot"**, OR
     - Type in the chat: `Book 2026-11-03 at 09:00 AM`.
3. View booked appointments in **Tab 3: "📅 Confirmed Appointments Master Schedule"**.

---

## 🌐 FastAPI REST API Usage

### 1. Start the API Server
```bash
python src/main.py --api
```
*(Runs on `http://localhost:8000` with Swagger docs at `http://localhost:8000/docs`)*

### 2. Available Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Service health and total indexed patients |
| `GET` | `/api/patients` | Search & filter patients by clinic or risk tier |
| `GET` | `/api/patient/{id}` | Full patient clinical profile and risk metrics |
| `GET` | `/api/patient/{id}/slots` | Available appointment slots tailored to risk level |
| `POST` | `/api/chat` | Send a chat message, perform RAG, and get response |
| `POST` | `/api/appointments/schedule` | Direct appointment booking endpoint |
| `GET` | `/api/appointments` | List all scheduled appointments |
| `DELETE` | `/api/appointments/{id}` | Cancel / reschedule an appointment |

---

### 3. API Request Examples

#### A. Send a Chat Message (`POST /api/chat`)
```bash
curl -X POST "http://localhost:8000/api/chat" ^
  -H "Content-Type: application/json" ^
  -d "{\"message\": \"Why was I prioritized as high risk?\", \"patient_id\": \"PAT-0001\"}"
```

#### B. Get Risk-Tailored Available Slots (`GET /api/patient/{id}/slots`)
```bash
curl "http://localhost:8000/api/patient/PAT-0001/slots?limit=4"
```

#### C. Book an Appointment (`POST /api/appointments/schedule`)
```bash
curl -X POST "http://localhost:8000/api/appointments/schedule" ^
  -H "Content-Type: application/json" ^
  -d "{\"patient_id\": \"PAT-0001\", \"appointment_date\": \"2026-11-03\", \"appointment_time\": \"09:00 AM\", \"reason\": \"Urgent HbA1c Review\"}"
```

#### D. List Booked Appointments (`GET /api/appointments`)
```bash
curl "http://localhost:8000/api/appointments"
```

---

## 🧪 Automated Testing

To run the complete test suite (10 unit and integration tests):
```bash
pytest tests/
```
Output:
```
tests/test_data_loader.py ..       [20%]
tests/test_rag_chatbot.py ......   [80%]
tests/test_risk_engine.py .        [90%]
tests/test_scheduling_engine.py .   [100%]
10 passed in 2.28s
```
