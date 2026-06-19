# Northstar Sign - Enterprise Document Workflow SaaS

Northstar Sign is a high-fidelity, full-stack document signature platform designed for secure organizational workflows. Built with a focus on **security, scale, and visual precision**, it provides a "Cozy Premium" experience for managing legally-binding signatures.

**Built from scratch with zero boilerplate.**

---

## 🏢 Interactive Corporate Demo
The project includes a pre-configured corporate environment for **Northstar Technologies Pvt. Ltd.**, featuring over 12 months of organic activity.

| Role | Credentials | Access Level |
| :--- | :--- | :--- |
| **Manager** | `pranali@northstar-tech.com` / `northstar2025` | Document Creation, Workflow Management |
| **Administrator** | `admin@northstar-tech.com` / `admin123` | Global Audit, Metrics, System Health |

> **Quick Start:** Run `python scripts/seed_demo_data.py` to reset the dashboard to its "lived-in" corporate state.

---

## 🚀 Key Product Features

### 📄 Intelligent Document Lifecycle
*   **Visual Editor:** Responsive, percentage-based coordinate system for precise field placement on any PDF.
*   **Multi-Signer Support:** Atomic state machine managing `PENDING` -> `PARTIALLY_SIGNED` -> `COMPLETED` transitions.
*   **Final PDF Engine:** High-fidelity server-side PDF generation with dynamic signature overlays.
*   **Rejection & Expiration:** Robust handling of business edge cases with automated owner notifications.

### 🛡️ Security & Engineering Maturity
*   **Identity Isolation:** Dual-portal architecture strictly separating Admin oversight from User workflows.
*   **Token Hardening:** One-way SHA-256 hashing for all signing tokens; single-use "burn" logic.
*   **Audit Trail:** Immutable, searchable ledger of every system event for compliance.
*   **Resilient Infrastructure:** Rate limiting, secure headers, and transaction-safe background jobs.

---

## 🛠️ Technology Stack

### Backend (The Engine)
*   **FastAPI:** High-performance asynchronous framework.
*   **PostgreSQL + SQLAlchemy:** Robust relational storage with asyncpg drivers.
*   **Alembic:** Precise schema versioning and migrations.
*   **ReportLab & PyPDF:** Advanced PDF processing and coordinate mapping.
*   **APScheduler:** Reliable background jobs for reminders and cleanups.

### Frontend (The Experience)
*   **Next.js (App Router):** Modern React architecture.
*   **Tailwind CSS:** "Cozy Premium" design system using Stone/Navy/Emerald palettes.
*   **Zustand:** Centralized state management for auth and editor contexts.
*   **React-PDF:** Interactive document rendering and field annotation.

---

## 📦 Local Installation

### Prerequisites
*   Python 3.12+
*   Node.js 20+
*   PostgreSQL 16+

### 1. Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python scripts/seed_demo_data.py
uvicorn app.main:app --reload
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## 📜 Architectural Decisions
*   **Coordinate System:** Used percentage-based coordinates (0-100) instead of pixels to ensure signatures stay perfectly aligned regardless of the signer's device resolution.
*   **Token Security:** Signing links are high-entropy, hashed on the server, and never stored in plain text to prevent link hijacking.
*   **Portal Separation:** Implemented mandatory server-side role checks for the `/admin` routes to ensure zero privilege escalation.

---

## 📜 License
This project is for educational and portfolio purposes. All rights reserved.
