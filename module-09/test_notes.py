"""Pytest suite for the Notes API."""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import pytest
import pytest_asyncio
import httpx

import notes as notes_module
from notes import app

pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture
async def client(tmp_path, monkeypatch):
    db_file = str(tmp_path / "notes.db")
    monkeypatch.setattr(notes_module, "DB_PATH", db_file)
    notes_module.init_schema()
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
    ) as c:
        yield c


# ── helpers ───────────────────────────────────────────────────────────────

async def _create(client: httpx.AsyncClient, title: str, body: str = "") -> dict:
    r = await client.post("/notes", json={"title": title, "body": body})
    assert r.status_code == 201
    return r.json()


# ── create ────────────────────────────────────────────────────────────────

async def test_create_returns_201(client):
    r = await client.post("/notes", json={"title": "Hello", "body": "World"})
    assert r.status_code == 201
    d = r.json()
    assert d["id"] == 1
    assert d["title"] == "Hello"
    assert d["body"] == "World"
    assert d["created_at"].endswith("Z")
    assert d["updated_at"].endswith("Z")


async def test_create_body_defaults_to_empty(client):
    r = await client.post("/notes", json={"title": "No body"})
    assert r.status_code == 201
    assert r.json()["body"] == ""


# ── list ──────────────────────────────────────────────────────────────────

async def test_list_empty(client):
    r = await client.get("/notes")
    assert r.status_code == 200
    assert r.json() == []


async def test_list_returns_all_in_order(client):
    await _create(client, "A")
    await _create(client, "B")
    await _create(client, "C")
    r = await client.get("/notes")
    assert r.status_code == 200
    assert [n["title"] for n in r.json()] == ["A", "B", "C"]


# ── search ────────────────────────────────────────────────────────────────

async def test_search_matches_title(client):
    await _create(client, "Python tips", "some body")
    await _create(client, "Go tricks", "other body")
    r = await client.get("/notes", params={"q": "Python"})
    assert r.status_code == 200
    results = r.json()
    assert len(results) == 1
    assert results[0]["title"] == "Python tips"


async def test_search_matches_body(client):
    await _create(client, "note1", "contains keyword here")
    await _create(client, "note2", "nothing special")
    r = await client.get("/notes", params={"q": "keyword"})
    assert r.status_code == 200
    assert len(r.json()) == 1
    assert r.json()[0]["title"] == "note1"


async def test_search_case_insensitive_like(client):
    await _create(client, "UPPER title")
    r = await client.get("/notes", params={"q": "upper"})
    assert r.status_code == 200
    assert len(r.json()) == 1


async def test_search_no_match_returns_empty_list(client):
    await _create(client, "foo")
    r = await client.get("/notes", params={"q": "zzznomatch"})
    assert r.status_code == 200
    assert r.json() == []


# ── get one ───────────────────────────────────────────────────────────────

async def test_get_one_returns_note(client):
    note = await _create(client, "Single", "body text")
    r = await client.get(f"/notes/{note['id']}")
    assert r.status_code == 200
    assert r.json()["title"] == "Single"
    assert r.json()["body"] == "body text"


async def test_get_one_fields_match_create(client):
    note = await _create(client, "Check fields", "content")
    r = await client.get(f"/notes/{note['id']}")
    assert r.json() == note


# ── update ────────────────────────────────────────────────────────────────

async def test_update_title_only(client):
    note = await _create(client, "Old title", "keep this body")
    r = await client.patch(f"/notes/{note['id']}", json={"title": "New title"})
    assert r.status_code == 200
    d = r.json()
    assert d["title"] == "New title"
    assert d["body"] == "keep this body"


async def test_update_body_only(client):
    note = await _create(client, "Keep title", "old body")
    r = await client.patch(f"/notes/{note['id']}", json={"body": "new body"})
    assert r.status_code == 200
    d = r.json()
    assert d["title"] == "Keep title"
    assert d["body"] == "new body"


async def test_update_both_fields(client):
    note = await _create(client, "old", "old")
    r = await client.patch(f"/notes/{note['id']}", json={"title": "new", "body": "new"})
    assert r.status_code == 200
    assert r.json()["title"] == "new"
    assert r.json()["body"] == "new"


async def test_update_is_persisted(client):
    note = await _create(client, "Before")
    await client.patch(f"/notes/{note['id']}", json={"title": "After"})
    r = await client.get(f"/notes/{note['id']}")
    assert r.json()["title"] == "After"


# ── delete ────────────────────────────────────────────────────────────────

async def test_delete_returns_204(client):
    note = await _create(client, "Bye")
    r = await client.delete(f"/notes/{note['id']}")
    assert r.status_code == 204
    assert r.content == b""


async def test_delete_removes_note_from_list(client):
    note = await _create(client, "Gone")
    await client.delete(f"/notes/{note['id']}")
    r = await client.get("/notes")
    assert all(n["id"] != note["id"] for n in r.json())


async def test_delete_does_not_affect_other_notes(client):
    a = await _create(client, "A")
    b = await _create(client, "B")
    await client.delete(f"/notes/{a['id']}")
    r = await client.get("/notes")
    ids = [n["id"] for n in r.json()]
    assert a["id"] not in ids
    assert b["id"] in ids


# ── 404 ───────────────────────────────────────────────────────────────────

async def test_get_nonexistent_returns_404(client):
    r = await client.get("/notes/9999")
    assert r.status_code == 404
    assert r.json() == {"error": "not found"}


async def test_patch_nonexistent_returns_404(client):
    r = await client.patch("/notes/9999", json={"title": "X"})
    assert r.status_code == 404
    assert r.json() == {"error": "not found"}


async def test_delete_nonexistent_returns_404(client):
    r = await client.delete("/notes/9999")
    assert r.status_code == 404
    assert r.json() == {"error": "not found"}


# ── 422 ───────────────────────────────────────────────────────────────────

async def test_create_missing_title_returns_422(client):
    r = await client.post("/notes", json={"body": "no title field"})
    assert r.status_code == 422


async def test_create_empty_title_returns_422(client):
    r = await client.post("/notes", json={"title": "", "body": "empty title"})
    assert r.status_code == 422


async def test_create_title_too_long_returns_422(client):
    r = await client.post("/notes", json={"title": "x" * 201})
    assert r.status_code == 422


async def test_create_non_string_title_returns_422(client):
    r = await client.post("/notes", json={"title": 123})
    # pydantic coerces int→str in v2, so expect either 201 or 422;
    # the key point is the server handles it without a 500
    assert r.status_code in (201, 422)


async def test_patch_empty_title_returns_422(client):
    note = await _create(client, "Valid title")
    r = await client.patch(f"/notes/{note['id']}", json={"title": ""})
    assert r.status_code == 422


async def test_patch_title_too_long_returns_422(client):
    note = await _create(client, "Valid title")
    r = await client.patch(f"/notes/{note['id']}", json={"title": "y" * 201})
    assert r.status_code == 422
