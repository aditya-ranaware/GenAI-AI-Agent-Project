from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routes import ask, files

app = FastAPI(title="Data Analyst Agent API")

# CORS is only needed in development (React on port 5173, API on port 8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(files.router, prefix="/api")
app.include_router(ask.router, prefix="/api")

# Serve the charts the agent creates, e.g. /api/charts/chart_ab12cd34.png
settings.charts_dir.mkdir(parents=True, exist_ok=True)
app.mount("/api/charts", StaticFiles(directory=settings.charts_dir), name="charts")


@app.get("/api/health")
def health():
    return {"status": "ok"}


# Serve the built React app. The "static" folder exists only in Docker (or after a local build).
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

if STATIC_DIR.exists():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")

    @app.get("/{path:path}")
    def serve_frontend(path: str):
        if path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not found")
        file = (STATIC_DIR / path).resolve()
        if path and file.is_file() and STATIC_DIR in file.parents:
            return FileResponse(file)
        return FileResponse(STATIC_DIR / "index.html")