from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ValidationError
from typing import List, Dict, Any
from app.services.openai_service import generate_ai_estimate
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class Screen(BaseModel):
    id: int
    name: str
    html: str
    events: List[str]

class Event(BaseModel):
    id: int
    name: str
    screen: str
    process: str

class Entity(BaseModel):
    id: int
    name: str
    attributes: List[str]

class Relation(BaseModel):
    id: int
    from_: str
    to: str
    type: str

class OrderCheckRequest(BaseModel):
    screens: List[Screen]
    events: List[Event]
    entities: List[Entity]
    relations: List[Relation]

@router.post("/api/estimate")
async def order_check(request: OrderCheckRequest):
    try:
        ai_estimate = await generate_ai_estimate(request.dict())
        return ai_estimate
    except ValueError as ve:
        logger.error(f"Error processing AI response: {str(ve)}")
        raise HTTPException(status_code=500, detail="Error processing AI response")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")