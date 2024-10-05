from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from app.database import get_db
from app.models.estimate import Estimate, EstimateStatus, AIResponse
from pydantic import BaseModel

router = APIRouter()

class AIResponseData(BaseModel):
    id: int
    screens: dict
    events: dict
    database: dict

class OrderedEstimateResponse(BaseModel):
    id: int
    name: str
    email: str
    inquiry: str
    status: int
    ai_response: Optional[AIResponseData]

@router.get("/api/ordered_estimates", response_model=List[OrderedEstimateResponse])
def get_ordered_estimates(db: Session = Depends(get_db)):
    try:
        ordered_estimates = db.query(Estimate).options(
            joinedload(Estimate.ai_response)
        ).filter(Estimate.status == EstimateStatus.ACCEPTED).all()

        result = []
        for estimate in ordered_estimates:
            ai_response_data = None
            if estimate.ai_response:
                ai_response_data = AIResponseData(
                    id=estimate.ai_response.id,
                    screens=estimate.ai_response.screens,
                    events=estimate.ai_response.events,
                    database=estimate.ai_response.database
                )

            result.append(
                OrderedEstimateResponse(
                    id=estimate.id,
                    name=estimate.name,
                    email=estimate.email,
                    inquiry=estimate.inquiry,
                    status=estimate.status,
                    ai_response=ai_response_data
                )
            )
        return result
    except Exception as e:
        print(f"Error in get_ordered_estimates: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
