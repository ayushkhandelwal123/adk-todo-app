import os
import pytest
from fastapi.testclient import TestClient
from app import app


@pytest.fixture(autouse=True)
def setup_test_db(tmp_path, monkeypatch):
    db_file = tmp_path / "test_todos.db"
    monkeypatch.setenv("DB_PATH", str(db_file))


client = TestClient(app)


def test_create_todo():
    # Test creating todo with minimal fields
    response = client.post("/todos", json={"title": "Buy milk"})
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Buy milk"
    assert data["description"] == ""
    assert data["completed"] is False

    # Test creating todo with full fields
    response2 = client.post(
        "/todos",
        json={"title": "Walk dog", "description": "In the park", "completed": True},
    )
    assert response2.status_code == 201
    data2 = response2.json()
    assert data2["id"] == 2
    assert data2["title"] == "Walk dog"
    assert data2["description"] == "In the park"
    assert data2["completed"] is True


def test_list_todos():
    # Empty list initial
    response = client.get("/todos")
    assert response.status_code == 200
    assert response.json() == []

    # After adding todos
    client.post("/todos", json={"title": "Todo 1"})
    client.post("/todos", json={"title": "Todo 2"})

    response = client.get("/todos")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Todo 1"
    assert data[1]["title"] == "Todo 2"


def test_get_todo():
    client.post("/todos", json={"title": "Read book", "description": "Chapter 1"})

    # Found
    response = client.get("/todos/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Read book"
    assert data["description"] == "Chapter 1"
    assert data["completed"] is False

    # Not found 404
    response_404 = client.get("/todos/999")
    assert response_404.status_code == 404
    assert response_404.json() == {"detail": "Todo not found"}


def test_update_todo():
    client.post("/todos", json={"title": "Old Title", "description": "Old Desc"})

    # Update title and completed status
    response = client.put(
        "/todos/1", json={"title": "New Title", "completed": True}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "New Title"
    assert data["description"] == "Old Desc"
    assert data["completed"] is True

    # Not found 404
    response_404 = client.put("/todos/999", json={"title": "Anything"})
    assert response_404.status_code == 404
    assert response_404.json() == {"detail": "Todo not found"}


def test_delete_todo():
    client.post("/todos", json={"title": "To delete"})

    # Delete existing
    response = client.delete("/todos/1")
    assert response.status_code == 200

    # Verify it is deleted from list
    response_list = client.get("/todos")
    assert response_list.json() == []

    # Get deleted todo -> 404
    response_get = client.get("/todos/1")
    assert response_get.status_code == 404

    # Delete non-existing -> 404
    response_404 = client.delete("/todos/999")
    assert response_404.status_code == 404
    assert response_404.json() == {"detail": "Todo not found"}


def test_toggle_todo():
    # Create todo (defaults to completed=False)
    client.post("/todos", json={"title": "Toggle test"})

    # Toggle False -> True
    res1 = client.patch("/todos/1/toggle")
    assert res1.status_code == 200
    assert res1.json()["completed"] is True
    assert res1.json()["id"] == 1
    assert res1.json()["title"] == "Toggle test"

    # Toggle True -> False
    res2 = client.patch("/todos/1/toggle")
    assert res2.status_code == 200
    assert res2.json()["completed"] is False


def test_toggle_todo_404():
    response_404 = client.patch("/todos/999/toggle")
    assert response_404.status_code == 404
    assert response_404.json() == {"detail": "Todo not found"}


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "<title>Todo App</title>" in response.text




def test_todos_db_not_touched():
    assert not os.path.exists("todos.db")
