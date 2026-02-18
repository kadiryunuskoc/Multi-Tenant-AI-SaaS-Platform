# OAuth2 Password Flow Test

After updating the code, restart Docker:

```bash
docker-compose down
docker-compose up --build
```

Then in Swagger UI (http://localhost:8000/docs):

1. Click the **"Authorize"** button (🔒 lock icon)
2. You'll see a login form with:
   - **username**: Enter your email (e.g., `admin@isnet.com`)
   - **password**: Enter your password (e.g., `Test1234`)
3. Click "Authorize"
4. Click "Close"

Now all protected endpoints will automatically include your token! No need to copy/paste tokens manually.

## How it works

- Changed from `HTTPBearer` to `OAuth2PasswordBearer`
- OAuth2PasswordBearer shows a login form in Swagger UI
- When you click "Authorize", it calls `/api/v1/auth/login` automatically
- The token is stored and sent with every request

Much easier than copying tokens! ✅
