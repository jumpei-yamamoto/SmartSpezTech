from pydantic import BaseModel
from typing import List, Optional, Dict, Union, Any

class SimulationResult(BaseModel):
    requirements_specification: str
    requirements_definition: str
    screens: List[str]
    estimate_develop: str
    answers: Dict[str, Optional[Union[str, List[str]]]]

class SimulationData(BaseModel):
    title: str
    text: str
    screen_description: str
    html: str  # Changed from List[str] to str
    # answers: Dict[str, Any]

class SimulationDataList(BaseModel):
    simulationData: List[SimulationData]

class InquiryRequest(BaseModel):
    name: str
    email: str
    message: str
    simulationData: SimulationData  # Changed from SimulationDataList to List[SimulationData]

class EstimateRequest(BaseModel):
    answers: Dict[str, Any]


class PreviewRequest(BaseModel):
    answers: Dict[str, Any]

