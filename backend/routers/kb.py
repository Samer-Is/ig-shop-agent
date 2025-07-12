from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Request
from typing import List
from pydantic import BaseModel
from database import get_database, DatabaseService
from auth_middleware import get_current_user_id, require_auth
import logging
import os
import uuid

logger = logging.getLogger(__name__)

router = APIRouter()

class KBDocumentResponse(BaseModel):
    id: str
    title: str
    file_uri: str

# Dependency to get database connection
async def get_db() -> DatabaseService:
    """Get database connection"""
    return await get_database()

@router.get("/", response_model=List[KBDocumentResponse])
async def get_knowledge_base(request: Request, db: DatabaseService = Depends(get_db)):
    """Get all knowledge base documents"""
    try:
        # Get current user ID
        user_id = get_current_user_id(request)
        if not user_id:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        documents = await db.fetch_all(
            "SELECT id, title, content as file_uri FROM kb_documents WHERE user_id = $1 ORDER BY created_at DESC",
            user_id
        )
        return [KBDocumentResponse(
            id=doc["id"],
            title=doc["title"],
            file_uri=doc["file_uri"]
        ) for doc in documents]
        
    except Exception as e:
        logger.error(f"Error getting knowledge base: {e}")
        raise HTTPException(status_code=500, detail="Failed to get knowledge base documents")

@router.post("/upload")
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    db: DatabaseService = Depends(get_db)
):
    """Upload a document to the knowledge base"""
    try:
        # Get current user ID
        user_id = get_current_user_id(request)
        if not user_id:
            raise HTTPException(status_code=401, detail="Authentication required")
        # Validate file type
        allowed_types = ["application/pdf", "text/plain", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail="Invalid file type. Only PDF, TXT, and DOCX files are allowed."
            )
        
        # Generate unique filename and ID
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        doc_id = str(uuid.uuid4())
        
        # For now, we'll store a placeholder URI
        # In production, this would upload to Azure Blob Storage
        file_uri = f"https://storage.example.com/kb/{unique_filename}"
        
        # Read file content (for text files)
        content = ""
        if file.content_type == "text/plain":
            content = (await file.read()).decode('utf-8')
        else:
            content = f"Binary file: {file.filename}"
        
        # Create database record
        await db.execute_query(
            "INSERT INTO kb_documents (id, user_id, title, content) VALUES ($1, $2, $3, $4)",
            doc_id,
            user_id,
            file.filename,
            content
        )
        
        return {
            "message": "Document uploaded successfully",
            "id": doc_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload document")

@router.delete("/{doc_id}")
async def delete_document(doc_id: str, request: Request, db: DatabaseService = Depends(get_db)):
    """Delete a knowledge base document"""
    try:
        # Get current user ID
        user_id = get_current_user_id(request)
        if not user_id:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Check if document exists and belongs to user
        document = await db.fetch_one("SELECT id FROM kb_documents WHERE id = $1 AND user_id = $2", doc_id, user_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Delete document
        await db.execute_query("DELETE FROM kb_documents WHERE id = $1 AND user_id = $2", doc_id, user_id)
        
        return {"message": "Document deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete document") 