from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
from pathlib import Path
from app.database import get_db
from app.models.user import User
from app.models.dataset import Dataset
from app.models.ml_model import MLModel
from app.schemas.ml import (
    DatasetResponse, ModelTrainRequest, ModelResponse, 
    PredictionRequest, PredictionResponse, BatchPredictionRequest, BatchPredictionResponse
)
from app.utils.dependencies import get_current_user, require_permission
from app.ml.trainer import MLTrainer
from app.ml.predictor import Predictor
from app.config import get_settings
import pandas as pd

settings = get_settings()
router = APIRouter(prefix="/api/v1", tags=["ML Operations"])


@router.post("/datasets/upload", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
async def upload_dataset(
    file: UploadFile = File(...),
    name: str = Form(...),
    current_user: User = Depends(require_permission("upload:data")),
    db: Session = Depends(get_db)
):
    """Upload a dataset for training."""
    
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are supported"
        )
    
    # Create upload directory
    upload_dir = Path(settings.UPLOAD_DIR) / f"tenant_{current_user.tenant_id}"
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Save file
    file_path = upload_dir / f"{name}_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Get dataset info
    try:
        df = pd.read_csv(file_path)
        row_count = len(df)
        column_count = len(df.columns)
    except Exception as e:
        os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid CSV file: {str(e)}"
        )
    
    # Create dataset record
    db_dataset = Dataset(
        tenant_id=current_user.tenant_id,
        name=name,
        file_path=str(file_path),
        row_count=row_count,
        column_count=column_count,
        uploaded_by=current_user.id
    )
    
    db.add(db_dataset)
    db.commit()
    db.refresh(db_dataset)
    
    return db_dataset


@router.get("/datasets", response_model=List[DatasetResponse])
async def list_datasets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all datasets for current tenant."""
    datasets = db.query(Dataset).filter(Dataset.tenant_id == current_user.tenant_id).all()
    return datasets


@router.post("/models/train", response_model=ModelResponse, status_code=status.HTTP_201_CREATED)
async def train_model(
    train_request: ModelTrainRequest,
    current_user: User = Depends(require_permission("write:models")),
    db: Session = Depends(get_db)
):
    """Train a new ML model."""
    
    # Get dataset
    dataset = db.query(Dataset).filter(
        Dataset.id == train_request.dataset_id,
        Dataset.tenant_id == current_user.tenant_id
    ).first()
    
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    # Check if model with same name exists
    existing_models = db.query(MLModel).filter(
        MLModel.tenant_id == current_user.tenant_id,
        MLModel.name == train_request.name
    ).all()
    
    # Generate version
    if not existing_models:
        version = "v1.0.0"
    else:
        # Increment minor version
        latest_version = max([m.version for m in existing_models])
        major, minor, patch = latest_version.replace('v', '').split('.')
        version = f"v{major}.{int(minor) + 1}.{patch}"
    
    # Create model record (status: training)
    db_model = MLModel(
        tenant_id=current_user.tenant_id,
        name=train_request.name,
        version=version,
        algorithm=train_request.algorithm,
        dataset_id=dataset.id,
        model_path="",  # Will be updated after training
        status="training",
        created_by=current_user.id
    )
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    
    try:
        # Train model
        trainer = MLTrainer(
            tenant_id=current_user.tenant_id,
            model_name=train_request.name,
            storage_dir=settings.MODEL_DIR
        )
        
        metrics = trainer.train(
            file_path=dataset.file_path,
            target_column=train_request.target_column,
            algorithm=train_request.algorithm,
            test_size=train_request.test_size
        )
        
        # Save model
        model_path, scaler_path = trainer.save_model(version)
        
        # Update model record
        db_model.model_path = model_path
        db_model.scaler_path = scaler_path
        db_model.accuracy = metrics["accuracy"]
        db_model.f1_score = metrics["f1_score"]
        db_model.precision_score = metrics["precision"]
        db_model.recall_score = metrics["recall"]
        db_model.status = "active"
        
        db.commit()
        db.refresh(db_model)
        
        return db_model
        
    except Exception as e:
        # Update status to failed
        db_model.status = "failed"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Model training failed: {str(e)}"
        )


@router.get("/models", response_model=List[ModelResponse])
async def list_models(
    current_user: User = Depends(require_permission("read:models")),
    db: Session = Depends(get_db)
):
    """List all models for current tenant."""
    models = db.query(MLModel).filter(
        MLModel.tenant_id == current_user.tenant_id
    ).order_by(MLModel.created_at.desc()).all()
    return models


@router.get("/models/{model_id}", response_model=ModelResponse)
async def get_model(
    model_id: int,
    current_user: User = Depends(require_permission("read:models")),
    db: Session = Depends(get_db)
):
    """Get model details."""
    model = db.query(MLModel).filter(
        MLModel.id == model_id,
        MLModel.tenant_id == current_user.tenant_id
    ).first()
    
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    return model


@router.post("/predict", response_model=PredictionResponse)
async def predict(
    prediction_request: PredictionRequest,
    current_user: User = Depends(require_permission("predict")),
    db: Session = Depends(get_db)
):
    """Make a prediction using a trained model."""
    
    # Get model
    model = db.query(MLModel).filter(
        MLModel.id == prediction_request.model_id,
        MLModel.tenant_id == current_user.tenant_id,
        MLModel.status == "active"
    ).first()
    
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found or not active"
        )
    
    try:
        # Load predictor
        predictor = Predictor(
            model_path=model.model_path,
            scaler_path=model.scaler_path,
            tenant_id=current_user.tenant_id,
            model_name=model.name
        )
        
        # Make prediction
        result = predictor.predict_single(prediction_request.features)
        
        # Save prediction to audit trail
        from app.models.ml_model import Prediction
        import json
        
        db_prediction = Prediction(
            tenant_id=current_user.tenant_id,
            model_id=model.id,
            input_data=json.dumps(prediction_request.features),
            prediction=json.dumps(result["prediction"]),
            confidence=result["confidence"]
        )
        db.add(db_prediction)
        db.commit()
        
        return {
            **result,
            "model_id": model.id,
            "model_version": model.version
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )


@router.post("/predict/batch", response_model=BatchPredictionResponse)
async def predict_batch(
    batch_request: BatchPredictionRequest,
    current_user: User = Depends(require_permission("predict")),
    db: Session = Depends(get_db)
):
    """Make batch predictions."""
    
    # Get model
    model = db.query(MLModel).filter(
        MLModel.id == batch_request.model_id,
        MLModel.tenant_id == current_user.tenant_id,
        MLModel.status == "active"
    ).first()
    
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found or not active"
        )
    
    try:
        # Load predictor
        predictor = Predictor(
            model_path=model.model_path,
            scaler_path=model.scaler_path,
            tenant_id=current_user.tenant_id,
            model_name=model.name
        )
        
        # Make predictions
        results = predictor.predict_batch(batch_request.features_list)
        
        return {
            "predictions": results,
            "model_id": model.id,
            "model_version": model.version,
            "count": len(results)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch prediction failed: {str(e)}"
        )
