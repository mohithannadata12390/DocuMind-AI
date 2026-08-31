import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.ingestion_service import IngestionService
from app.services.chunking_service import ChunkingService
from app.services.vector_store_service import VectorStoreService
from app.models.schemas import DocumentUploadResponse

router = APIRouter()
chunking_service = ChunkingService()
vector_store = VectorStoreService()

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF documents are supported.")
        
    try:
        content = await file.read()
        document_id = str(uuid.uuid4())
        
        pages_data = IngestionService.extract_text_from_pdf(content, file.filename)
        if not pages_data:
            raise HTTPException(status_code=400, detail="No readable text found in document.")
            
        chunks = chunking_service.create_chunks(pages_data, document_id)
        vector_store.add_chunks(chunks)
        
        return DocumentUploadResponse(
            document_id=document_id,
            filename=file.filename,
            total_pages=len(pages_data),
            total_chunks=len(chunks),
            status="indexed"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")
