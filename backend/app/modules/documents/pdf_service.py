import os
import uuid
import io
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from pypdf import PdfReader, PdfWriter

from app.modules.documents.models import Document, DocumentFile
from app.modules.documents.repository import DocumentRepository
from app.modules.signers.repository import SignerRepository
from app.modules.fields.repository import SignatureFieldRepository
from app.modules.signing.repository import SigningRepository
from app.modules.audit.service import AuditService
from app.common.enums import AuditActorType, AuditEventType, FieldType
from app.core.config import settings
from app.core.logging import logger

class PdfGenerationService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.doc_repo = DocumentRepository(session)
        self.signer_repo = SignerRepository(session)
        self.field_repo = SignatureFieldRepository(session)
        self.signing_repo = SigningRepository(session)
        self.audit_service = AuditService(session)

    async def generate_final_pdf(self, document_id: uuid.UUID) -> DocumentFile | None:
        """
        Generates the final signed PDF by overlaying field values onto the original PDF.
        """
        logger.info(f"Generating final PDF for document: {document_id}")
        # 1. Prevent regeneration
        existing_final = await self.doc_repo.get_final_file(document_id)
        if existing_final:
            return existing_final

        # 2. Fetch all required data
        document = await self.doc_repo.get_by_id(document_id)
        original_file = await self.doc_repo.get_original_file(document_id)
        if not original_file:
            return None

        fields = await self.field_repo.list_by_document(document_id)

        # 3. Create map of field_id to value
        # We'll fetch all values for all signers for this document
        from app.modules.signing.models import FieldValue
        result = await self.session.execute(
            select(FieldValue).where(FieldValue.field_id.in_([f.id for f in fields]))
        )
        values = {v.field_id: v.value for v in result.scalars().all()}

        # 4. Process PDF
        reader = PdfReader(original_file.file_path)
        writer = PdfWriter()

        # Group fields by page
        fields_by_page = {}
        for f in fields:
            pg = f.page_number
            if pg not in fields_by_page:
                fields_by_page[pg] = []
            fields_by_page[pg].append(f)

        for page_idx in range(len(reader.pages)):
            page = reader.pages[page_idx]
            page_num = page_idx + 1

            if page_num in fields_by_page:
                # Create overlay for this page
                packet = io.BytesIO()
                # Use actual page size from reader
                mb = page.mediabox
                width = float(mb.width)
                height = float(mb.height)

                can = canvas.Canvas(packet, pagesize=(width, height))

                for f in fields_by_page[page_num]:
                    val = values.get(f.id, "")
                    if not val:
                        continue

                    # ReportLab origin is bottom-left
                    # PDF coordinates usually follow this too, but we need to verify
                    # If x,y in our DB is from top-left, we need to flip y.
                    # Standard in these mini-docusigns is often x,y from bottom-left (PDF style)
                    # or top-left (Web style). Let's assume bottom-left for now as per "absolute PDF coordinates".

                    text = val
                    if f.field_type == FieldType.SIGNATURE:
                        text = f"Signed by: {val}"
                        can.setFont("Helvetica-Bold", 10)
                    else:
                        can.setFont("Helvetica", 10)

                    can.drawString(f.x_coordinate, f.y_coordinate, text)

                can.save()
                packet.seek(0)
                overlay_reader = PdfReader(packet)
                overlay_page = overlay_reader.pages[0]

                page.merge_page(overlay_page)

            writer.add_page(page)

        # 5. Save final file
        stored_name = f"{uuid.uuid4()}.pdf"
        final_dir = os.path.join(settings.STORAGE_BASE_PATH, "final")
        os.makedirs(final_dir, exist_ok=True)
        final_path = os.path.join(final_dir, stored_name)

        with open(final_path, "wb") as output_stream:
            writer.write(output_stream)

        # 6. Create DocumentFile record
        file_size = os.path.getsize(final_path)
        final_doc_file = DocumentFile(
            document_id=document_id,
            file_name=f"Signed_{original_file.file_name}",
            stored_name=stored_name,
            file_path=final_path,
            file_size=file_size,
            mime_type="application/pdf",
            is_final=True
        )
        created_file = await self.doc_repo.create_file(final_doc_file)
        logger.info(f"Final PDF generated successfully: {final_path}")

        # 7. Audit
        await self.audit_service.record_event(
            event_type=AuditEventType.FINAL_PDF_GENERATED,
            actor_type=AuditActorType.SYSTEM,
            document_id=document_id,
            event_data={"file_size": file_size}
        )

        return created_file
