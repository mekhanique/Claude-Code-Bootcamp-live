"""Notes API persisting to SQLite."""
from __future__ import annotations

import sqlite3
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field

DB_PATH = "notes.db"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_schema() -> None:
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                body TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    init_schema()
    yield


app = FastAPI(lifespan=lifespan)


class NoteIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    body: str = Field(default="")


class NotePatch(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    body: str | None = None


class NoteOut(BaseModel):
    id: int
    title: str
    body: str
    created_at: str
    updated_at: str


def row_to_note(row: sqlite3.Row) -> NoteOut:
    return NoteOut(
        id=row["id"],
        title=row["title"],
        body=row["body"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(_, exc: HTTPException) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


@app.post("/notes", status_code=201, response_model=NoteOut)
def create_note(payload: NoteIn) -> NoteOut:
    now = utc_now_iso()
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO notes (title, body, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (payload.title, payload.body, now, now),
        )
        row = conn.execute("SELECT * FROM notes WHERE id = ?", (cur.lastrowid,)).fetchone()
    return row_to_note(row)


@app.get("/notes", response_model=list[NoteOut])
def list_notes(q: str | None = Query(default=None)) -> list[NoteOut]:
    with get_conn() as conn:
        if q:
            like = f"%{q}%"
            rows = conn.execute(
                "SELECT * FROM notes WHERE title LIKE ? OR body LIKE ? ORDER BY id",
                (like, like),
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM notes ORDER BY id").fetchall()
    return [row_to_note(r) for r in rows]


@app.get("/notes/{note_id}", response_model=NoteOut)
def get_note(note_id: int) -> NoteOut:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="not found")
    return row_to_note(row)


@app.patch("/notes/{note_id}", response_model=NoteOut)
def update_note(note_id: int, payload: NotePatch) -> NoteOut:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="not found")
        title = payload.title if payload.title is not None else row["title"]
        body = payload.body if payload.body is not None else row["body"]
        now = utc_now_iso()
        conn.execute(
            "UPDATE notes SET title = ?, body = ?, updated_at = ? WHERE id = ?",
            (title, body, now, note_id),
        )
        row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
    return row_to_note(row)


@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: int) -> Response:
    with get_conn() as conn:
        cur = conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="not found")
    return Response(status_code=204)
