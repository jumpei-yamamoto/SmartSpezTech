from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.estimate import Estimate, Screen, EstimateStatus
from pydantic import BaseModel

router = APIRouter()

class ScreenResponse(BaseModel):
    title: str
    catchphrase: Optional[str] = None
    description: Optional[str] = None
    preview: str

class OrderedEstimateResponse(BaseModel):
    id: int
    name: str
    email: str
    inquiry: str
    status: int
    screen: ScreenResponse

@router.get("/api/ordered_estimates", response_model=List[OrderedEstimateResponse])
def get_ordered_estimates(db: Session = Depends(get_db)):
    try:
        ordered_estimates = db.query(Estimate).filter(Estimate.status == EstimateStatus.ACCEPTED).all()
        print(ordered_estimates)
        result = []
        for estimate in ordered_estimates:
            screens = db.query(Screen).filter(Screen.estimate_id == estimate.id).all()
            for screen in screens:
                result.append(
                    OrderedEstimateResponse(
                        id=estimate.id,
                        name=estimate.name,
                        email=estimate.email,
                        inquiry=estimate.inquiry,
                        status=estimate.status,
                        screen=ScreenResponse(
                            title=screen.title,
                            catchphrase=screen.catchphrase or "",  # None の場合は空文字列に変換
                            description=screen.description or "",  # None の場合は空文字列に変換
                            preview=screen.preview
                        )
                    )
                )
        return result
    except Exception as e:
        print(f"Error in get_ordered_estimates: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")