# INFRAPLUS — Infrastructure Project Monitoring, Risk Assessment & Analytics Platform

INFRAPLUS is a government-grade, enterprise-ready infrastructure monitoring platform designed to provide real-time visibility, deterministic mathematical risk scoring, and grounded generative AI intelligence across public capital projects.

---

## Architecture Overview

```
                          ┌─────────────────────────────┐
                          │   React 19 + TypeScript     │
                          │   Vite + Tailwind CSS UI    │
                          └──────────────┬──────────────┘
                                         │
                                         ▼ (HTTP / Bearer Tokens)
                          ┌─────────────────────────────┐
                          │   FastAPI Python Backend    │
                          │ Token Verification & APIs   │
                          └──────────────┬──────────────┘
                                         │
               ┌─────────────────────────┼─────────────────────────┐
               ▼                         ▼                         ▼
   ┌───────────────────────┐ ┌───────────────────────┐ ┌───────────────────────┐
   │ Firebase Realtime DB  │ │  Python Risk Engine   │ │     Google Gemini     │
   │  Production Truth     │ │   Deterministic Math  │ │ Grounded Intelligence │
   └───────────────────────┘ └───────────────────────┘ └───────────────────────┘
               │
               ▼
   ┌───────────────────────┐
   │ Cloud Document Storage│
   │  Firebase / Storage   │
   └───────────────────────┘
```

---

## Core Technologies

### Frontend
- **Framework**: React 19, TypeScript, Vite
- **Styling & Motion**: Tailwind CSS v4, Framer Motion, Lucide Icons
- **Data Visualizations**: Recharts (Pie/Donut charts, Horizontal/Vertical bar charts)
- **Routing**: React Router DOM (v7) with `ProtectedRoute` and `GuestRoute`
- **Authentication**: Firebase Authentication SDK (Email Verification, Password Reset)

### Backend
- **Framework**: Python 3.14, FastAPI, Pydantic v2
- **Server**: Uvicorn ASGI
- **Database Connector**: Firebase Admin SDK & Firebase Realtime Database REST client
- **AI Intelligence**: `google-genai` SDK with strict grounded prompt engineering and deterministic fallback
- **Risk Engine**: Deterministic Python mathematical engine (single source of truth)

---

## Deterministic Risk Engine Formula

The Python Risk Engine is the single source of truth for risk calculations. Gemini **never** calculates or overrides the official risk score:

1. **Progress Risk (35% Weight)**:
   $$\text{gap} = \text{planned\_progress} - \text{progress}$$
   $$\text{progress\_risk} = \text{clamp}(\max(\text{gap}, 0) \times 2.5)$$

2. **Delay Risk (40% Weight)**:
   $$\text{delay\_risk} = \text{clamp}\left(\frac{\text{delay\_days}}{90} \times 100\right)$$

3. **Budget Risk (25% Weight)**:
   $$\text{spend\_ahead} = \max(\text{budget\_used} - \text{progress}, 0)$$
   $$\text{budget\_risk} = \text{clamp}(0.55 \times \text{budget\_used} + 0.45 \times \text{spend\_ahead})$$

4. **Composite Overall Score**:
   $$\text{overall\_score} = \text{clamp}(0.35 \times \text{progress\_risk} + 0.40 \times \text{delay\_risk} + 0.25 \times \text{budget\_risk})$$

5. **Risk Classification**:
   - **HIGH RISK**: Score $\ge 70$
   - **MEDIUM RISK**: Score $\ge 40$
   - **LOW RISK**: Score $< 40$

---

## Project Structure

