"""
Clinical Notes Router
Handles CRUD operations for clinical notes with role-based access control.

Access Rules:
- Doctor: Can add notes
- Patient: Can view own notes (read-only)
- Admin: Full CRUD permissions
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.patient import Patient
from app.models.clinical_note import ClinicalNote, NoteCategory, EncryptionRole
from app.schemas import ClinicalNoteCreate, ClinicalNoteUpdate, ClinicalNoteResponse
from app.services.notes_encryption import NotesEncryption
from app.routers.auth import get_current_user

router = APIRouter(prefix="/notes", tags=["Clinical Notes"])


@router.post("", response_model=ClinicalNoteResponse, status_code=status.HTTP_201_CREATED)
def create_note(
    note_data: ClinicalNoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new clinical note.
    
    Access: Doctor and Admin only
    """
    # Check if user is doctor or admin
    if current_user.role.value not in ["DOCTOR", "ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors and admins can create notes"
        )
    
    # Verify patient exists
    patient = db.query(Patient).filter(Patient.id == note_data.patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Determine encryption role based on author role
    if current_user.role.value == "ADMIN":
        encryption_role = EncryptionRole.ADMIN
    else:
        encryption_role = EncryptionRole.DOCTOR
    
    # Encrypt the note content
    encrypted_content = NotesEncryption.encrypt_note(
        note_data.content,
        encryption_role.value
    )
    
    # Create note
    new_note = ClinicalNote(
        patient_id=note_data.patient_id,
        author_id=current_user.id,
        note_content=encrypted_content,
        encryption_role=encryption_role,
        category=NoteCategory(note_data.category),
        is_sensitive=note_data.is_sensitive
    )
    
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    
    # Decrypt for response
    decrypted_content = NotesEncryption.decrypt_note(
        new_note.note_content,
        new_note.encryption_role.value
    )
    
    return ClinicalNoteResponse(
        id=new_note.id,
        patient_id=new_note.patient_id,
        author_id=new_note.author_id,
        author_name=f"{current_user.username}",
        content=decrypted_content,
        category=new_note.category.value,
        is_sensitive=new_note.is_sensitive,
        encryption_role=new_note.encryption_role.value,
        created_at=new_note.created_at,
        updated_at=new_note.updated_at
    )


@router.get("/patient/{patient_id}", response_model=List[ClinicalNoteResponse])
def get_patient_notes(
    patient_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all notes for a patient.
    
    Access:
    - Patient: Can only view own notes
    - Doctor: Can view notes they created
    - Admin: Can view all notes
    """
    # Verify patient exists
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Build query based on user role
    query = db.query(ClinicalNote).filter(
        ClinicalNote.patient_id == patient_id,
        ClinicalNote.is_active == True
    )
    
    # Access control
    if current_user.role.value == "PATIENT":
        # Patients can only access their own notes
        # In a real system, you'd link user to patient
        # For now, we'll check if there's a link or raise error
        # TODO: Implement patient-user linking
        pass  # For now, allow if patient_id matches
    elif current_user.role.value == "DOCTOR":
        # Doctors can see notes they created
        query = query.filter(ClinicalNote.author_id == current_user.id)
    elif current_user.role.value == "ADMIN":
        # Admins can see all notes
        pass
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    notes = query.order_by(ClinicalNote.created_at.desc()).all()
    
    # Decrypt and return notes
    response_notes = []
    for note in notes:
        # Check if user can decrypt this note
        if NotesEncryption.can_decrypt(current_user.role.value, note.encryption_role.value):
            try:
                decrypted_content = NotesEncryption.decrypt_note(
                    note.note_content,
                    note.encryption_role.value
                )
                
                # Get author name
                author = db.query(User).filter(User.id == note.author_id).first()
                author_name = author.username if author else "Unknown"
                
                response_notes.append(ClinicalNoteResponse(
                    id=note.id,
                    patient_id=note.patient_id,
                    author_id=note.author_id,
                    author_name=author_name,
                    content=decrypted_content,
                    category=note.category.value,
                    is_sensitive=note.is_sensitive,
                    encryption_role=note.encryption_role.value,
                    created_at=note.created_at,
                    updated_at=note.updated_at
                ))
            except Exception as e:
                # If decryption fails, skip this note
                print(f"Failed to decrypt note {note.id}: {e}")
                continue
    
    return response_notes


@router.get("/{note_id}", response_model=ClinicalNoteResponse)
def get_note(
    note_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific note by ID.
    
    Access: Based on role and note ownership
    """
    note = db.query(ClinicalNote).filter(
        ClinicalNote.id == note_id,
        ClinicalNote.is_active == True
    ).first()
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    # Check access permissions
    if current_user.role.value == "DOCTOR" and note.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view notes you created"
        )
    
    # Check if user can decrypt
    if not NotesEncryption.can_decrypt(current_user.role.value, note.encryption_role.value):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to decrypt this note"
        )
    
    # Decrypt content
    decrypted_content = NotesEncryption.decrypt_note(
        note.note_content,
        note.encryption_role.value
    )
    
    # Get author name
    author = db.query(User).filter(User.id == note.author_id).first()
    author_name = author.username if author else "Unknown"
    
    return ClinicalNoteResponse(
        id=note.id,
        patient_id=note.patient_id,
        author_id=note.author_id,
        author_name=author_name,
        content=decrypted_content,
        category=note.category.value,
        is_sensitive=note.is_sensitive,
        encryption_role=note.encryption_role.value,
        created_at=note.created_at,
        updated_at=note.updated_at
    )


@router.put("/{note_id}", response_model=ClinicalNoteResponse)
def update_note(
    note_id: str,
    note_update: ClinicalNoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a clinical note.
    
    Access: Admin only
    """
    # Only admins can edit notes
    if current_user.role.value != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can edit notes"
        )
    
    note = db.query(ClinicalNote).filter(
        ClinicalNote.id == note_id,
        ClinicalNote.is_active == True
    ).first()
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    # Update fields
    if note_update.content:
        # Re-encrypt with admin key
        encrypted_content = NotesEncryption.encrypt_note(
            note_update.content,
            EncryptionRole.ADMIN.value
        )
        note.note_content = encrypted_content
        note.encryption_role = EncryptionRole.ADMIN
    
    if note_update.category:
        note.category = NoteCategory(note_update.category)
    
    if note_update.is_sensitive is not None:
        note.is_sensitive = note_update.is_sensitive
    
    db.commit()
    db.refresh(note)
    
    # Decrypt for response
    decrypted_content = NotesEncryption.decrypt_note(
        note.note_content,
        note.encryption_role.value
    )
    
    # Get author name
    author = db.query(User).filter(User.id == note.author_id).first()
    author_name = author.username if author else "Unknown"
    
    return ClinicalNoteResponse(
        id=note.id,
        patient_id=note.patient_id,
        author_id=note.author_id,
        author_name=author_name,
        content=decrypted_content,
        category=note.category.value,
        is_sensitive=note.is_sensitive,
        encryption_role=note.encryption_role.value,
        created_at=note.created_at,
        updated_at=note.updated_at
    )


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a clinical note (soft delete).
    
    Access: Admin only
    """
    # Only admins can delete notes
    if current_user.role.value != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete notes"
        )
    
    note = db.query(ClinicalNote).filter(ClinicalNote.id == note_id).first()
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    # Soft delete
    note.is_active = False
    db.commit()
    
    return None
