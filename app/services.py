import json
from openai import OpenAI
from fastapi import HTTPException
from .config import OPENAI_API_KEY
from .models import AnalysisResponse

client = OpenAI(api_key=OPENAI_API_KEY)

async def analyze_cv_with_gpt(cv_text: str, job_description: str) -> AnalysisResponse:
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

        response = client.responses.parse(
            model="gpt-5",
            input=[{"role": "user", "content": prompt}],
            text_format=AnalysisResponse
        )
        
        return response.output_parsed
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd podczas analizy: {str(e)}")
