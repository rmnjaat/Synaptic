"""Notes router."""
from fastapi import APIRouter, Depends, status
from app.schemas.note import NoteCreate, NoteUpdate, NoteRead
from app.schemas.common import APIResponse
from app.services.note import NoteService
from app.dependencies import get_note_service
from typing import List

router = APIRouter(prefix="/notes", tags=["Notes"])


@router.post("/create", response_model=APIResponse[NoteRead], status_code=status.HTTP_201_CREATED)
def create_note(payload: NoteCreate, svc: NoteService = Depends(get_note_service)):
    note = svc.create_note(payload.model_dump())
    return APIResponse.ok(data=NoteRead.model_validate(note), message="Note created.")


@router.put("/{note_id}", response_model=APIResponse[NoteRead])
def update_note(note_id: int, payload: NoteUpdate, svc: NoteService = Depends(get_note_service)):
    note = svc.update_note(note_id, payload.model_dump())
    return APIResponse.ok(data=NoteRead.model_validate(note), message="Note updated.")


@router.delete("/{note_id}", response_model=APIResponse[None])
def delete_note(note_id: int, svc: NoteService = Depends(get_note_service)):
    svc.delete_note(note_id)
    return APIResponse.ok(message="Note deleted.")


@router.get("/topic/{topic_id}", response_model=APIResponse[List[NoteRead]])
def get_notes_by_topic(topic_id: int, svc: NoteService = Depends(get_note_service)):
    notes = svc.get_notes_by_topic(topic_id)
    return APIResponse.ok(data=[NoteRead.model_validate(n) for n in notes])
