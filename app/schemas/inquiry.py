from pydantic import BaseModel, Field
from typing import List, Optional

class ScreenResponse(BaseModel):
    id: int
    title: str
    catchphrase: Optional[str] = None
    description: Optional[str] = None
    preview: str

class InquiryResponse(BaseModel):
    id: int
    name: str
    email: str
    inquiry: str
    answers: Optional[str] = Field(default=None)  # Make answers optional
    status: int
    screens: List[ScreenResponse]

    class Config:
        orm_mode = True