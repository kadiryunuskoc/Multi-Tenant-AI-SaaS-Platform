from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class DatasetUpload(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)


class DatasetResponse(BaseModel):
    id: int
    tenant_id: int
    name: str
    file_path: str
    row_count: Optional[int]
    column_count: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ModelTrainRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    dataset_id: int
    target_column: str
    algorithm: str = Field(default="random_forest", pattern="^(random_forest|logistic_regression)$")
    test_size: float = Field(default=0.2, ge=0.1, le=0.5)


class ModelResponse(BaseModel):
    id: int
    tenant_id: int
    name: str
    version: str
    algorithm: Optional[str]
    accuracy: Optional[float]
    f1_score: Optional[float]
    precision_score: Optional[float]
    recall_score: Optional[float]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class PredictionRequest(BaseModel):
    model_id: int
    features: Dict[str, Any] = Field(..., description="Feature values as key-value pairs")


class BatchPredictionRequest(BaseModel):
    model_id: int
    features_list: List[Dict[str, Any]] = Field(..., description="List of feature dictionaries")


class PredictionResponse(BaseModel):
    prediction: Any
    confidence: Optional[float]
    probabilities: Optional[List[float]]
    model_id: int
    model_version: str
    
    model_config = {"protected_namespaces": ()}


class BatchPredictionResponse(BaseModel):
    predictions: List[Dict[str, Any]]
    model_id: int
    model_version: str
    count: int
    
    model_config = {"protected_namespaces": ()}
