from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.estimate import Estimate, Screen, EstimateStatus, Event, Entity, Relation, AIResponse as AIResponseModel  # SQLAlchemy model
from app.schemas.inquiry import InquiryResponse, ScreenResponse
from pydantic import BaseModel, Field

router = APIRouter()

@router.get("/api/inquiries", response_model=List[InquiryResponse])
def get_inquiries(db: Session = Depends(get_db)):
    try:
        estimates = db.query(Estimate).all()
        
        response_data = []
        
        for estimate in estimates:
            screens = db.query(Screen).filter(Screen.estimate_id == estimate.id).all()
            
            screen_responses = [
                ScreenResponse(
                    id=screen.id,
                    title=screen.title,
                    catchphrase=screen.catchphrase or "",  # None を空文字列に変換
                    description=screen.description or "",  # None を空文字列に変換
                    preview=screen.preview or ""  # preview も同様に処理
                ) for screen in screens
            ]
            
            response_data.append(
                InquiryResponse(
                    id=estimate.id,
                    name=estimate.name,
                    email=estimate.email,
                    inquiry=estimate.inquiry,
                    answers=estimate.answers or "",  # None を空文字列に変換
                    status=estimate.status,
                    screens=screen_responses
                )
            )
        
        return response_data
    except Exception as e:
        print(f"Error in get_inquiries: {str(e)}")  # デバッグ用に追加
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/api/inquirydetail/{inquiry_id}", response_model=InquiryResponse)
def get_inquiry(inquiry_id: int, db: Session = Depends(get_db)):
    try:
        estimate = db.query(Estimate).filter(Estimate.id == inquiry_id).first()
        
        if not estimate:
            raise HTTPException(status_code=404, detail="Inquiry not found")
        
        screens = db.query(Screen).filter(Screen.estimate_id == estimate.id).all()
        
        screen_responses = [
            ScreenResponse(
                id=screen.id,
                title=screen.title,
                catchphrase=screen.catchphrase or "",
                description=screen.description or "",
                preview=screen.preview or ""
            ) for screen in screens
        ]
        
        response_data = InquiryResponse(
            id=estimate.id,
            name=estimate.name,
            email=estimate.email,
            inquiry=estimate.inquiry,
            answers=estimate.answers or "",
            status=estimate.status,
            screens=screen_responses
        )
        
        return response_data
    except Exception as e:
        print(f"Error in get_inquiry: {str(e)}")  # デバッグ用
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

class ScreenData(BaseModel):
    id: int
    name: str
    html: str
    events: List[str]

class EventData(BaseModel):
    id: int
    name: str
    screen: str
    process: str

class EntityData(BaseModel):
    id: int
    name: str
    attributes: List[str]

class RelationData(BaseModel):
    id: int
    from_: str = Field(alias="from")
    to: str
    type: str

class AIResponse(BaseModel):
    features: List[str]
    requirements: List[str]

class AcceptOrderRequest(BaseModel):
    inquiryId: int
    screens: List[ScreenData]
    events: List[EventData]
    entities: List[EntityData]
    relations: List[RelationData]
    aiResponse: AIResponse

# When interacting with the database, use AIResponseModel instead of AIResponse
@router.post("/api/accept-order")
def accept_order(request: AcceptOrderRequest, db: Session = Depends(get_db)):
    estimate = db.query(Estimate).filter(Estimate.id == request.inquiryId).first()
    if not estimate:
        raise HTTPException(status_code=404, detail="Estimate not found")
    
    estimate.status = EstimateStatus.ACCEPTED

    # Screens
    for screen_data in request.screens:
        screen = Screen(
            estimate_id=estimate.id,
            title=screen_data.name,
            preview=screen_data.html
        )
        db.add(screen)

    # Events
    for event_data in request.events:
        event = Event(
            estimate_id=estimate.id,
            name=event_data.name,
            screen=event_data.screen,
            process=event_data.process
        )
        db.add(event)

    # Entities
    for entity_data in request.entities:
        entity = Entity(
            estimate_id=estimate.id,
            name=entity_data.name,
            attributes=entity_data.attributes
        )
        db.add(entity)

    # Relations
    for relation_data in request.relations:
        relation = Relation(
            estimate_id=estimate.id,
            from_=relation_data.from_,
            to=relation_data.to,
            type=relation_data.type
        )
        db.add(relation)

    # AI Response
    ai_response = AIResponseModel(
        estimate_id=estimate.id,
        features=request.aiResponse.features,
        requirements=request.aiResponse.requirements
    )
    db.add(ai_response)

    db.commit()
    
    return {"message": "Order accepted and data saved successfully"}

# ... 既存のコード ...
