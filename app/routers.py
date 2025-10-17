from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from datetime import datetime, timezone
from .models import AnalysisResponse
from .services import analyze_cv_with_gpt
from .utils import extract_text_from_pdf, extract_text_from_txt

router = APIRouter()

@router.get("/")
async def root():
    return {
        "message": "Career Coach API",
        "version": "1.0.0",
        "status": "running"
    }

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "career-coach-backend"
    }

@router.post("/upload-cv")
async def upload_cv(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Brak nazwy pliku")
    
    file_extension = file.filename.lower().split('.')[-1]
    if file_extension not in ['pdf', 'txt']:
        raise HTTPException(
            status_code=400, 
            detail="Nieobsługiwany format pliku. Dozwolone: PDF, TXT"
        )
    
    try:
        file_content = await file.read()
        
        if file_extension == 'pdf':
            cv_text = extract_text_from_pdf(file_content)
        elif file_extension == 'txt':
            cv_text = extract_text_from_txt(file_content)
        
        if not cv_text.strip():
            raise HTTPException(status_code=400, detail="Nie udało się wyciągnąć tekstu z pliku")
        
        return {
            "success": True,
            "filename": file.filename,
            "text": cv_text,
            "message": "CV zostało pomyślnie przetworzone"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd podczas przetwarzania pliku: {str(e)}")

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_cv(
    cv_text: str = Form(...),
    job_description: str = Form(...)
):
    if not cv_text.strip():
        raise HTTPException(status_code=400, detail="CV nie może być puste")
    
    if not job_description.strip():
        raise HTTPException(status_code=400, detail="Opis oferty pracy nie może być pusty")
    
    try:
        analysis = await analyze_cv_with_gpt(cv_text, job_description)
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd podczas analizy: {str(e)}")
