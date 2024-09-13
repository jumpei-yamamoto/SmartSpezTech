from fastapi import APIRouter, HTTPException
from app.models.screen import ScreenDetailsRequest
from app.services.screen import get_screen_details

router = APIRouter()

@router.post("/screen_details")
async def screen_details(request: ScreenDetailsRequest):
    return await get_screen_details(request.screen, request.answers)