from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.db.init_db import init_db
from app.api.v1.router import router as api_router

#app = FastAPI(title="Finance API",lifespan=lifespan)



@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup code
    init_db()  # create tables
    yield
    # shutdown code (optional)
    print("App shutting down...")

app = FastAPI(title="Finance API", lifespan=lifespan)
app.include_router(api_router, prefix="/api/v1")
frontend_dir = Path(__file__).resolve().parent / "frontend"
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")


@app.get("/")
def root():
    return FileResponse(frontend_dir / "index.html")


@app.get("/health")
def health():
    return {"message": "API is running", "environment": settings.ENV}
