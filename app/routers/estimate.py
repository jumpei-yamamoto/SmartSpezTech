from fastapi import APIRouter, HTTPException
from app.schemas.estimate import EstimateRequest
from app.services.estimate import generate_estimate

router = APIRouter()

@router.post("/estimate")
async def estimate(request: EstimateRequest):
    return await generate_estimate(request.answers)