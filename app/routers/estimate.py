from fastapi import APIRouter, HTTPException
from app.schemas.estimate import EstimateRequest, InquiryRequest, PreviewRequest
from app.services.estimate import generate_estimate, save_inquiry_data, generate_preview

router = APIRouter()

@router.post("/estimate")
async def estimate(request: EstimateRequest):
    return await generate_estimate(request.answers)

@router.post("/submit_inquiry")
async def submit_inquiry(request: InquiryRequest):
    try:
        await save_inquiry_data(request)
        return {"message": "Inquiry submitted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/preview")
async def estimate(request: PreviewRequest):
    return await generate_preview(request.answers)