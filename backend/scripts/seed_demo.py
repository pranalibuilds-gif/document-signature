import asyncio
import uuid
import random
from datetime import datetime, timedelta, timezone
from sqlalchemy import text
from app.core.database import AsyncSessionLocal
from app.core.security.hashing import hash_password
from app.common.enums import DocumentStatus, SignerStatus, UserRole, AuditActorType, AuditEventType, NotificationType, NotificationStatus, FieldType
from app.modules.users.models import User
from app.modules.documents.models import Document, DocumentFile
from app.modules.signers.models import DocumentSigner
from app.modules.fields.models import SignatureField
from app.modules.audit.models import AuditLog
from app.modules.notifications.models import Notification

async def seed():
    async with AsyncSessionLocal() as session:
        print("Wiping existing data...")
        await session.execute(text("TRUNCATE TABLE field_values, signing_tokens, password_reset_tokens, email_verification_tokens, signature_fields, document_signers, document_files, audit_logs, notifications, refresh_tokens, documents, users CASCADE"))
        await session.commit()

        print("Creating Office Manager account...")
        manager_id = uuid.uuid4()
        manager_email = "pranali@demo.com"
        manager_password = "pranali25"

        manager = User(
            id=manager_id,
            email=manager_email,
            hashed_password=hash_password(manager_password),
            first_name="Pranali",
            last_name="Manager",
            role=UserRole.ADMIN,
            is_verified=True,
            created_at=datetime.now(timezone.utc) - timedelta(days=1000)
        )
        session.add(manager)

        user2_id = uuid.uuid4()
        user2 = User(
            id=user2_id,
            email="staff@labmentix.com",
            hashed_password=hash_password("Password123!"),
            first_name="Staff",
            last_name="Member",
            role=UserRole.USER,
            is_verified=True,
            created_at=datetime.now(timezone.utc) - timedelta(days=500)
        )
        session.add(user2)
        await session.flush()

        print("Generating 3 years of document history...")
        doc_titles = [
            "Employment Contract", "NDA Agreement", "Office Lease", "Equipment Purchase",
            "Vendor Agreement", "Software License", "Project Proposal", "Invoice Approval",
            "MOU Partnership", "Employee Handbook Ack", "Insurance Renewal", "Tax Form W-9",
            "Board Meeting Minutes", "Shareholder Agreement", "Contractor SOW"
        ]

        signers_pool = [
            "alice@example.com", "bob@example.com", "charlie@client.com", "dana@partner.net",
            "evan@vendor.com", "fiona@hr.com", "george@legal.org", "hannah@finance.com"
        ]

        total_docs = 120
        start_date = datetime.now(timezone.utc) - timedelta(days=1000)

        for i in range(total_docs):
            created_at = start_date + timedelta(days=random.randint(0, 990), hours=random.randint(0, 23))

            # Determine status based on age
            age_days = (datetime.now(timezone.utc) - created_at).days
            if age_days < 5:
                status = random.choice([DocumentStatus.DRAFT, DocumentStatus.PENDING])
            elif age_days < 30:
                status = random.choice([DocumentStatus.PENDING, DocumentStatus.PARTIALLY_SIGNED, DocumentStatus.COMPLETED])
            else:
                status = random.choices(
                    [DocumentStatus.COMPLETED, DocumentStatus.REJECTED, DocumentStatus.EXPIRED],
                    weights=[80, 10, 10]
                )[0]

            doc_id = uuid.uuid4()
            document = Document(
                id=doc_id,
                owner_id=manager_id,
                title=f"{random.choice(doc_titles)} - {2021 + (1000 - age_days)//365} #{i+1}",
                status=status,
                created_at=created_at,
                updated_at=created_at + timedelta(days=1),
                completed_at=created_at + timedelta(days=2) if status == DocumentStatus.COMPLETED else None,
                expires_at=created_at + timedelta(days=30)
            )
            session.add(document)

            # Add a mock file - UNIQUE stored_name
            stored_name = f"{uuid.uuid4()}.pdf"
            doc_file = DocumentFile(
                id=uuid.uuid4(),
                document_id=doc_id,
                file_name="agreement.pdf",
                stored_name=stored_name,
                file_path=f"storage/original/{stored_name}",
                file_size=1024 * 150,
                mime_type="application/pdf",
                is_final=False,
                created_at=created_at
            )
            session.add(doc_file)

            # Add signers (1-3) - UNIQUE emails per document
            num_signers = random.randint(1, 3)
            doc_signers_emails = random.sample(signers_pool, num_signers)

            for j, s_email in enumerate(doc_signers_emails):
                signer_id = uuid.uuid4()
                s_status = SignerStatus.PENDING
                if status == DocumentStatus.COMPLETED:
                    s_status = SignerStatus.SIGNED
                elif status == DocumentStatus.REJECTED and j == 0:
                    s_status = SignerStatus.REJECTED

                signer = DocumentSigner(
                    id=signer_id,
                    document_id=doc_id,
                    email=s_email,
                    status=s_status,
                    invited_at=created_at + timedelta(hours=1),
                    signed_at=created_at + timedelta(days=1) if s_status == SignerStatus.SIGNED else None,
                    created_at=created_at
                )
                session.add(signer)

                # Add a field for the signer
                field = SignatureField(
                    id=uuid.uuid4(),
                    document_id=doc_id,
                    assigned_signer_id=signer_id,
                    field_type=FieldType.SIGNATURE,
                    page_number=1,
                    x_coordinate=random.randint(10, 80),
                    y_coordinate=random.randint(10, 80),
                    width=150,
                    height=50,
                    required=True,
                    created_at=created_at
                )
                session.add(field)

            # Audit logs
            audit = AuditLog(
                id=uuid.uuid4(),
                document_id=doc_id,
                user_id=manager_id,
                actor_type=AuditActorType.USER,
                event_type=AuditEventType.DOCUMENT_CREATED,
                created_at=created_at
            )
            session.add(audit)

            if i % 20 == 0:
                print(f"  Generated {i} documents...")

        await session.commit()
        print("\nDatabase seeded successfully! ✅")
        print(f"Manager Email: {manager_email}")
        print(f"Password: {manager_password}")

if __name__ == "__main__":
    asyncio.run(seed())
