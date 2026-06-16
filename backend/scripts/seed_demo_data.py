import asyncio
import uuid
import random
import os
from datetime import datetime, timedelta, timezone
from sqlalchemy import text
from reportlab.pdfgen import canvas

from app.core.database import AsyncSessionLocal
from app.core.security.hashing import hash_password
from app.common.enums import DocumentStatus, SignerStatus, UserRole, AuditActorType, AuditEventType, FieldType
from app.modules.users.models import User
from app.modules.documents.models import Document, DocumentFile
from app.modules.signers.models import DocumentSigner
from app.modules.fields.models import SignatureField
from app.modules.audit.models import AuditLog
from app.core.config import settings

COMPANY_NAME = "Northstar Technologies Pvt. Ltd."
COMPANY_DOMAIN = "northstar-tech.com"

# Realistic Employee Pool
EMPLOYEES = [
    ("Pranali", "More", "pranali@northstar-tech.com"),
    ("Sarah", "Johnson", "s.johnson@northstar-tech.com"),
    ("Michael", "Chen", "m.chen@northstar-tech.com"),
    ("Priya", "Sharma", "p.sharma@northstar-tech.com"),
    ("David", "Wilson", "d.wilson@northstar-tech.com"),
    ("Emily", "Davis", "e.davis@northstar-tech.com"),
    ("James", "Miller", "j.miller@northstar-tech.com"),
    ("Aarav", "Patel", "a.patel@northstar-tech.com"),
    ("Sophia", "Martinez", "s.martinez@northstar-tech.com"),
    ("Daniel", "Brown", "d.brown@northstar-tech.com"),
]

VENDORS = ["Global Logistics Inc.", "Azure Cloud Services", "Office Depot", "Green Energy Corp", "Swift Software Solutions"]

DOC_CATEGORIES = {
    "HR": [
        "Employment Agreement", "Offer Letter", "Internship Agreement", "NDA",
        "Employee Handbook Acknowledgement", "Remote Work Agreement", "Salary Revision Letter"
    ],
    "Procurement": [
        "Vendor Agreement", "Master Service Agreement", "Purchase Approval Form", "Equipment Procurement Request"
    ],
    "Finance": ["Expense Reimbursement", "Budget Approval Form", "Invoice Approval"],
    "Operations": ["Facility Access Request", "Asset Handover Form", "Laptop Allocation Form"],
    "Compliance": ["GDPR Consent", "Information Security Policy"],
    "Executive": ["Board Resolution", "Director Approval", "Strategic Approval Memo"]
}

def generate_mock_pdf(filename, title):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    c = canvas.Canvas(filename)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 780, COMPANY_NAME)
    c.setFont("Helvetica", 12)
    c.drawString(100, 760, title)
    c.line(100, 755, 500, 755)
    c.drawString(100, 730, f"Generated on: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}")
    c.drawString(100, 700, "This is a computer-generated document for Northstar internal use.")
    c.save()

