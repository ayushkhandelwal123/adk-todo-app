import os
from pathlib import Path
import sqlite3
from typing import List, Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"
INDEX_FILE = STATIC_DIR / "index.html"

app = FastAPI(title="Todo API")

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def get_db_path() -> str:
    return os.environ.get("DB_PATH", str(BASE_DIR / "todos.db"))


def get_db_connection():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            completed INTEGER NOT NULL DEFAULT 0
        )
        """
    )
    conn.commit()
    return conn


class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    completed: bool = False


class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


class Todo(BaseModel):
    id: int
    title: str
    description: Optional[str] = ""
    completed: bool = False


@app.get("/", response_class=FileResponse)
def read_index():
    return FileResponse(INDEX_FILE)


@app.post("/todos", response_model=Todo, status_code=status.HTTP_201_CREATED)
def create_todo(todo: TodoCreate):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        desc = todo.description if todo.description is not None else ""
        comp = 1 if todo.completed else 0
        cursor.execute(
            "INSERT INTO todos (title, description, completed) VALUES (?, ?, ?)",
            (todo.title, desc, comp),
        )
        conn.commit()
        todo_id = cursor.lastrowid
        return Todo(
            id=todo_id,
            title=todo.title,
            description=desc,
            completed=todo.completed,
        )
    finally:
        conn.close()


@app.get("/todos", response_model=List[Todo])
def list_todos():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, description, completed FROM todos")
        rows = cursor.fetchall()
        return [
            Todo(
                id=row["id"],
                title=row["title"],
                description=row["description"],
                completed=bool(row["completed"]),
            )
            for row in rows
        ]
    finally:
        conn.close()


@app.get("/todos/{todo_id}", response_model=Todo)
def get_todo(todo_id: int):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, title, description, completed FROM todos WHERE id = ?",
            (todo_id,),
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Todo not found")
        return Todo(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            completed=bool(row["completed"]),
        )
    finally:
        conn.close()


@app.put("/todos/{todo_id}", response_model=Todo)
def update_todo(todo_id: int, todo_update: TodoUpdate):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, title, description, completed FROM todos WHERE id = ?",
            (todo_id,),
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Todo not found")

        current_title = row["title"]
        current_desc = row["description"]
        current_comp = bool(row["completed"])

        new_title = (
            todo_update.title
            if todo_update.title is not None
            else current_title
        )
        new_desc = (
            todo_update.description
            if todo_update.description is not None
            else current_desc
        )
        new_comp = (
            todo_update.completed
            if todo_update.completed is not None
            else current_comp
        )

        cursor.execute(
            "UPDATE todos SET title = ?, description = ?, completed = ? WHERE id = ?",
            (new_title, new_desc, 1 if new_comp else 0, todo_id),
        )
        conn.commit()
        return Todo(
            id=todo_id,
            title=new_title,
            description=new_desc,
            completed=new_comp,
        )
    finally:
        conn.close()


@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM todos WHERE id = ?",
            (todo_id,),
        )
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Todo not found")
        cursor.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
        conn.commit()
        return {"detail": "Todo deleted successfully"}
    finally:
        conn.close()


@app.patch("/todos/{todo_id}/toggle", response_model=Todo)
def toggle_todo(todo_id: int):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, title, description, completed FROM todos WHERE id = ?",
            (todo_id,),
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Todo not found")

        new_completed = not bool(row["completed"])
        cursor.execute(
            "UPDATE todos SET completed = ? WHERE id = ?",
            (1 if new_completed else 0, todo_id),
        )
        conn.commit()
        return Todo(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            completed=new_completed,
        )
    finally:
        conn.close()
