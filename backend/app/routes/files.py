import io
from pathlib import Path

import pandas as pd
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import settings

router = APIRouter()

MAX_UPLOAD_BYTES = 5 * 1024 * 1024  # 5 MB keeps the demo fast and safe


@router.post("/files/upload")
async def upload_file(file: UploadFile = File(...)):
    file_name = Path(file.filename or "").name
    if not file_name.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed.")

    content = await file.read()
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File is too large. The limit is 5 MB.")

    try:
        df = pd.read_csv(io.BytesIO(content))
    except Exception:
        raise HTTPException(status_code=422, detail="Could not read this file as a CSV.")
    if df.empty or len(df.columns) == 0:
        raise HTTPException(status_code=422, detail="The CSV has no data.")

    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    (settings.upload_dir / file_name).write_bytes(content)
    return {"file": file_name, "rows": len(df), "columns": list(df.columns)}


@router.get("/files")
def list_files():
    return {"files": sorted(p.name for p in settings.upload_dir.glob("*.csv"))}


@router.delete("/files/{file_name}")
def delete_file(file_name: str):
    path = settings.upload_dir / Path(file_name).name
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found.")
    path.unlink()
    return {"deleted": path.name}