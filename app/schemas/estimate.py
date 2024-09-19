from pydantic import BaseModel
from typing import List, Optional, Dict, Union, Any

class SimulationResult(BaseModel):
    requirements_specification: str
    requirements_definition: str
    screens: List[str]
    estimate_develop: str
    answers: Dict[str, Optional[Union[str, List[str]]]]

class InquiryRequest(BaseModel):
    name: str
    email: str
    message: str
    simulationResult: SimulationResult

class EstimateRequest(BaseModel):
    answers: Dict[str, Any]


class PreviewRequest(BaseModel):
    answers: Dict[str, Any]

# 他のスキーマ定義...
