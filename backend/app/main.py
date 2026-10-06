from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import APP_TITLE, APP_TAGLINE, DISCLAIMER
from app.api.routes import router as api_router

app = FastAPI(
    title=APP_TITLE,
    description=f"{APP_TAGLINE}\n\n{DISCLAIMER}",
    version="1.0.0"
)

# CORS middleware for React/Vite development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.get("/")
def root():
    return {
        "name": APP_TITLE,
        "tagline": APP_TAGLINE,
        "status": "HEALTHY",
        "docs_url": "/docs",
        "api_prefix": "/api",
        "disclaimer": DISCLAIMER
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}
