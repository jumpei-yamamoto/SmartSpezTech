from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
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
    screens: List[ScreenResponse]

@router.get("/api/ordered_estimates", response_model=List[OrderedEstimateResponse])
def get_ordered_estimates(db: Session = Depends(get_db)):
    try:
        ordered_estimates = db.query(Estimate).options(
            joinedload(Estimate.screens)
        ).filter(Estimate.status == EstimateStatus.ACCEPTED).all()

        result = []
        for estimate in ordered_estimates:
            # Screenをtitleでグループ化し、最も情報が豊富なものを選択
            screen_dict = {}
            for screen in estimate.screens:
                if screen.title not in screen_dict or _is_more_informative(screen, screen_dict[screen.title]):
                    screen_dict[screen.title] = screen

            screen_responses = [
                ScreenResponse(
                    title=screen.title,
                    catchphrase=screen.catchphrase or "",
                    description=screen.description or "",
                    preview=screen.preview
                ) for screen in screen_dict.values()
            ]
            result.append(
                OrderedEstimateResponse(
                    id=estimate.id,
                    name=estimate.name,
                    email=estimate.email,
                    inquiry=estimate.inquiry,
                    status=estimate.status,
                    screens=screen_responses
                )
            )
        return result
    except Exception as e:
        print(f"Error in get_ordered_estimates: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

def _is_more_informative(screen1: Screen, screen2: Screen) -> bool:
    """
    screen1がscreen2よりも情報量が多いかどうかを判断する
    """
    if screen1.description and not screen2.description:
        return True
    if screen1.catchphrase and not screen2.catchphrase:
        return True
    return False
