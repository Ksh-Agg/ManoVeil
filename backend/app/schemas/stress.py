from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
from app.models.stress_score import ScoreCategory


class StressScoreRead(BaseModel):
    id: UUID
    user_id: UUID
    psychometric_score: float
    nlp_score: float
    fused_score: float
    category: ScoreCategory
    yellow_flag: bool
    shap_values: dict | None
    feature_values: dict | None
    model_version: str | None
    computed_at: datetime
    model_config = {"from_attributes": True}


class SHAPExplanation(BaseModel):
    score_id: UUID
    fused_score: float
    category: ScoreCategory
    feature_names: list[str]
    feature_values: list[float]
    shap_values: list[float]
    base_value: float
