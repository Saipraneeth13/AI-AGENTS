"""PDF text extraction using PyMuPDF (fitz)."""
import fitz

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extracts text from PDF file bytes."""
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text.strip()
    except Exception as e:
        print(f"PDF extraction error: {e}")
        return ""
