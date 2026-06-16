import asyncio
import httpx
import os
import uuid

BASE_URL = "http://127.0.0.1:8000/api/v1"

async def get_token():
    async with httpx.AsyncClient() as client:
        res = await client.post(f"{BASE_URL}/auth/login", json={
            "email": "pranali@northstar-tech.com",
            "password": "northstar2025"
        })
        return res.json()["access_token"]

async def test_uploads():
    token = await get_token()
    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient() as client:
        print("--- Phase 7: PDF Rendering Stress Audit ---")

        # TC-7.4.3 Size Limit
        print("\n[TC-7.4.3] Upload Size Limit Test (Simulating 21MB)")
        # We don't actually need to send 21MB, we can mock the size in the request or use a real file
        # Creating a dummy "large" file
        large_path = "storage/stress_tests/too_large.pdf"
        with open(large_path, "wb") as f:
            f.seek(21 * 1024 * 1024 - 1)
            f.write(b"\0")

        try:
            with open(large_path, "rb") as f:
                res = await client.post(f"{BASE_URL}/documents", headers=headers, json={"title": "Size Test"})
                doc_id = res.json()["id"]

                files = {"file": ("too_large.pdf", f, "application/pdf")}
                upload_res = await client.post(f"{BASE_URL}/documents/{doc_id}/upload", headers=headers, files=files)
                print(f"Result: {upload_res.status_code}")
                if upload_res.status_code == 413:
                    print("PASS: 21MB file rejected.")
                else:
                    print(f"FAIL: Expected 413, got {upload_res.status_code}")
        finally:
            if os.path.exists(large_path): os.remove(large_path)

        # TC-7.1.3 Large PDF Upload
        print("\n[TC-7.1.3] Uploading 50-page PDF...")
        with open("storage/stress_tests/large_50.pdf", "rb") as f:
            res = await client.post(f"{BASE_URL}/documents", headers=headers, json={"title": "Large Doc Test"})
            doc_id = res.json()["id"]
            files = {"file": ("large_50.pdf", f, "application/pdf")}
            upload_res = await client.post(f"{BASE_URL}/documents/{doc_id}/upload", headers=headers, files=files)
            print(f"Upload Status: {upload_res.status_code}")
            if upload_res.status_code == 200:
                print("PASS: 50-page PDF uploaded.")
            else:
                print("FAIL: Large upload failed.")

        # TC-7.2.4 Mixed Orientation Upload
        print("\n[TC-7.2.4] Uploading Mixed Orientation PDF...")
        with open("storage/stress_tests/mixed_orientation.pdf", "rb") as f:
            res = await client.post(f"{BASE_URL}/documents", headers=headers, json={"title": "Mixed Orientation Test"})
            doc_id = res.json()["id"]
            files = {"file": ("mixed.pdf", f, "application/pdf")}
            upload_res = await client.post(f"{BASE_URL}/documents/{doc_id}/upload", headers=headers, files=files)
            print(f"Upload Status: {upload_res.status_code}")
            if upload_res.status_code == 200:
                print("PASS: Mixed orientation PDF uploaded.")
            else:
                print("FAIL: Mixed orientation upload failed.")

if __name__ == "__main__":
    asyncio.run(test_uploads())
