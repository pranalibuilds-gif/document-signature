import asyncio
import httpx
from app.core.security.jwt import create_access_token, create_refresh_token
from app.common.enums import UserRole
import uuid

BASE_URL = "http://127.0.0.1:8000/api/v1"

async def test_auth():
    async with httpx.AsyncClient() as client:
        print("--- Phase 1: Auth Integrity Audit ---")

        # 1. Login TC-1.1 (Manager)
        print("\n[TC-1.1] User Login (Manager)")
        login_res = await client.post(f"{BASE_URL}/auth/login", json={
            "email": "pranali@northstar-tech.com",
            "password": "northstar2025"
        })
        if login_res.status_code == 200:
            user_token = login_res.json()["access_token"]
            me_res = await client.get(f"{BASE_URL}/users/me", headers={"Authorization": f"Bearer {user_token}"})
            user_data = me_res.json()
            print(f"PASS: Login Successful. Role: {user_data['role']}")

            # TC-2.1 User -> Admin URL
            print("[TC-2.1] User -> Admin API Check")
            admin_res = await client.get(f"{BASE_URL}/admin/dashboard", headers={"Authorization": f"Bearer {user_token}"})
            print(f"RESULT: User accessing admin API status: {admin_res.status_code}")
            if admin_res.status_code == 403:
                print("PASS: Admin access denied for User.")
            else:
                print(f"FAIL: Expected 403, got {admin_res.status_code}")
        else:
            print(f"FAIL: Login failed: {login_res.text}")

        # 2. Login TC-1.2 (Admin)
        print("\n[TC-1.2] Admin Login")
        login_res = await client.post(f"{BASE_URL}/auth/login", json={
            "email": "admin@northstar-tech.com",
            "password": "admin123"
        })
        if login_res.status_code == 200:
            admin_token = login_res.json()["access_token"]
            me_res = await client.get(f"{BASE_URL}/users/me", headers={"Authorization": f"Bearer {admin_token}"})
            admin_data = me_res.json()
            print(f"PASS: Admin Login Successful. Role: {admin_data['role']}")

            # TC-2.2 Admin -> User Routes
            print("[TC-2.2] Admin -> User API Check")
            user_api_res = await client.get(f"{BASE_URL}/documents", headers={"Authorization": f"Bearer {admin_token}"})
            print(f"RESULT: Admin accessing documents API status: {user_api_res.status_code}")
            # Usually admins are users too, so 200 is expected unless strict separation is applied.
        else:
            print(f"FAIL: Admin Login failed: {login_res.text}")

        # 3. Anonymous Access TC-2.3
        print("\n[TC-2.3] Anonymous Access Check")
        anon_res = await client.get(f"{BASE_URL}/documents")
        print(f"RESULT: Anonymous accessing documents API status: {anon_res.status_code}")
        if anon_res.status_code == 401:
            print("PASS: Anonymous access denied.")
        else:
            print(f"FAIL: Expected 401, got {anon_res.status_code}")

if __name__ == "__main__":
    asyncio.run(test_auth())
