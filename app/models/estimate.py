from pydantic import BaseModel
from typing import Dict, Any

class EstimateRequest(BaseModel):
    answers: Dict[str, Any]