```
FINAL/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── chat.py             # Grounded AI Assistant (POST /api/ai/chat)
│   │   │   ├── dashboard.py        # Executive Summary (GET /api/dashboard)
│   │   │   ├── health.py           # Health Check (GET /health)
│   │   │   ├── projects.py         # Project 360 & Listings (GET /projects, /projects/{id}/*)
│   │   │   └── storage.py          # Document Upload & Storage (POST /projects/{id}/documents/upload)
│   │   ├── core/
│   │   │   └── security.py         # Server-side Firebase ID token verification
│   │   ├── models/
│   │   │   ├── ai.py               # ChatRequest, ChatResponse, ProjectRiskSummary
│   │   │   ├── dashboard.py        # DashboardSummary, RiskDistribution, EarlyWarning
│   │   │   └── project.py          # ProjectRecord, RiskBreakdown, FinancialMetrics, etc.
│   │   ├── services/
│   │   │   ├── dashboard_service.py # Dynamic KPI aggregation from RTDB
│   │   │   ├── firebase_service.py  # Realtime Database client (Admin SDK & REST)
│   │   │   ├── gemini_service.py    # Grounded Gemini explanation & actions
│   │   │   ├── project_service.py   # 360° analytics & data access
│   │   │   ├── prompt_builder.py    # Strict system instructions preventing hallucinations
│   │   │   ├── query_engine.py      # Domain query matching
│   │   │   ├── risk_engine.py       # Deterministic Python mathematical engine
│   │   │   └── storage_service.py   # Cloud document storage & validation
│   │   ├── config.py               # Environment configuration loader
│   │   └── main.py                 # FastAPI application & CORS
│   ├── data/
│   │   └── projects.json           # 11 sample projects (manual seed reference only)
│   ├── scripts/
│   │   └── seed_database.py        # Explicit developer manual utility (--confirm required)
│   ├── .env                        # Backend environment configuration
│   ├── .env.example                # Backend environment template
│   └── requirements.txt            # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── common/             # KpiCard, RiskBadge, EmptyState, ErrorState, Skeletons, Modal
│   │   │   ├── layout/             # Navbar, Sidebar, Footer, AppLayout, ProtectedRoute, GuestRoute
│   │   │   ├── project-detail/     # Overview, Financial, Progress, Timeline, Milestones, Agencies, Documents, RiskAi
│   │   │   └── projects/           # ProjectCard, ProjectTable, ProjectFilterBar
│   │   ├── context/
│   │   │   └── AuthContext.tsx     # Firebase Auth, Email Verification, Session Management
│   │   ├── pages/
│   │   │   ├── LandingPage.tsx     # Futuristic Government Enterprise Showcase
│   │   │   ├── LoginPage.tsx       # Secure Officer Sign In
│   │   │   ├── SignupPage.tsx      # Officer Account Registration
│   │   │   ├── VerifyEmailPage.tsx # Enforced Email Verification Gateway
│   │   │   ├── ForgotPasswordPage.tsx
│   │   │   ├── DashboardPage.tsx   # Executive Monitoring Command Center
│   │   │   ├── ProjectsPage.tsx    # Project Explorer with Search, Filters, Grid/Table
│   │   │   ├── ProjectDetailPage.tsx # Project 360° Deep Dive
│   │   │   ├── RiskEnginePage.tsx  # Formula Transparency & Live Audit Matrix
│   │   │   ├── AiAssistantPage.tsx # Grounded Gemini Intelligence Hub
│   │   │   └── NotFoundPage.tsx
│   │   ├── services/
│   │   │   ├── api.ts              # Centralized API client with Auth Bearer tokens
│   │   │   └── firebase.ts         # Firebase Web App client initialization
│   │   ├── types/
│   │   │   └── index.ts            # Full TypeScript interface definitions
│   │   ├── App.tsx                 # Application Routes & Providers
│   │   ├── index.css               # Modern CSS tokens & accessibility
│   │   └── main.tsx
│   ├── .env                        # Frontend environment configuration
│   ├── .env.example
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
└── SIH26103 AI/                    # Authoritative AI prototype asset (fully preserved)
```

---

## Configuration & Environment Variables

### Backend (`backend/.env`)

```env
# Gemini API Key (Required for AI explanations)
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.6-flash

# Firebase Realtime Database URL (Sole production data source)
FIREBASE_DATABASE_URL=https://your-project-id-default-rtdb.firebaseio.com/

# Optional Service Account Key (path or raw JSON)
FIREBASE_SERVICE_ACCOUNT_KEY=path/to/serviceAccountKey.json

# Server Configuration
PORT=8000
HOST=127.0.0.1
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

### Frontend (`frontend/.env`)

```env
VITE_API_BASE_URL=http://localhost:8000

# Firebase Web App Credentials (from Firebase Console -> Project Settings)
VITE_FIREBASE_API_KEY=your_firebase_web_api_key
VITE_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
VITE_FIREBASE_DATABASE_URL=https://your_project-default-rtdb.firebaseio.com
VITE_FIREBASE_PROJECT_ID=your_project_id
VITE_FIREBASE_STORAGE_BUCKET=your_project.firebasestorage.app
VITE_FIREBASE_MESSAGING_SENDER_ID=your_messaging_sender_id
VITE_FIREBASE_APP_ID=your_app_id
```

---

## Running the Platform

### 1. Backend

From the workspace root (`FINAL`):

```powershell
cd backend
& "..\SIH26103 AI\.venv\Scripts\python.exe" -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- API Interactive Docs: `http://127.0.0.1:8000/docs`
- Health Diagnostic Check: `http://127.0.0.1:8000/health`

### 2. Frontend

In a separate terminal:

```powershell
cd frontend
npm run dev
```

- Web Portal: `http://localhost:5173`

---

## Data Integrity & Database Governance

- **Sole Production Data Source**: Firebase Realtime Database is the **ONLY** production source of project data.
- **Reference Dataset**: `backend/data/projects.json` is strictly a development/reference dataset. It is **NEVER** used as a production fallback when Firebase is empty or unavailable.
- **Manual Developer Seeder**: `scripts/seed_database.py` is strictly a manual developer utility. It **NEVER** auto-runs, auto-seeds, or silently creates projects. It requires the explicit `--confirm` CLI flag:
  ```powershell
  cd backend
  & "..\SIH26103 AI\.venv\Scripts\python.exe" scripts/seed_database.py --confirm
  ```
- **Empty States**: If Firebase Realtime Database is connected but contains 0 project records, the platform renders professional empty states across all screens (0 KPI values, empty arrays; **no fake/synthetic data**).
- **Error States**: If Firebase is unconfigured or unreachable, endpoints return HTTP 503 and the UI renders actionable error screens with retry buttons.

---

## Authentication & Security Workflow

1. **Sign Up**: Officer registers with official name, email, department, and password.
2. **Email Verification**: Firebase dispatches a verification link. Unverified accounts are strictly gated at `/verify-email`.
3. **Session Verification**: The frontend attaches the Firebase Bearer ID token to all outbound API requests.
4. **Backend Authorization**: FastAPI validates the token via Firebase Admin SDK.
5. **Data Protection**: Secrets (Gemini keys, Firebase Admin credentials) remain strictly on the backend and are never exposed to the client.
