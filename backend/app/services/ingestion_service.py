import io
from typing import List, Dict, Any
import pypdf
import pdfplumber

class IngestionService:
    @staticmethod
    def extract_text_from_pdf(file_bytes: bytes, filename: str) -> List[Dict[str, Any]]:
        """
        Extracts text page by page from a PDF with metadata preservation.
        Falls back to pdfplumber if pypdf encounters complex layouts or tables.
        """
        pages_data = []
        
        try:
            stream = io.BytesIO(file_bytes)
            reader = pypdf.PdfReader(stream)
            num_pages = len(reader.pages)
            pdfplumber_doc = None
            
            for idx in range(num_pages):
                try:
                    text = reader.pages[idx].extract_text() or ""
                except Exception:
                    # Fallback to pdfplumber for just this specific page
                    if pdfplumber_doc is None:
                        # Open a fresh stream for pdfplumber so it doesn't mess with pypdf's stream position
                        pdfplumber_doc = pdfplumber.open(io.BytesIO(file_bytes))
                    
                    try:
                        text = pdfplumber_doc.pages[idx].extract_text() or ""
                    except Exception:
                        text = ""
                
                # Clean up null bytes and weird unicode artifacts
                cleaned_text = text.replace("\x00", "").strip()
                if cleaned_text:
                    pages_data.append({
                        "page_number": idx + 1,
                        "text": cleaned_text,
                        "filename": filename
                    })
                    
            if pdfplumber_doc:
                pdfplumber_doc.close()
                
        except Exception:
            # If pypdf fails to even open the document, fallback entirely
            pages_data = [] # Clear any partially extracted pages to prevent duplicates
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                for idx, page in enumerate(pdf.pages):
                    text = page.extract_text() or ""
                    cleaned_text = text.replace("\x00", "").strip()
                    if cleaned_text:
                        pages_data.append({
                            "page_number": idx + 1,
                            "text": cleaned_text,
                            "filename": filename
                        })
                        
        return pages_data