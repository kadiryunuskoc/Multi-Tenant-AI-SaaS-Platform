# API Documentation

## Base URL

```
http://localhost:8000
```

## Authentication

All endpoints except `/auth/register`, `/auth/login`, and `/auth/tenants` require authentication via JWT Bearer token.

**Header Format:**
```
Authorization: Bearer <access_token>
```

---

## Endpoints

### Authentication

#### POST /api/v1/auth/tenants
Create a new tenant.

**Request:**
```json
{
  "name": "Acme Corporation"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "name": "Acme Corporation",
  "api_key": "generated-api-key-here",
  "status": "active",
  "created_at": "2026-02-17T14:00:00Z"
}
```

---

#### POST /api/v1/auth/register
Register a new user.

**Request:**
```json
{
  "email": "admin@acme.com",
  "password": "SecurePass123",
  "full_name": "John Doe",
  "role": "admin",
  "tenant_id": 1
}
```

**Roles:** `admin`, `user`, `viewer`

**Response:** `201 Created`
```json
{
  "id": 1,
  "email": "admin@acme.com",
  "full_name": "John Doe",
  "role": "admin",
  "tenant_id": 1,
  "is_active": true,
  "created_at": "2026-02-17T14:00:00Z"
}
```

---

#### POST /api/v1/auth/login
Authenticate and get JWT tokens.

**Request:**
```json
{
  "email": "admin@acme.com",
  "password": "SecurePass123"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "admin@acme.com",
    "full_name": "John Doe",
    "role": "admin",
    "tenant_id": 1,
    "is_active": true,
    "created_at": "2026-02-17T14:00:00Z"
  }
}
```

---

#### POST /api/v1/auth/refresh
Refresh access token.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:** `200 OK` (same as login)

---

#### GET /api/v1/auth/me
Get current user information.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "id": 1,
  "email": "admin@acme.com",
  "full_name": "John Doe",
  "role": "admin",
  "tenant_id": 1,
  "is_active": true,
  "created_at": "2026-02-17T14:00:00Z"
}
```

---

### Datasets

#### POST /api/v1/datasets/upload
Upload a CSV dataset.

**Headers:** 
- `Authorization: Bearer <token>`
- `Content-Type: multipart/form-data`

**Form Data:**
- `file`: CSV file
- `name`: Dataset name

**Response:** `201 Created`
```json
{
  "id": 1,
  "tenant_id": 1,
  "name": "Iris Dataset",
  "file_path": "./storage/uploads/tenant_1/Iris Dataset_iris.csv",
  "row_count": 150,
  "column_count": 5,
  "created_at": "2026-02-17T14:00:00Z"
}
```

---

#### GET /api/v1/datasets
List all datasets for current tenant.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "tenant_id": 1,
    "name": "Iris Dataset",
    "file_path": "./storage/uploads/tenant_1/iris.csv",
    "row_count": 150,
    "column_count": 5,
    "created_at": "2026-02-17T14:00:00Z"
  }
]
```

---

### Models

#### POST /api/v1/models/train
Train a new ML model.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "name": "Iris Classifier",
  "dataset_id": 1,
  "target_column": "species",
  "algorithm": "random_forest",
  "test_size": 0.2
}
```

**Algorithms:** `random_forest`, `logistic_regression`

**Response:** `201 Created`
```json
{
  "id": 1,
  "tenant_id": 1,
  "name": "Iris Classifier",
  "version": "v1.0.0",
  "algorithm": "random_forest",
  "accuracy": 0.96,
  "f1_score": 0.95,
  "precision_score": 0.96,
  "recall_score": 0.95,
  "status": "active",
  "created_at": "2026-02-17T14:00:00Z"
}
```

---

#### GET /api/v1/models
List all models for current tenant.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "tenant_id": 1,
    "name": "Iris Classifier",
    "version": "v1.0.0",
    "algorithm": "random_forest",
    "accuracy": 0.96,
    "f1_score": 0.95,
    "precision_score": 0.96,
    "recall_score": 0.95,
    "status": "active",
    "created_at": "2026-02-17T14:00:00Z"
  }
]
```

---

#### GET /api/v1/models/{model_id}
Get model details.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK` (same as model object above)

---

### Predictions

#### POST /api/v1/predict
Make a single prediction.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "model_id": 1,
  "features": {
    "sepal_length": 5.1,
    "sepal_width": 3.5,
    "petal_length": 1.4,
    "petal_width": 0.2
  }
}
```

**Response:** `200 OK`
```json
{
  "prediction": "setosa",
  "confidence": 0.98,
  "probabilities": [0.98, 0.01, 0.01],
  "model_id": 1,
  "model_version": "v1.0.0"
}
```

---

#### POST /api/v1/predict/batch
Make batch predictions.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "model_id": 1,
  "features_list": [
    {
      "sepal_length": 5.1,
      "sepal_width": 3.5,
      "petal_length": 1.4,
      "petal_width": 0.2
    },
    {
      "sepal_length": 6.3,
      "sepal_width": 3.3,
      "petal_length": 6.0,
      "petal_width": 2.5
    }
  ]
}
```

**Response:** `200 OK`
```json
{
  "predictions": [
    {
      "prediction": "setosa",
      "confidence": 0.98,
      "probabilities": [0.98, 0.01, 0.01]
    },
    {
      "prediction": "virginica",
      "confidence": 0.95,
      "probabilities": [0.01, 0.04, 0.95]
    }
  ],
  "model_id": 1,
  "model_version": "v1.0.0",
  "count": 2
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid input data"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Permission denied. Required: write:models"
}
```

### 404 Not Found
```json
{
  "detail": "Model not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Model training failed: <error message>"
}
```

---

## Role-Based Permissions

| Role | Permissions |
|------|-------------|
| **admin** | All permissions |
| **user** | `read:models`, `write:models`, `predict`, `upload:data` |
| **viewer** | `read:models`, `predict` |

---

