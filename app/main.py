from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
import os
import tempfile
from typing import Optional
import PyPDF2
from openai import OpenAI
from pydantic import BaseModel
import io

from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise HTTPException(status_code=500, detail="OPENAI_API_KEY not found in environment variables")

client = OpenAI(api_key=api_key)

# Modele Pydantic
class AnalysisRequest(BaseModel):
    job_description: str

class AnalysisResponse(BaseModel):
    match_percentage: int
    strengths: list[str]
    weaknesses: list[str]
    suggestions: list[str]
    learning_suggestions: list[str]

app = FastAPI(
    title="Career Coach API",
    description="Backend API dla aplikacji Career Coach",
    version="1.0.0"
)

# Konfiguracja CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # W produkcji zmień na konkretne domeny
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Funkcje pomocnicze
def extract_text_from_pdf(file_content: bytes) -> str:
    """Wyciąga tekst z pliku PDF"""
    try:
        pdf_file = io.BytesIO(file_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Błąd podczas przetwarzania PDF: {str(e)}")

def extract_text_from_txt(file_content: bytes) -> str:
    """Wyciąga tekst z pliku TXT"""
    try:
        return file_content.decode('utf-8').strip()
    except UnicodeDecodeError:
        try:
            return file_content.decode('latin-1').strip()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Błąd podczas przetwarzania pliku tekstowego: {str(e)}")

async def analyze_cv_with_gpt(cv_text: str, job_description: str) -> AnalysisResponse:
    """Analizuje CV względem oferty pracy używając GPT-5"""
    try:
        prompt = f"""
Jesteś ekspertem HR i rekruterem IT. Przeanalizuj CV kandydata względem oferty pracy i przygotuj szczegółową ocenę.

CV KANDYDATA:
{cv_text}

OFERTA PRACY:
{job_description}

Przygotuj analizę w następującej strukturze (odpowiedz w języku polskim):

1. PROCENT DOPASOWANIA: [liczba od 0 do 100]

2. MOCNE STRONY:
- [wymień 3-5 głównych mocnych stron kandydata względem oferty]

3. SŁABE STRONY:
- [wymień 3-5 głównych braków w CV względem wymagań oferty]

4. SUGESTIE POPRAWEK CV:
- [wymień 3-5 konkretnych sugestii jak poprawić CV]

5. SUGESTIE NAUKI:
- [wymień 3-5 konkretnych technologii/umiejętności do nauki]

Odpowiedz w formacie JSON:
{{
    "match_percentage": [liczba],
    "strengths": ["punkt1", "punkt2", "punkt3"],
    "weaknesses": ["punkt1", "punkt2", "punkt3"],
    "suggestions": ["punkt1", "punkt2", "punkt3"],
    "learning_suggestions": ["punkt1", "punkt2", "punkt3"]
}}
"""

        response = client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": "Jesteś ekspertem HR i rekruterem IT. Zawsze odpowiadasz w formacie JSON."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # Parsowanie odpowiedzi JSON
        import json
        analysis_text = response.choices[0].message.content.strip()
        
        # Usuń markdown formatting jeśli istnieje
        if analysis_text.startswith("```json"):
            analysis_text = analysis_text[7:]
        if analysis_text.endswith("```"):
            analysis_text = analysis_text[:-3]
        
        analysis_data = json.loads(analysis_text)
        
        return AnalysisResponse(
            match_percentage=analysis_data["match_percentage"],
            strengths=analysis_data["strengths"],
            weaknesses=analysis_data["weaknesses"],
            suggestions=analysis_data["suggestions"],
            learning_suggestions=analysis_data["learning_suggestions"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd podczas analizy: {str(e)}")


@app.get("/")
async def root():
    """Root endpoint - podstawowa informacja o API"""
    return {
        "message": "Career Coach API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint - sprawdza czy serwis działa"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "career-coach-backend"
    }


@app.post("/upload-cv")
async def upload_cv(file: UploadFile = File(...)):
    """Upload CV w formacie PDF lub TXT"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Brak nazwy pliku")
    
    # Sprawdź rozszerzenie pliku
    file_extension = file.filename.lower().split('.')[-1]
    if file_extension not in ['pdf', 'txt']:
        raise HTTPException(
            status_code=400, 
            detail="Nieobsługiwany format pliku. Dozwolone: PDF, TXT"
        )
    
    try:
        # Wczytaj zawartość pliku
        file_content = await file.read()
        
        # Wyciągnij tekst w zależności od typu pliku
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


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_cv(
    cv_text: str = Form(...),
    job_description: str = Form(...)
):
    """Analizuje CV względem oferty pracy"""
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

