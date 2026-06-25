# job_app/tests/test_api.py
import pytest
from httpx import AsyncClient


# 🔒 Force all async tests in this file to share the session loop scope
# This prevents different event loops from mixing up!
pytestmark = pytest.mark.asyncio(loop_scope="session")

async def test_user_registration_and_login_flow(client: AsyncClient):
    """Verifies user creation, correct password validation, and cookie assignment."""
    # 1. Register a profile
    reg_payload = {
        "username": "tester",
        "email": "tester@test.com",
        "password": "supersecurepassword"
    }
    reg_resp = await client.post("/auth/register", json=reg_payload)
    assert reg_resp.status_code == 201
    
    # 2. Duplicate entries must be rejected by database safeguards
    dup_resp = await client.post("/auth/register", json=reg_payload)
    assert dup_resp.status_code == 400

    # 3. Login attempt with bad credentials must be blocked
    bad_login = {"email": "tester@test.com", "password": "wrongpassword"}
    bad_resp = await client.post("/auth/login", json=bad_login)
    assert bad_resp.status_code == 401

    # 4. Successful login must register cookie markers
    good_login = {"email": "tester@test.com", "password": "supersecurepassword"}
    login_resp = await client.post("/auth/login", json=good_login)
    assert login_resp.status_code == 200
    assert "job_tracker_session" in client.cookies


async def test_spreadsheet_route_unauthorized_protection(client: AsyncClient):
    """Ensures unauthenticated calls to grid data are immediately blocked by dependencies."""
    response = await client.get("/jobs/")
    assert response.status_code == 401




# job_app/tests/test_api.py

async def test_spreadsheet_row_manipulation_lifecycle(client: AsyncClient):
    """Tests standard grid CRUD operations directly without hitting external networks."""
    # 1. 🔒 Authenticate this specific client instance so it has a valid cookie state
    reg_payload = {"username": "griduser", "email": "grid@test.com", "password": "password123"}
    await client.post("/auth/register", json=reg_payload)
    
    # This step logs the user in and places the secure cookie token into the client's cookie jar
    await client.post("/auth/login", json={"email": "grid@test.com", "password": "password123"})

    # 2. Build the spreadsheet row data payload
    job_create_payload = {
        "title": "Cloud Infrastructure Engineer",
        "company_name": "Amazon",
        "raw_job_posting": "Looking for an AWS architecture expert to manage databases.",
        "status": "Wishlist"
    }
    
    # 3. Append a new row to the spreadsheet grid (Will now clear authentication!)
    create_resp = await client.post("/jobs/", json=job_create_payload)
    assert create_resp.status_code == 201
    row_data = create_resp.json()
    assert row_data["title"] == "Cloud Infrastructure Engineer"
    assert row_data["company_name"] == "Amazon"
    assert row_data["status"] == "Wishlist"

    # 4. Fetch the spreadsheet rows grid table layout
    get_grid_resp = await client.get("/jobs/")
    assert get_grid_resp.status_code == 200
    assert len(get_grid_resp.json()) == 1

    # 5. Modify a cell status directly (e.g. Wishlist -> Interviewing)
    job_id = row_data["id"]
    patch_resp = await client.patch(f"/jobs/{job_id}/status", json={"status": "Interviewing"})
    assert patch_resp.status_code == 200
    assert patch_resp.json()["status"] == "Interviewing"

    # 6. Delete a record out of the grid row collection
    del_resp = await client.delete(f"/jobs/{job_id}")
    assert del_resp.status_code == 204
