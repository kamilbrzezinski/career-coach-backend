# Career Coach Backend

Backend API dla aplikacji Career Coach zbudowany w **Python + FastAPI**.

## 🚀 Technologie

- **Framework:** FastAPI
- **Python:** 3.9+
- **Server:** Uvicorn
- **Database:** PostgreSQL (Supabase)
- **Deployment:** Render

## 📁 Struktura projektu

```
career-coach-backend/
├── app/
│   ├── __init__.py
│   └── main.py          # Główna aplikacja FastAPI
├── requirements.txt      # Zależności Python
├── .gitignore           # Pliki ignorowane przez Git
└── README.md            # Ten plik
```

## 🛠️ Instalacja i uruchomienie

### 1. Utwórz wirtualne środowisko

```bash
python -m venv venv
source venv/bin/activate  # Na Windows: venv\Scripts\activate
```

### 2. Zainstaluj zależności

```bash
pip install -r requirements.txt
```

### 3. Uruchom serwer deweloperski

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Aplikacja będzie dostępna pod adresem: `http://localhost:8000`

## 📡 Endpointy

- `GET /` - Podstawowe informacje o API
- `GET /health` - Health check endpoint
- `GET /docs` - Automatyczna dokumentacja Swagger UI
- `GET /redoc` - Alternatywna dokumentacja ReDoc

## 🌐 Deployment na Render

1. Push kodu do repozytorium GitHub
2. Połącz Render z repozytorium
3. Skonfiguruj:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## 📝 Zmienne środowiskowe

W produkcji ustaw następujące zmienne:

```
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres
ENVIRONMENT=production
```

## 🔗 Linki

- [Dokumentacja FastAPI](https://fastapi.tiangolo.com/)
- [Render Dashboard](https://render.com)
- [Supabase Dashboard](https://supabase.com)
