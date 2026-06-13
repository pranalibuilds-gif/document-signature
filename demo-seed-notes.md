# Northstar Technologies - Demo Data Seed Notes

This dataset simulates 12-18 months of active usage by a mid-sized technology firm.

## Company Profile
*   **Name:** Northstar Technologies Pvt. Ltd.
*   **Domain:** `northstar-tech.com`
*   **Activity Period:** June 2025 – June 2026 (12 Months)

## Personas
### 1. The Manager (User)
*   **Email:** `pranali@northstar-tech.com`
*   **Password:** `northstar2025`
*   **Role:** Office Manager / Primary Document Owner
*   **Usage:** Owns all 120 documents in the system.

### 2. The Administrator (Admin)
*   **Email:** `admin@northstar-tech.com`
*   **Password:** `admin123`
*   **Role:** System Administrator
*   **Access:** Full global audit trail and user management.

## Employee Signer Pool (40+ Reused Signers)
Includes Sarah Johnson, Michael Chen, Priya Sharma, David Wilson, Emily Davis, etc.

## Document Distribution (Total: 120)
*   **HR:** Employment Agreements, NDAs, Handbook Acks.
*   **Procurement:** Vendor Agreements, MSAs.
*   **Finance:** Budget Approvals, Expense Claims.
*   **Operations:** Asset Handovers, Facility Access.
*   **Executive:** Board Resolutions, Strategic Memos.

## Current System State
*   **Completed:** 85 (Archive ready with final PDFs)
*   **Pending:** 16 (Active workflows)
*   **Rejected:** 12 (Historical rejections)
*   **Expired:** 7 (Past deadline)
*   **Draft:** 0

---

## Technical Details
*   **PDF Storage:** `storage/original/` and `storage/final/`
*   **Database:** PostgreSQL (`docu_sign_db`)
*   **Coordinate System:** Percentage-based (0-100) for cross-device accuracy.
