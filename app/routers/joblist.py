from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from app.database import get_db
from app.models.estimate import Estimate, Screen, EstimateStatus, Event
from pydantic import BaseModel

router = APIRouter()

class ScreenResponse(BaseModel):
    id: int  # Screen IDを追加
    title: str
    text: Optional[str] = None
    description: Optional[str] = None
    preview: str

class EventResponse(BaseModel):
    id: int
    name: str
    screen: str
    process: str

class OrderedEstimateResponse(BaseModel):
    id: int
    name: str
    email: str
    inquiry: str
    status: int
    screens: List[ScreenResponse]  # 複数のScreenを返すように変更
    events: List[EventResponse]  # 複数のEventを返すように変更

@router.get("/api/ordered_estimates", response_model=List[OrderedEstimateResponse])
def get_ordered_estimates(db: Session = Depends(get_db)):
    try:
        ordered_estimates = db.query(Estimate).options(
            joinedload(Estimate.screens),
            joinedload(Estimate.events)
        ).filter(Estimate.status == EstimateStatus.ACCEPTED).all()

        result = []
        for estimate in ordered_estimates:
            screen_responses = [
                ScreenResponse(
                    id=screen.id,  # Screen モデルの id を使用
                    title=screen.title,  # Screen モデルの title を使用
                    text=screen.text or "",
                    description=screen.description or "",
                    preview=screen.preview
                ) for screen in estimate.screens
            ] if estimate.screens else []

            event_responses = [
                EventResponse(
                    id=event.id,
                    name=event.name,
                    screen=event.screen,
                    process=event.process
                ) for event in estimate.events
            ] if estimate.events else []

            result.append(
                OrderedEstimateResponse(
                    id=estimate.id,  # これが案件番号（Estimate ID）になります
                    name=estimate.name,
                    email=estimate.email,
                    inquiry=estimate.inquiry,
                    status=estimate.status,
                    screens=screen_responses,
                    events=event_responses
                )
            )
        return result
    except Exception as e:
        print(f"Error in get_ordered_estimates: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# _is_more_informative 関数は不要になったため削除
