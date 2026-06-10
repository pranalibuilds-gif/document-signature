# Secrets & Configuration Management

This document outlines how to manage and rotate sensitive configuration values for the Document Signature SaaS.

## Principles
1. **Environment Only:** No secrets are ever stored in the code or committed to Git.
2. **Fail Fast:** The application will refuse to start if critical security settings (like `SECRET_KEY`) are missing or insufficiently secure.
3. **Rotation:** All secrets should be rotated periodically or immediately upon suspected compromise.

## Core Secrets

### 1. JWT Secret Key (`SECRET_KEY`)
- **Usage:** Signs Access and Refresh tokens.
- **Rotation Impact:** High. Rotating this key will immediately invalidate **all** active user sessions and signing links. Users will need to log in again.
- **Generation:** `openssl rand -hex 32`

### 2. Database Password (`POSTGRES_PASSWORD`)
- **Usage:** Accessing the PostgreSQL database.
- **Rotation Impact:** Medium. Requires updating the environment variable and a service restart.
- **Note:** In production, use a managed database service (RDS, Railway, etc.) and rotate via their console.

### 3. Email API Keys (`RESEND_API_KEY`, etc.)
- **Usage:** Sending invitations and notifications.
- **Rotation Impact:** Low. No user sessions are affected, but email delivery will fail until the new key is applied and the service is restarted.

## Rotation Procedure
1. Generate the new secret value.
2. Update the environment variables in the production environment (e.g., Render, Railway, or GitHub Secrets).
3. Perform a rolling restart of the application services.
4. Verify the logs to ensure the application started correctly with the new configuration.
