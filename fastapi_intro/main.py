from fastapi import FastAPI
from fastapi import HTTPException, status
from pydantic import BaseModel
from endpoints import books

app = FastAPI()
app.include_router(books.router)


class Note(BaseModel):
    title: str
    body: str


notes_db: dict[int, Note] = {}
next_id = 1


@app.get("/")
def read_root():
    return {"message": "Hello, World"}


@app.get("/items/{item_id}")
def read_item(item_id: str):
    return {"item_id": item_id, "doubled": item_id * 2}


@app.post("/notes", status_code=status.HTTP_201_CREATED)
def create_note(note: Note):
    global next_id
    notes_db[next_id] = note
    created_id = next_id
    next_id += 1
    return {"id": created_id, "note": note}


@app.get("/notes/{note_id}")
def get_note(note_id: int):
    if note_id not in notes_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Note {note_id} not found."
        )
    return notes_db.get(note_id)


@app.get("/notes")
def list_notes(tag: str | None = None, limit: int = 10):
    results = list(notes_db.values())
    if tag is not None:
        results = [n for n in results if tag in n.title]
    return results[:limit]


@app.put("/notes/{note_id}")
def replace_note(note_id: int, note: Note):
    notes_db[note_id] = note
    return note


@app.patch("/notes/{note_id}")
def update_note_partial(note_id: int, updates: dict):
    existing = notes_db[note_id]
    updated = existing.model_copy(update=updates)
    notes_db[note_id] = updated
    return updated


@app.delete("/notes/{note_id}")
def delete_note(note_id: int):
    del notes_db[note_id]
    return {"deleted": note_id}
