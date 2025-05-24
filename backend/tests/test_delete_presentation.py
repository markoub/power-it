import sys
import os
from fastapi.testclient import TestClient
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api import app
from database import init_db

asyncio.run(init_db())


def test_create_and_delete_presentation():
    name = f"Delete Test {os.urandom(4).hex()}"
    payload = {
        "name": name,
        "topic": "Test Topic",
        "author": "Tester",
        "research_type": "research",
    }

    with TestClient(app) as client:
        create_resp = client.post("/presentations", json=payload)
        assert create_resp.status_code == 201
        pres_id = create_resp.json()["id"]

        del_resp = client.delete(f"/presentations/{pres_id}")
        assert del_resp.status_code == 204

        get_resp = client.get(f"/presentations/{pres_id}")
        assert get_resp.status_code == 404

        list_resp = client.get("/presentations")
        assert list_resp.status_code == 200
        data = list_resp.json()
        items = data["items"] if isinstance(data, dict) else data
        ids = [p["id"] for p in items]
        assert pres_id not in ids
