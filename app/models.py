from pydantic import BaseModel

class AnalysisRequest(BaseModel):
    job_description: str

class AnalysisResponse(BaseModel):
    match_percentage: int
    strengths: list[str]
    weaknesses: list[str]
    suggestions: list[str]
    learning_suggestions: list[str]
