from pydantic import BaseModel
from typing import List, Optional

class Form(BaseModel):
    id: Optional[str] = None
    answers: List[str]