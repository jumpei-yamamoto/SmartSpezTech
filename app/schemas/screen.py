from pydantic import BaseModel
from typing import Dict, Any

class ScreenData(BaseModel):
    # 画面詳細データのフィールドを定義
    pass

class ScreenDetailsRequest(BaseModel):
    screen: str
    answers: Dict[str, Any]