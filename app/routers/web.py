"""
Web Interface Router

This module provides HTML-based web interface endpoints for the Password Manager.
"""

from uuid import UUID
from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.password_entry import PasswordEntryCreate, PasswordEntryUpdate
from app.services.password_entry_service import get_password_entry_service
from app.services.folder_service import get_folder_service

# Create web router
router = APIRouter(
    tags=["web"],
    responses={404: {"description": "Not found"}},
)


def get_templates(request: Request) -> Jinja2Templates:
    """Get templates from app state."""
    return request.app.state.templates


# TEMPORARY: Hardcoded user ID for testing (in real app, use authentication)
TEMP_USER_ID = UUID("00000000-0000-0000-0000-000000000001")


@router.get("/", response_class=HTMLResponse)
async def web_index(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Home page showing all password entries.
    """
    try:
        entry_service = get_password_entry_service(db)
        folder_service = get_folder_service(db)
        
        entries = entry_service.get_all_entries_for_user(TEMP_USER_ID)
        folders = folder_service.get_all_folders_for_user(TEMP_USER_ID)
        
        templates = get_templates(request)
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "entries": entries,
                "folders": folders,
                "title": "Password Manager"
            }
        )
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@router.get("/entries/create", response_class=HTMLResponse)
async def web_entries_create_form(
    request: Request,
    db: Session = Depends(get_db)
):
    """Display the create entry form."""
    try:
        folder_service = get_folder_service(db)
        folders = folder_service.get_all_folders_for_user(TEMP_USER_ID)
        
        templates = get_templates(request)
        return templates.TemplateResponse(
            "entries/create.html",
            {
                "request": request,
                "folders": folders,
                "title": "Create New Entry"
            }
        )
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@router.post("/entries/create")
async def web_entries_create_submit(
    request: Request,
    name: str = Form(..., min_length=1, max_length=100),
    username: str = Form(None, max_length=100),
    password: str = Form(None),
    website_url: str = Form(None, max_length=500),
    notes: str = Form(None),
    folder_id: str = Form(None),
    db: Session = Depends(get_db)
):
    """Process the create entry form submission."""
    try:
        entry_service = get_password_entry_service(db)
        
        # Convert folder_id if provided
        folder_uuid = UUID(folder_id) if folder_id and folder_id != "" else None
        
        entry_data = PasswordEntryCreate(
            name=name,
            username=username if username else None,
            password=password if password else None,
            website_url=website_url if website_url else None,
            notes=notes if notes else None,
            folder_id=folder_uuid
        )
        
        entry_service.create_entry(TEMP_USER_ID, entry_data)
        
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@router.get("/entries/{entry_id}", response_class=HTMLResponse)
async def web_entries_detail(
    request: Request,
    entry_id: UUID,
    db: Session = Depends(get_db)
):
    """Display entry details."""
    try:
        entry_service = get_password_entry_service(db)
        entry = entry_service.get_entry_by_id(entry_id, TEMP_USER_ID)
        
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Entry not found"
            )
        
        templates = get_templates(request)
        return templates.TemplateResponse(
            "entries/detail.html",
            {
                "request": request,
                "entry": entry,
                "title": entry.name
            }
        )
        
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@router.get("/entries/{entry_id}/edit", response_class=HTMLResponse)
async def web_entries_edit_form(
    request: Request,
    entry_id: UUID,
    db: Session = Depends(get_db)
):
    """Display the edit entry form."""
    try:
        entry_service = get_password_entry_service(db)
        folder_service = get_folder_service(db)
        
        entry = entry_service.get_entry_by_id(entry_id, TEMP_USER_ID)
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Entry not found"
            )
        
        folders = folder_service.get_all_folders_for_user(TEMP_USER_ID)
        
        templates = get_templates(request)
        return templates.TemplateResponse(
            "entries/edit.html",
            {
                "request": request,
                "entry": entry,
                "folders": folders,
                "title": f"Edit {entry.name}"
            }
        )
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@router.post("/entries/{entry_id}/edit")
async def web_entries_edit_submit(
    request: Request,
    entry_id: UUID,
    name: str = Form(..., min_length=1, max_length=100),
    username: str = Form(None, max_length=100),
    password: str = Form(None),
    website_url: str = Form(None, max_length=500),
    notes: str = Form(None),
    folder_id: str = Form(None),
    db: Session = Depends(get_db)
):
    """Process the edit entry form submission."""
    try:
        entry_service = get_password_entry_service(db)
        
        # Convert folder_id if provided
        folder_uuid = UUID(folder_id) if folder_id and folder_id != "" else None
        
        entry_data = PasswordEntryUpdate(
            name=name,
            username=username if username else None,
            password=password if password else None,
            website_url=website_url if website_url else None,
            notes=notes if notes else None,
            folder_id=folder_uuid
        )
        
        updated_entry = entry_service.update_entry(entry_id, TEMP_USER_ID, entry_data)
        
        if not updated_entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Entry not found"
            )
        
        return RedirectResponse(
            url=f"/entries/{entry_id}", 
            status_code=status.HTTP_303_SEE_OTHER
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@router.post("/entries/{entry_id}/delete")
async def web_entries_delete(
    entry_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete an entry."""
    try:
        entry_service = get_password_entry_service(db)
        deleted = entry_service.delete_entry(entry_id, TEMP_USER_ID)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Entry not found"
            )
        
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
        
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


