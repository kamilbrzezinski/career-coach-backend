import io
import pypdf
from fastapi import HTTPException

def extract_text_from_pdf(file_content: bytes) -> str:
    try:
        pdf_file = io.BytesIO(file_content)
        pdf_reader = pypdf.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Błąd podczas przetwarzania PDF: {str(e)}")

def extract_text_from_txt(file_content: bytes) -> str:
    try:
        return file_content.decode('utf-8').strip()
    except UnicodeDecodeError:
        try:
            return file_content.decode('latin-1').strip()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Błąd podczas przetwarzania pliku tekstowego: {str(e)}")
