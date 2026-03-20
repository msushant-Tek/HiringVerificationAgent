import io
from typing import Optional

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extracts text from a PDF document using PyMuPDF (fitz).
    In a more advanced setup, this could use Google Cloud Document AI for OCR.
    """
    try:
        import fitz # PyMuPDF
        
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
            
        return text
    except ImportError:
        return "PyMuPDF not installed. Cannot extract text from PDF."
    except Exception as e:
        return f"Error extracting text from PDF: {str(e)}"
        
class OCRService:
    @staticmethod
    async def process_document(file_content: bytes, filename: str) -> str:
        """
        Processes a document (like a resume PDF) and returns extracted text.
        """
        if filename.lower().endswith(".pdf"):
            return extract_text_from_pdf(file_content)
        else:
            # Fallback for plain text or handle other formats
            try:
                return file_content.decode('utf-8')
            except UnicodeDecodeError:
                return "Unsupported file format or unreadable content."
