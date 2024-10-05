from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.database import get_db
from app.models.estimate import Estimate, Screen, EstimateStatus, Event, Entity, Relation, AIResponse as AIResponseModel
from app.schemas.inquiry import InquiryResponse, ScreenResponse
from pydantic import BaseModel, Field, ValidationError
import logging

logger = logging.getLogger(__name__)

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
                    text=screen.text or "",  # None を空文字列に変換
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
                    # answers=estimate.answers or "",  # None を空文字列に変換
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
        
        # 最新の screens のみを取得
        screens = db.query(Screen).filter(Screen.estimate_id == estimate.id).order_by(Screen.title, Screen.id.desc()).distinct(Screen.title).all()
        
        screen_responses = [
            ScreenResponse(
                id=screen.id,
                title=screen.title,
                text=screen.text or "",
                description=screen.description or "",
                preview=screen.preview or ""
            ) for screen in screens
        ]
        
        response_data = InquiryResponse(
            id=estimate.id,
            name=estimate.name,
            email=estimate.email,
            inquiry=estimate.inquiry,
            # answers=estimate.answers or "",
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
    from_: str 
    to: str
    type: str


class AIResponse(BaseModel):
    features: List[str] = []
    requirements: List[str] = []

class EstimateData(BaseModel):
    estimate_hours: float
    features: List[str]
    requirements: List[str]

class ScreenEstimate(BaseModel):
    workload: str
    difficulty: int
    tests: List[str]

class EventEstimate(BaseModel):
    workload: str
    difficulty: int
    tests: List[str]

class DatabaseEstimate(BaseModel):
    workload: str
    difficulty: int
    tests: List[str]

class AIEstimate(BaseModel):
    screens: Dict[str, ScreenEstimate]
    events: Dict[str, EventEstimate]
    database: DatabaseEstimate

class AcceptOrderRequest(BaseModel):
    inquiryId: int
    screens: List[ScreenData]
    events: List[EventData]
    entities: List[EntityData]
    relations: List[RelationData]
    aiEstimate: AIEstimate

@router.post("/api/accept-order")
async def accept_order(request: AcceptOrderRequest, db: Session = Depends(get_db)):
    try:
        logger.info(f"Received accept order request: {request.dict()}")

        # エスティメートを取得
        estimate = db.query(Estimate).filter(Estimate.id == request.inquiryId).first()
        if not estimate:
            raise HTTPException(status_code=404, detail="Estimate not found")
        
        # エスティメートのステータスを更新
        estimate.status = EstimateStatus.ACCEPTED

        # Screensをデータベースに追加
        for screen_data in request.screens:
            screen = Screen(
                estimate_id=estimate.id,
                title=screen_data.name,
                preview=screen_data.html
            )
            db.add(screen)

        # Eventsをデータベースに追加
        for event_data in request.events:
            event = Event(
                estimate_id=estimate.id,
                name=event_data.name,
                screen=event_data.screen,
                process=event_data.process
            )
            db.add(event)

        # Entitiesをデータベースに追加
        for entity_data in request.entities:
            entity = Entity(
                estimate_id=estimate.id,
                name=entity_data.name,
                attributes=entity_data.attributes
            )
            db.add(entity)

        # Relationsをデータベースに追加
        for relation_data in request.relations:
            relation = Relation(
                estimate_id=estimate.id,
                from_=relation_data.from_,  
                to=relation_data.to,
                type=relation_data.type
            )
            db.add(relation)

        # AIResponseの保存
        # screens, events, databaseを辞書に変換
        ai_estimate = AIResponseModel(
            estimate_id=estimate.id,
            screens={k: v.dict() for k, v in request.aiEstimate.screens.items()},  # screensを辞書に変換
            events={k: v.dict() for k, v in request.aiEstimate.events.items()},    # eventsを辞書に変換
            database=request.aiEstimate.database.dict()  # databaseを辞書に変換
        )
        db.add(ai_estimate)

        # データベースにコミット
        db.commit()
        
        return {"message": "Order accepted and data saved successfully"}
    
    except ValidationError as e:
        logger.error(f"Validation error: {e.json()}")
        raise HTTPException(status_code=422, detail=e.errors())
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