# ==================== FOLDER ROUTES ====================

@router.get("/folders", response_class=HTMLResponse)
async def web_folders_list(
    request: Request,
    db: Session = Depends(get_db)
):
    """Display all folders."""
    try:
        folder_service = get_folder_service(db)
        folders = folder_service.get_all_folders_for_user(TEMP_USER_ID)
        
        templates = get_templates(request)
        return templates.TemplateResponse(
            "folders/list.html",
            {
                "request": request,
                "folders": folders,
                "title": "Folders"
            }
        )
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@router.get("/folders/create", response_class=HTMLResponse)
async def web_folders_create_form(request: Request):
    """Display the create folder form."""
    templates = get_templates(request)
    return templates.TemplateResponse(
        "folders/create.html",
        {
            "request": request,
            "title": "Create New Folder"
        }
    )


@router.post("/folders/create")
async def web_folders_create_submit(
    request: Request,
    name: str = Form(..., min_length=1, max_length=100),
    db: Session = Depends(get_db)
):
    """Process the create folder form submission."""
    try:
        from app.schemas.folder import FolderCreate
        folder_service = get_folder_service(db)
        
        folder_data = FolderCreate(name=name)
        folder_service.create_folder(TEMP_USER_ID, folder_data)
        
        return RedirectResponse(url="/folders", status_code=status.HTTP_303_SEE_OTHER)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@router.get("/folders/{folder_id}", response_class=HTMLResponse)
async def web_folders_detail(
    request: Request,
    folder_id: UUID,
    db: Session = Depends(get_db)
):
    """Display folder details with entries."""
    try:
        folder_service = get_folder_service(db)
        entry_service = get_password_entry_service(db)
        
        folder = folder_service.get_folder_by_id(folder_id, TEMP_USER_ID)
        if not folder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Folder not found"
            )
        
        # Get entries in this folder
        entries = entry_service.get_all_entries_for_user(TEMP_USER_ID, folder_id=folder_id)
        
        templates = get_templates(request)
        return templates.TemplateResponse(
            "folders/detail.html",
            {
                "request": request,
                "folder": folder,
                "entries": entries,
                "title": folder.name
            }
        )
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@router.post("/folders/{folder_id}/delete")
async def web_folders_delete(
    folder_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a folder."""
    try:
        folder_service = get_folder_service(db)
        deleted = folder_service.delete_folder(folder_id, TEMP_USER_ID)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Folder not found"
            )
        
        return RedirectResponse(url="/folders", status_code=status.HTTP_303_SEE_OTHER)
        
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )