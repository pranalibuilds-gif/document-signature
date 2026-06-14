# DocuSign Mini - Secure Document Signing SaaS

**Built from scratch with zero boilerplate.**

DocuSign Mini is a professional-grade, full-stack document signature platform designed for small to mid-sized organizations. It provides a seamless, secure, and legally-compliant workflow for managing document signatures, from initial creation to final PDF generation.

---

## 🏢 Corporate Demo Environment
The application comes with a pre-configured corporate dataset simulating **Northstar Technologies Pvt. Ltd.** with over 12 months of organic activity.

| Role | Email | Password |
| :--- | :--- | :--- |
| **Manager (User)** | `pranali@northstar-tech.com` | `northstar2025` |
| **System Admin** | `admin@northstar-tech.com` | `admin123` |

### Seeding the Demo Data
To reset the environment to its verified corporate state:
```bash
cd backend
$env:PYTHONPATH="."
python scripts/seed_demo_data.py
```

---

## 🚀 Key Features

### 📄 Document Lifecycle Management
*   **DRAFT:** Intuitive setup for document titles and metadata.
*   **PDF UPLOAD:** Secure handling and storage of original PDF documents.
*   **VISUAL EDITOR:** Drag-and-drop interactive interface for placing signature, text, and date fields using percentage-based coordinates for perfect responsiveness across all devices.
*   **REVIEW & ACTIVATE:** Final summary and validation before sending invitations.
*   **PENDING / PARTIAL:** Real-time tracking of signer progress.
*   **COMPLETED:** Automatic generation of final PDFs with high-fidelity signature overlays.

### ✍️ Signer Experience
*   **WELCOME TUNNEL:** Professional landing page clarifying the legal nature of electronic signatures.
*   **MOBILE-FIRST VIEWER:** Responsive PDF viewing and field interaction optimized for touch devices.
*   **PREMIUM SIGNATURES:** Choice of multiple high-end cursive and script fonts for a personal touch.

### 🛡️ Security & Compliance
*   **JWT AUTHENTICATION:** Secure session management with short-lived access tokens and rotated refresh tokens.
*   **TOKEN HASHING:** One-way SHA-256 hashing for all signing and reset tokens, ensuring they remain secure even if the database is accessed.
*   **AUDIT TRAIL:** Immutable record of every system event, including creation, views, signatures, and rejections.
*   **RATE LIMITING:** Granular protection against brute-force and abuse on sensitive endpoints.

### 💼 Admin & Oversight
*   **DASHBOARD METRICS:** High-level overview of system usage and document status distribution.
*   **USER MANAGEMENT:** Searchable directory of registered users and their verification status.
*   **GLOBAL AUDIT LOG:** Centralized compliance log for security monitoring.

## 🛠️ Technology Stack

### Backend
*   **FastAPI:** High-performance Python web framework.
*   **SQLAlchemy + asyncpg:** Asynchronous ORM for robust database interaction.
*   **PostgreSQL:** Relational database for metadata and audit storage.
*   **ReportLab & PyPDF:** Advanced PDF processing for coordinate calculation and overlays.
*   **APScheduler:** Automated cleanup and reminder jobs.

### Frontend
*   **Next.js (App Router):** React framework for modern web experiences.
*   **Zustand:** Lightweight state management for auth and editor contexts.
*   **Tailwind CSS:** "Cozy Premium" aesthetic using the latest Tailwind v4 features.
*   **React-PDF:** Interactive PDF rendering and coordinate mapping.
*   **Lucide React:** Consistent and professional iconography.

## 📦 Getting Started

### Prerequisites
*   Python 3.9+
*   Node.js 18+
*   PostgreSQL 14+

### Setup
1.  **Clone the repository:**
    ```bash
    git clone https://github.com/pranalibuilds-gif/document-signature.git
    cd document-signature
    ```

2.  **Backend Setup:**
    ```bash
    cd backend
    python -m venv .venv
    source .venv/bin/activate  # Or .venv\Scripts\activate on Windows
    pip install -r requirements.txt
    alembic upgrade head
    uvicorn app.main:app --reload
    ```

3.  **Frontend Setup:**
    ```bash
    cd frontend
    npm install
    npm run dev
    ```

## 📜 License
This project is for educational and portfolio purposes. All rights reserved.
