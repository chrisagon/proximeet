#!/usr/bin/env python3
"""E2E test: admin can delete an internal restaurant."""

import os
import sys
from pathlib import Path

os.environ["DATABASE_URL"] = "sqlite:////tmp/proximeet_e2e.db"

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.db import engine
from app.main import app
from app.models import Role, User


def run() -> None:
    db_path = Path("/tmp/proximeet_e2e.db")
    if db_path.exists():
        db_path.unlink()

    client = TestClient(app)

    signup = client.post(
        "/auth/signup",
        json={
            "email": "chrisagon@gmail.com",
            "first_name": "Chris",
            "last_name": "Agon",
            "nickname": None,
            "avatar_url": None,
        },
    )
    assert signup.status_code == 201, signup.text
    payload = signup.json()
    user_id = payload["user"]["id"]

    with Session(engine) as session:
        user = session.get(User, user_id)
        assert user is not None
        user.role = Role.ADMIN
        session.add(user)
        session.commit()

    place_id = "internal_test_resto"
    create = client.post(
        "/restaurants",
        json={
            "place_id": place_id,
            "name": "Restaurant Interne Test",
            "cuisine_tags": "Test",
            "is_official_habit": True,
        },
    )
    assert create.status_code == 200, create.text

    token = f"local:{user_id}"
    delete = client.delete(
        f"/restaurants/{place_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert delete.status_code == 200, delete.text

    listing = client.get("/restaurants?skip=0&limit=20")
    assert listing.status_code == 200
    items = listing.json().get("items", [])
    assert all(item["place_id"] != place_id for item in items)

    print("✅ E2E admin delete internal restaurant: OK")


if __name__ == "__main__":
    run()
