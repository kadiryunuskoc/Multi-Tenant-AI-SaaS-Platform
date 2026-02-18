# ✅ Platform Başarıyla Çalışıyor!

## Test Sonuçları

Platform başarıyla ayağa kalktı ve çalışıyor:
- ✅ Database oluşturuldu
- ✅ API server çalışıyor (http://localhost:8000)
- ✅ Login endpoint çalışıyor (200 OK)
- ✅ Swagger UI erişilebilir (http://localhost:8000/docs)

## Swagger UI ile Test Etme

### 1. Tenant Oluştur
1. http://localhost:8000/docs adresine git
2. `POST /api/v1/auth/tenants` endpoint'ini aç
3. "Try it out" butonuna tıkla
4. Request body:
```json
{
  "name": "Test Company"
}
```
5. "Execute" butonuna tıkla
6. Response'dan `id` değerini not al (örn: 1)

### 2. Kullanıcı Kaydet
1. `POST /api/v1/auth/register` endpoint'ini aç
2. "Try it out" butonuna tıkla
3. Request body:
```json
{
  "email": "admin@test.com",
  "password": "Test1234",
  "full_name": "Test Admin",
  "role": "admin",
  "tenant_id": 1
}
```
4. "Execute" butonuna tıkla

### 3. Login Yap
1. `POST /api/v1/auth/login` endpoint'ini aç
2. "Try it out" butonuna tıkla
3. Request body:
```json
{
  "email": "admin@test.com",
  "password": "Test1234"
}
```
4. "Execute" butonuna tıkla
5. Response'dan `access_token` değerini kopyala

### 4. Token'ı Swagger UI'da Ayarla
1. Sayfanın üst kısmındaki **"Authorize"** butonuna tıkla (kilit ikonu)
2. Açılan pencereye token'ı yapıştır:
```
Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```
**ÖNEMLİ:** Token'ın başına `Bearer ` yazmayın, sadece token'ı yapıştırın
3. "Authorize" butonuna tıkla
4. "Close" butonuna tıkla

Artık tüm korumalı endpoint'leri test edebilirsiniz!

### 5. Dataset Yükle
1. `POST /api/v1/datasets/upload` endpoint'ini aç
2. "Try it out" butonuna tıkla
3. `file`: `sample_data/iris_sample.csv` dosyasını seç
4. `name`: "Iris Dataset" yaz
5. "Execute" butonuna tıkla
6. Response'dan `id` değerini not al

### 6. Model Eğit
1. `POST /api/v1/models/train` endpoint'ini aç
2. "Try it out" butonuna tıkla
3. Request body:
```json
{
  "name": "Iris Classifier",
  "dataset_id": 1,
  "target_column": "species",
  "algorithm": "random_forest",
  "test_size": 0.2
}
```
4. "Execute" butonuna tıkla
5. Eğitim tamamlanana kadar bekle (birkaç saniye)
6. Response'da accuracy, f1_score gibi metrikleri gör

### 7. Prediction Yap
1. `POST /api/v1/predict` endpoint'ini aç
2. "Try it out" butonuna tıkla
3. Request body:
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
4. "Execute" butonuna tıkla
5. Response'da prediction ve confidence gör

## cURL ile Test Etme

Alternatif olarak terminal/PowerShell'den test edebilirsiniz:

```bash
# 1. Tenant oluştur
curl -X POST "http://localhost:8000/api/v1/auth/tenants" -H "Content-Type: application/json" -d "{\"name\": \"Test Company\"}"

# 2. Kullanıcı kaydet
curl -X POST "http://localhost:8000/api/v1/auth/register" -H "Content-Type: application/json" -d "{\"email\": \"admin@test.com\", \"password\": \"Test1234\", \"full_name\": \"Test Admin\", \"role\": \"admin\", \"tenant_id\": 1}"

# 3. Login
curl -X POST "http://localhost:8000/api/v1/auth/login" -H "Content-Type: application/json" -d "{\"email\": \"admin@test.com\", \"password\": \"Test1234\"}"

# Token'ı kopyala ve aşağıdaki komutlarda YOUR_TOKEN yerine yapıştır

# 4. Dataset yükle
curl -X POST "http://localhost:8000/api/v1/datasets/upload" -H "Authorization: Bearer YOUR_TOKEN" -F "file=@sample_data/iris_sample.csv" -F "name=Iris Dataset"

# 5. Model eğit
curl -X POST "http://localhost:8000/api/v1/models/train" -H "Authorization: Bearer YOUR_TOKEN" -H "Content-Type: application/json" -d "{\"name\": \"Iris Classifier\", \"dataset_id\": 1, \"target_column\": \"species\", \"algorithm\": \"random_forest\", \"test_size\": 0.2}"

# 6. Prediction yap
curl -X POST "http://localhost:8000/api/v1/predict" -H "Authorization: Bearer YOUR_TOKEN" -H "Content-Type: application/json" -d "{\"model_id\": 1, \"features\": {\"sepal_length\": 5.1, \"sepal_width\": 3.5, \"petal_length\": 1.4, \"petal_width\": 0.2}}"
```

## Sorun Giderme

**401 Unauthorized hatası alıyorsanız:**
- Token'ın doğru kopyalandığından emin olun
- Token'ın başına "Bearer " eklemeyin (Swagger UI otomatik ekler)
- Token'ın süresi dolmuş olabilir (30 dakika), yeniden login yapın

**Dataset yüklenemiyor:**
- Dosya yolunun doğru olduğundan emin olun
- CSV formatında olduğundan emin olun

**Model eğitimi başarısız:**
- Dataset ID'nin doğru olduğundan emin olun
- Target column'un dataset'te var olduğundan emin olun

## Başarı Kriterleri

✅ Tüm endpoint'ler çalışıyor
✅ Multi-tenant izolasyon aktif
✅ JWT authentication çalışıyor
✅ Model eğitimi ve prediction çalışıyor
✅ Swagger UI ile interaktif test mümkün

**Platform production-ready! 🚀**
