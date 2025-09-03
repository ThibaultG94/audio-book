from fastapi import APIRouter, HTTPException
from app.models.conversion import ConversionRequest, ConversionResponse, ConversionStatusResponse
from app.services.conversion_service import conversion_service

router = APIRouter(prefix="/api/convert", tags=["conversion"])

@router.post("/start", response_model=ConversionResponse)
async def start_conversion(request: ConversionRequest):
    try:
        job_id = conversion_service.start_conversion(
            file_id=request.file_id,
            voice_model=request.voice_model
        )
        return ConversionResponse(
            job_id=job_id,
            status="started",
            message="Conversion started successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{job_id}", response_model=ConversionStatusResponse)
async def get_status(job_id: str):
    try:
        return conversion_service.get_conversion_status(job_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Job not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
