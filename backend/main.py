"""WhyBoard API — FastAPI entry point."""

import logging

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.config import settings
from backend.intelligence import analyze_data
from backend.parser import (
    ParseError,
    parse_csv,
    parse_pasted_data,
    prepare_data_for_ai,
    validate_csv_size,
    validate_paste_length,
)
from backend.schema import AnalyzeResponse

logger = logging.getLogger(__name__)

app = FastAPI(
    title="WhyBoard API",
    description="Narrative intelligence from raw data",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}


class PasteRequest(BaseModel):
    data: str
    context: str | None = None


@app.post("/api/analyze/csv", response_model=AnalyzeResponse)
async def analyze_csv(
    file: UploadFile = File(...),
    context: str | None = None,
):
    """Analyze an uploaded CSV file and return narrative intelligence."""
    try:
        file_bytes = await file.read()

        validate_csv_size(file_bytes, max_mb=settings.MAX_CSV_SIZE_MB)

        df = parse_csv(file_bytes)
        cleaned_df, summary = prepare_data_for_ai(df)

        logger.info(
            "CSV analyzed: %d rows x %d cols",
            len(cleaned_df),
            len(cleaned_df.columns),
        )

        return await analyze_data(
            data_summary=summary,
            row_count=len(df),
            column_count=len(df.columns),
            context=context,
        )

    except ParseError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/analyze/paste", response_model=AnalyzeResponse)
async def analyze_paste(request: PasteRequest):
    """Analyze pasted tabular data and return narrative intelligence."""
    try:
        validate_paste_length(request.data, max_chars=settings.MAX_PASTE_CHARS)

        df = parse_pasted_data(request.data)
        cleaned_df, summary = prepare_data_for_ai(df)

        logger.info(
            "Paste analyzed: %d rows x %d cols",
            len(cleaned_df),
            len(cleaned_df.columns),
        )

        return await analyze_data(
            data_summary=summary,
            row_count=len(df),
            column_count=len(df.columns),
            context=request.context,
        )

    except ParseError as e:
        raise HTTPException(status_code=400, detail=str(e))
