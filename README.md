# FastAPI Todo App

A lightweight Todo web application built with FastAPI, SQLite, and vanilla JavaScript.

## Features

- Full CRUD operations for managing todo items.
- SQLite persistent database storage using Python's standard `sqlite3` module.
- Configurable database path via `DB_PATH` environment variable (defaults to `todos.db`).
- Interactive plain JavaScript frontend served at `/` with strikethrough styling for completed todos.
- Automated testing suite using `pytest` and `TestClient` with isolated per-test temporary databases.

## API Endpoints

- `GET /`: Serve the frontend user interface (`static/index.html`).
- `POST /todos`: Create a new todo item.
  - Body: `{"title": "...", "description": "...", "completed": false}`
- `GET /todos`: List all todo items.
- `GET /todos/{id}`: Retrieve a todo item by ID (returns `404` if not found).
- `PUT /todos/{id}`: Update a todo item by ID (returns `404` if not found).
  - Body: `{"title": "...", "description": "...", "completed": true}`
- `DELETE /todos/{id}`: Delete a todo item by ID (returns `404` if not found).
- `PATCH /todos/{id}/toggle`: Toggle a todo item's completion status (returns `404` if not found).

## Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running the App

Start the FastAPI app with Uvicorn:

```bash
uvicorn app:app --reload --port 8001
```

Open your browser and navigate to `http://127.0.0.1:8001` to view the UI.

## Running Tests

Run the test suite with `pytest`:

```bash
pytest
```