async def seed():
    if settings.ENVIRONMENT == "production":
        print("CRITICAL: Seeding is disabled in production environment.")
        return

    async with AsyncSessionLocal() as session:
        print("--- NORTHSTAR TECHNOLOGIES SEED START ---")
        print("Step 1: Wiping previous data...")
        await session.execute(text("TRUNCATE TABLE field_values, signing_tokens, password_reset_tokens, email_verification_tokens, signature_fields, document_signers, document_files, audit_logs, notifications, refresh_tokens, documents, users CASCADE"))
        await session.commit()

        print("Step 2: Creating Accounts...")
        admin_pass = hash_password("admin123")
        user_pass = hash_password("northstar2025")

        # Root Admin
        admin = User(
            id=uuid.uuid4(),
            email="admin@northstar-tech.com",
            hashed_password=admin_pass,
            first_name="System",
            last_name="Administrator",
            role=UserRole.ADMIN,
            is_verified=True,
            created_at=datetime.now(timezone.utc) - timedelta(days=500)
        )
        session.add(admin)

        # Primary Demo Manager
        manager_id = uuid.uuid4()
        manager = User(
            id=manager_id,
            email="pranali@northstar-tech.com",
            hashed_password=user_pass,
            first_name="Pranali",
            last_name="More",
            role=UserRole.USER,
            is_verified=True,
            created_at=datetime.now(timezone.utc) - timedelta(days=450)
        )
        session.add(manager)
        await session.flush()

        print("Step 3: Generating 120 documents over 12 months...")
        total_docs = 120
        start_date = datetime.now(timezone.utc) - timedelta(days=365)

        # Track statistics for report
        stats = {"COMPLETED": 0, "PENDING": 0, "REJECTED": 0, "EXPIRED": 0, "DRAFT": 0}

        for i in range(total_docs):
            # Spread documents over the year
            created_at = start_date + timedelta(days=random.randint(0, 360), hours=random.randint(0, 23))

            # Weighted status distribution
            if (datetime.now(timezone.utc) - created_at).days < 7:
                status = random.choices([DocumentStatus.DRAFT, DocumentStatus.PENDING], weights=[30, 70])[0]
            else:
                status = random.choices(
                    [DocumentStatus.COMPLETED, DocumentStatus.PENDING, DocumentStatus.REJECTED, DocumentStatus.EXPIRED],
                    weights=[70, 15, 10, 5]
                )[0]

            stats[status.value] += 1

            category = random.choice(list(DOC_CATEGORIES.keys()))
            type_name = random.choice(DOC_CATEGORIES[category])
            title = f"{type_name} - {created_at.strftime('%b %Y')}"

            doc_id = uuid.uuid4()
            document = Document(
                id=doc_id,
                owner_id=manager_id,
                title=title,
                status=status,
                created_at=created_at,
                updated_at=created_at + timedelta(hours=random.randint(1, 48)),
                completed_at=created_at + timedelta(days=random.randint(1, 3)) if status == DocumentStatus.COMPLETED else None,
                expires_at=created_at + timedelta(days=30)
            )
            session.add(document)

            # File Generation
            stored_name = f"{doc_id}_orig.pdf"
            file_path = f"storage/original/{stored_name}"
            # In a real seed we'd actually generate the file, but for speed let's just create records
            # and make sure one "test" file actually exists physically.
            generate_mock_pdf(os.path.join("storage/original", stored_name), title)

            doc_file = DocumentFile(
                id=uuid.uuid4(),
                document_id=doc_id,
                file_name=f"{type_name.replace(' ', '_').lower()}.pdf",
                stored_name=stored_name,
                file_path=file_path,
                file_size=random.randint(50000, 250000),
                mime_type="application/pdf",
                is_final=False,
                created_at=created_at
            )
            session.add(doc_file)

            # Final signed file for completed ones
            if status == DocumentStatus.COMPLETED:
                final_name = f"{doc_id}_final.pdf"
                generate_mock_pdf(os.path.join("storage/final", final_name), f"SIGNED: {title}")
                final_file = DocumentFile(
                    id=uuid.uuid4(),
                    document_id=doc_id,
                    file_name=f"Signed_{doc_file.file_name}",
                    stored_name=final_name,
                    file_path=f"storage/final/{final_name}",
                    file_size=random.randint(60000, 300000),
                    mime_type="application/pdf",
                    is_final=True,
                    created_at=document.completed_at
                )
                session.add(final_file)

            # Signers
            num_signers = random.randint(1, 2)
            doc_signers = random.sample(EMPLOYEES[1:], num_signers)

            for s_info in doc_signers:
                signer_id = uuid.uuid4()
                s_status = SignerStatus.PENDING
                if status == DocumentStatus.COMPLETED:
                    s_status = SignerStatus.SIGNED
                elif status == DocumentStatus.REJECTED:
                    s_status = random.choice([SignerStatus.REJECTED, SignerStatus.PENDING])

                signer = DocumentSigner(
                    id=signer_id,
                    document_id=doc_id,
                    email=s_info[2],
                    status=s_status,
                    invited_at=created_at + timedelta(minutes=random.randint(5, 60)),
                    signed_at=document.completed_at if s_status == SignerStatus.SIGNED else None,
                    created_at=created_at
                )
                session.add(signer)

                # Signature Field
                field = SignatureField(
                    id=uuid.uuid4(),
                    document_id=doc_id,
                    assigned_signer_id=signer_id,
                    field_type=FieldType.SIGNATURE,
                    page_number=1,
                    x_coordinate=random.randint(10, 70),
                    y_coordinate=random.randint(10, 70),
                    width=150,
                    height=50,
                    required=True,
                    created_at=created_at
                )
                session.add(field)

            # Audit
            session.add(AuditLog(
                id=uuid.uuid4(),
                document_id=doc_id,
                user_id=manager_id,
                actor_type=AuditActorType.USER,
                event_type=AuditEventType.DOCUMENT_CREATED,
                created_at=created_at
            ))

            if i % 20 == 0:
                print(f"  Generated {i} documents...")

        await session.commit()

        print("\n--- SEED COMPLETE ---")
        print(f"Company: {COMPANY_NAME}")
        print("Manager Login: pranali@northstar-tech.com / northstar2025")
        print("Admin Login: admin@northstar-tech.com / admin123")
        print(f"Stats: {stats}")

if __name__ == "__main__":
    asyncio.run(seed())
