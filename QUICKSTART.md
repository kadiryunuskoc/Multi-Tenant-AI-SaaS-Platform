# 🚀 Quick Start Guide

## Deployment (Single Command)

```bash
# Navigate to project directory
cd use_case

# Start the platform
docker-compose up --build
```

**Platform will be available at:**
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

---

## Testing the Platform

### 1. Create a Tenant

```bash
curl -X POST "http://localhost:8000/api/v1/auth/tenants" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Company"}'
```

Save the `id` from response (e.g., `1`)

### 2. Register a User

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@test.com",
    "password": "Test1234",
    "full_name": "Test Admin",
    "role": "admin",
    "tenant_id": 1
  }'
```

### 3. Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@test.com",
    "password": "Test1234"
  }'
```

Save the `access_token` from response.

### 4. Upload Dataset

```bash
curl -X POST "http://localhost:8000/api/v1/datasets/upload" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@sample_data/iris_sample.csv" \
  -F "name=Iris Dataset"
```

Save the `id` from response (e.g., `1`)

### 5. Train Model

```bash
curl -X POST "http://localhost:8000/api/v1/models/train" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Iris Classifier",
    "dataset_id": 1,
    "target_column": "species",
    "algorithm": "random_forest",
    "test_size": 0.2
  }'
```

Wait for training to complete. Save the `id` from response (e.g., `1`)

### 6. Make Prediction

```bash
curl -X POST "http://localhost:8000/api/v1/predict" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": 1,
    "features": {
      "sepal_length": 5.1,
      "sepal_width": 3.5,
      "petal_length": 1.4,
      "petal_width": 0.2
    }
  }'
```

Expected response:
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

## 📚 Documentation

- **[README.md](README.md)** - Complete project overview, architecture decisions, trade-offs
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Detailed technical architecture, diagrams, security
- **[API_DOCS.md](API_DOCS.md)** - Complete API reference with examples

---

## 🎯 Key Features

✅ Multi-tenant architecture with complete data isolation
✅ JWT authentication with role-based access control
✅ Self-service ML model training with automatic feature engineering
✅ Model versioning (semantic versioning)
✅ Real-time predictions via REST API
✅ Comprehensive documentation
✅ Single-command Docker deployment

---

## 📁 Project Structure

```
use_case/
├── README.md               # Main documentation
├── ARCHITECTURE.md         # Technical architecture
├── API_DOCS.md            # API reference
├── QUICKSTART.md          # This file
├── docker-compose.yml     # Deployment config
├── sample_data/           # Test datasets
│   └── iris_sample.csv
└── backend/               # FastAPI application
    ├── Dockerfile
    ├── requirements.txt
    └── app/
        ├── main.py
        ├── models/        # Database models
        ├── schemas/       # Pydantic schemas
        ├── api/          # API endpoints
        ├── ml/           # ML components
        └── utils/        # Utilities
```

---

## 🛠️ Technology Stack

- **Backend:** FastAPI (Python 3.11)
- **Database:** SQLite (prototype) → PostgreSQL (production)
- **ML:** scikit-learn
- **Auth:** JWT with bcrypt
- **Deployment:** Docker + Docker Compose

---

## 💡 Tips

1. **Interactive API Docs:** Visit http://localhost:8000/docs to test endpoints interactively
2. **Health Check:** Use http://localhost:8000/health to verify the platform is running
3. **Sample Data:** Use the provided `iris_sample.csv` for quick testing
4. **Roles:** Create users with different roles (admin, user, viewer) to test RBAC

---

## 🔧 Troubleshooting

**Port already in use:**
```bash
# Change port in docker-compose.yml
ports:
  - "8001:8000"  # Use 8001 instead
```

**Database issues:**
```bash
# Remove existing database
rm backend/ai_platform.db

# Restart
docker-compose up --build
```

**Permission errors:**
```bash
# On Linux/Mac, fix permissions
sudo chown -R $USER:$USER .
```

---

**For detailed information, see [README.md](README.md)**
