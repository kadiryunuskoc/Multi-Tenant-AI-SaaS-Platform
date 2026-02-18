import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
import joblib
import os
from pathlib import Path
from typing import Tuple, Dict, Any
import json


class MLTrainer:
    """Machine Learning model trainer with automatic feature engineering."""
    
    def __init__(self, tenant_id: int, model_name: str, storage_dir: str = "./storage/models"):
        self.tenant_id = tenant_id
        self.model_name = model_name
        self.storage_dir = Path(storage_dir)
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.feature_names = None
        
    def load_data(self, file_path: str, target_column: str) -> Tuple[pd.DataFrame, pd.Series]:
        """Load and validate dataset."""
        df = pd.read_csv(file_path)
        
        if target_column not in df.columns:
            raise ValueError(f"Target column '{target_column}' not found in dataset")
        
        X = df.drop(columns=[target_column])
        y = df[target_column]
        
        return X, y
    
    def preprocess_features(self, X: pd.DataFrame, fit: bool = True) -> np.ndarray:
        """Automatic feature engineering and preprocessing."""
        X = X.copy()
        
        # Identify column types
        numeric_cols = X.select_dtypes(include=['int64', 'float64']).columns.tolist()
        categorical_cols = X.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # Handle missing values
        for col in numeric_cols:
            X[col].fillna(X[col].median(), inplace=True)
        
        for col in categorical_cols:
            X[col].fillna('MISSING', inplace=True)
        
        # Encode categorical variables
        if categorical_cols:
            X = pd.get_dummies(X, columns=categorical_cols, drop_first=True)
        
        # Store feature names
        if fit:
            self.feature_names = X.columns.tolist()
        
        # Scale numeric features
        if fit:
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
        else:
            if self.scaler is None:
                raise ValueError("Scaler not fitted. Call with fit=True first.")
            # Ensure same columns as training
            for col in self.feature_names:
                if col not in X.columns:
                    X[col] = 0
            X = X[self.feature_names]
            X_scaled = self.scaler.transform(X)
        
        return X_scaled
    
    def preprocess_target(self, y: pd.Series, fit: bool = True) -> np.ndarray:
        """Encode target variable if categorical."""
        if y.dtype == 'object' or y.dtype.name == 'category':
            if fit:
                self.label_encoder = LabelEncoder()
                y_encoded = self.label_encoder.fit_transform(y)
            else:
                if self.label_encoder is None:
                    raise ValueError("Label encoder not fitted.")
                y_encoded = self.label_encoder.transform(y)
            return y_encoded
        return y.values
    
    def train(
        self,
        file_path: str,
        target_column: str,
        algorithm: str = "random_forest",
        test_size: float = 0.2,
        random_state: int = 42
    ) -> Dict[str, Any]:
        """Train ML model with automatic preprocessing."""
        
        # Load data
        X, y = self.load_data(file_path, target_column)
        
        # Preprocess
        X_processed = self.preprocess_features(X, fit=True)
        y_processed = self.preprocess_target(y, fit=True)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_processed, y_processed, test_size=test_size, random_state=random_state
        )
        
        # Select algorithm
        if algorithm == "random_forest":
            self.model = RandomForestClassifier(n_estimators=100, random_state=random_state)
        elif algorithm == "logistic_regression":
            self.model = LogisticRegression(max_iter=1000, random_state=random_state)
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        
        # Train model
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        
        metrics = {
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "f1_score": float(f1_score(y_test, y_pred, average='weighted')),
            "precision": float(precision_score(y_test, y_pred, average='weighted', zero_division=0)),
            "recall": float(recall_score(y_test, y_pred, average='weighted')),
            "algorithm": algorithm,
            "training_samples": len(X_train),
            "test_samples": len(X_test),
            "feature_count": len(self.feature_names)
        }
        
        return metrics
    
    def save_model(self, version: str) -> Tuple[str, str]:
        """Save trained model and scaler to disk."""
        if self.model is None:
            raise ValueError("No model to save. Train a model first.")
        
        # Create directory structure
        model_dir = self.storage_dir / f"tenant_{self.tenant_id}" / self.model_name / version
        model_dir.mkdir(parents=True, exist_ok=True)
        
        # Save model
        model_path = model_dir / "model.pkl"
        joblib.dump(self.model, model_path)
        
        # Save scaler
        scaler_path = model_dir / "scaler.pkl"
        joblib.dump({
            "scaler": self.scaler,
            "label_encoder": self.label_encoder,
            "feature_names": self.feature_names
        }, scaler_path)
        
        # Save metadata
        metadata_path = model_dir / "metadata.json"
        metadata = {
            "version": version,
            "tenant_id": self.tenant_id,
            "model_name": self.model_name,
            "feature_names": self.feature_names,
            "has_label_encoder": self.label_encoder is not None
        }
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return str(model_path), str(scaler_path)
    
    @staticmethod
    def load_model(model_path: str, scaler_path: str) -> Tuple[Any, Dict]:
        """Load trained model and preprocessing objects."""
        model = joblib.load(model_path)
        preprocessing = joblib.load(scaler_path)
        return model, preprocessing
    
    def predict(self, X: pd.DataFrame) -> Dict[str, Any]:
        """Make predictions on new data."""
        if self.model is None:
            raise ValueError("No model loaded. Train or load a model first.")
        
        # Preprocess
        X_processed = self.preprocess_features(X, fit=False)
        
        # Predict
        predictions = self.model.predict(X_processed)
        probabilities = self.model.predict_proba(X_processed) if hasattr(self.model, 'predict_proba') else None
        
        # Decode predictions if label encoder exists
        if self.label_encoder is not None:
            predictions = self.label_encoder.inverse_transform(predictions)
        
        result = {
            "predictions": predictions.tolist(),
            "probabilities": probabilities.tolist() if probabilities is not None else None
        }
        
        return result
