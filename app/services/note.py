"""NoteService — CRUD for learning notes."""
from fastapi import HTTPException
from app.repositories.note import NoteRepository


class NoteService:
    def __init__(self, repo: NoteRepository):
        self.repo = repo

    def create_note(self, note_data: dict):
        return self.repo.create(note_data)

    def update_note(self, note_id: int, update_data: dict):
        note = self.repo.get_by_id(note_id)
        if not note:
            raise HTTPException(status_code=404, detail={"success": False, "message": f"Note {note_id} not found."})
        return self.repo.update(note_id, {k: v for k, v in update_data.items() if v is not None})

    def delete_note(self, note_id: int) -> bool:
        if not self.repo.get_by_id(note_id):
            raise HTTPException(status_code=404, detail={"success": False, "message": f"Note {note_id} not found."})
        return self.repo.delete(note_id)

    def get_notes_by_topic(self, topic_id: int):
        return self.repo.get_by_topic_id(topic_id)
