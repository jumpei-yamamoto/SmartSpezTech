from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.estimate import Estimate, Screen
from app.schemas.inquiry import InquiryResponse, ScreenResponse


router = APIRouter()

@router.get("/api/inquiries", response_model=List[InquiryResponse])
def get_inquiries(db: Session = Depends(get_db)):
    try:
        # estimate_dataテーブルから全てのデータを取得
        estimates = db.query(Estimate).all()
        
        # None を空文字列に変換
        for estimate in estimates:
            estimate.answers = estimate.answers or ""  # None を空文字列に変換
        
        # レスポンス用のリストを作成
        response_data = []
        
        for estimate in estimates:
            # 各estimateに関連するscreenを取得
            screens = db.query(Screen).filter(Screen.estimate_id == estimate.id).all()
            
            # ScreenResponseオブジェクトのリストを作成
            screen_responses = [
                ScreenResponse(
                    id=screen.id,
                    title=screen.title,
                    catchphrase=screen.catchphrase,
                    description=screen.description,
                    preview=screen.preview
                ) for screen in screens
            ]
            
            # InquiryResponseオブジェクトを作成し、リストに追加
            response_data.append(
                InquiryResponse(
                    id=estimate.id,
                    name=estimate.name,
                    email=estimate.email,
                    inquiry=estimate.inquiry,
                    answers=estimate.answers,
                    status=estimate.status,
                    screens=screen_responses
                )
            )
        
        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# ... 既存のコード ...
