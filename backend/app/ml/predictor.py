import pandas as pd
from typing import Dict, Any, List
from app.ml.trainer import MLTrainer


class Predictor:
    """Prediction service for trained models."""
    
    def __init__(self, model_path: str, scaler_path: str, tenant_id: int, model_name: str):
        self.model_path = model_path
        self.scaler_path = scaler_path
        self.tenant_id = tenant_id
        self.model_name = model_name
        
        # Load model and preprocessing
        self.model, self.preprocessing = MLTrainer.load_model(model_path, scaler_path)
        self.scaler = self.preprocessing["scaler"]
        self.label_encoder = self.preprocessing.get("label_encoder")
        self.feature_names = self.preprocessing["feature_names"]
    
    def predict_single(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Make prediction for a single instance."""
        # Convert to DataFrame
        df = pd.DataFrame([features])
        
        # Use trainer's preprocessing logic
        trainer = MLTrainer(self.tenant_id, self.model_name)
        trainer.model = self.model
        trainer.scaler = self.scaler
        trainer.label_encoder = self.label_encoder
        trainer.feature_names = self.feature_names
        
        result = trainer.predict(df)
        
        # Extract single prediction
        prediction = result["predictions"][0]
        probabilities = result["probabilities"][0] if result["probabilities"] else None
        confidence = max(probabilities) if probabilities else None
        
        return {
            "prediction": prediction,
            "confidence": float(confidence) if confidence else None,
            "probabilities": probabilities
        }
    
    def predict_batch(self, features_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Make predictions for multiple instances."""
        # Convert to DataFrame
        df = pd.DataFrame(features_list)
        
        # Use trainer's preprocessing logic
        trainer = MLTrainer(self.tenant_id, self.model_name)
        trainer.model = self.model
        trainer.scaler = self.scaler
        trainer.label_encoder = self.label_encoder
        trainer.feature_names = self.feature_names
        
        result = trainer.predict(df)
        
        # Format results
        predictions = []
        for i in range(len(result["predictions"])):
            pred = result["predictions"][i]
            probs = result["probabilities"][i] if result["probabilities"] else None
            confidence = max(probs) if probs else None
            
            predictions.append({
                "prediction": pred,
                "confidence": float(confidence) if confidence else None,
                "probabilities": probs
            })
        
        return predictions
