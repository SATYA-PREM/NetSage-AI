import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.cases import router as cases_router
from backend.api.diagnosis import router as diagnosis_router
from backend.api.reviews import router as reviews_router
from backend.api.dashboard import router as dashboard_router


def get_allowed_origins():
    origins = {
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    }

    env_origins = os.getenv("ALLOWED_ORIGINS", "")
    if env_origins:
        origins.update(origin.strip() for origin in env_origins.split(",") if origin.strip())

    frontend_url = os.getenv("FRONTEND_URL")
    if frontend_url:
        origins.add(frontend_url)

    vercel_url = os.getenv("VERCEL_URL")
    if vercel_url:
        origins.add(vercel_url)

    return sorted(origins)


app = FastAPI(
    title="NetSage AI",
    description="AI-assisted network troubleshooting system",
    version="1.0.0",
)


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

allowed_origins = get_allowed_origins()

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Routers
# ---------------------------------------------------------

app.include_router(
    cases_router,
    prefix="/api/cases",
    tags=["Cases"],
)

app.include_router(
    diagnosis_router,
    prefix="/api/diagnosis",
    tags=["Diagnosis"],
)

app.include_router(
    reviews_router,
    prefix="/api/reviews",
    tags=["Reviews"],
)

app.include_router(
    dashboard_router,
    prefix="/api/dashboard",
    tags=["Dashboard"],
)


# ---------------------------------------------------------
# Health
# ---------------------------------------------------------

@app.get("/")
def root():
    return {
        "name": "NetSage AI",
        "status": "running",
        "version": "1.0.0",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "netsage-ai-backend",
    }