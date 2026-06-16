import asyncio
import httpx
import uuid
import time

BASE_URL = "http://127.0.0.1:8000/api/v1"

async def pen_test():
    async with httpx.AsyncClient() as client:
        print("--- Phase 3: Admin Security Pen Test ---")

        # 1. Setup: Get a valid USER token
        print("\n[Setup] Obtaining User Token...")
        user_email = f"tester_{uuid.uuid4().hex[:6]}@demo.com"
        await client.post(f"{BASE_URL}/auth/register", json={
            "email": user_email, "password": "password123", "first_name": "Pen", "last_name": "Tester"
        })
        login_res = await client.post(f"{BASE_URL}/auth/login", json={"email": user_email, "password": "password123"})
        user_token = login_res.json()["access_token"]
        user_headers = {"Authorization": f"Bearer {user_token}"}

        # 2. [TC-3.2.1] Manual Admin Request (Privilege Escalation attempt)
        admin_endpoints = ["/admin/dashboard", "/admin/users", "/admin/audit", "/admin/health-details"]
        print("\n[TC-3.2.1] Attempting to access Admin endpoints with USER token...")
        for ep in admin_endpoints:
            res = await client.get(f"{BASE_URL}{ep}", headers=user_headers)
            print(f"Endpoint {ep}: Status {res.status_code}")
            if res.status_code == 403:
                print(f"  PASS: Access denied for {ep}")
            else:
                print(f"  FAIL: VULNERABILITY! Access allowed for {ep}")

        # 3. [TC-3.6.1] Public Health Review
        print("\n[TC-3.6.1] Reviewing Public Health Endpoint...")
        health_res = await client.get("http://127.0.0.1:8000/health")
        try:
            health_json = health_res.json()
            print(f"Health Response: {health_json}")
            # Check for secrets leakage
            secrets_leak = any(k in str(health_json).lower() for k in ["pass", "secret", "key", "token", "db"])
            if not secrets_leak:
                print("  PASS: No secrets detected in public health response.")
            else:
                print("  FAIL: Potential sensitive data leak in health endpoint.")
        except Exception as e:
            print(f"  FAIL: Health endpoint returned non-JSON: {e}")

        # 4. [TC-3.7.1] Rate Limit Validation (Login)
        print("\n[TC-3.7.1] Validating Rate Limiting on Login...")
        burst_count = 15
        responses = []
        for i in range(burst_count):
            responses.append(client.post(f"{BASE_URL}/auth/login", json={"email": "wrong@test.com", "password": "wrong"}))

        results = await asyncio.gather(*responses)
        status_codes = [r.status_code for r in results]
        if 429 in status_codes:
            print(f"  PASS: Rate limiting triggered. Status 429 found in {status_codes.count(429)} requests.")
        else:
            print(f"  FAIL: Rate limiting not triggered after {burst_count} attempts. Statuses: {set(status_codes)}")

        # 5. [TC-3.8] Error Leakage Review
        print("\n[TC-3.8] Forcing 500 error to check for leakage...")
        err_res = await client.get("http://127.0.0.1:8000/debug-error")
        print(f"Error Response Status: {err_res.status_code}")
        try:
            data = err_res.json()
            print(f"Response Payload: {data}")
            leakage = "stack_trace" in data or "Traceback" in str(data) or "File" in str(data)
            if not leakage:
                print("  PASS: No stack traces or sensitive paths leaked in production error response.")
            else:
                print("  FAIL: Sensitive error info leaked!")
        except Exception as e:
            print(f"  FAIL: Error response was not JSON or contained garbage: {e}")
            print(f"  RAW BODY START: {err_res.text[:50]}")

if __name__ == "__main__":
    asyncio.run(pen_test())
