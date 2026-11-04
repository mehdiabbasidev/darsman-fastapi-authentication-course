# InsightHub FastAPI — Teaching Version

نسخه ساده‌شده پروژه InsightHub برای آموزش FastAPI با استفاده مستقیم از دیتابیس PostgreSQL موجود.

## Scope

فقط این دو مدل نگه داشته شده‌اند:

- `users`
- `user_profiles`

مدل‌ها و سرویس‌های مربوط به `documents`، `tags` و `document_tags` حذف شده‌اند.

> در دیتابیس اصلی InsightHub، جدول `user_profiles` ستون `id` مستقل ندارد و `user_id` هم Primary Key و هم Foreign Key است. این نسخه همان ساختار واقعی را حفظ می‌کند.

## Project structure

```text
Insighthub_FastAPI_Teaching/
│
├── app/
│   ├── database.py
│   ├── models/
│   │   ├── user.py
│   │   └── user_profile.py
│   ├── routers/
│   │   └── users.py
│   └── services/
│       └── users.py
│
├── main.py
├── requirements.txt
└── README.md
```

### چرا Service Layer نگه داشته شده؟

- `main.py` فقط مسئول HTTP و FastAPI است.
- `services/users.py` مسئول Query و CRUD با SQLAlchemy است.
- `models/` فقط مدل‌های دیتابیس را نگه می‌دارد.
- ساختار ساده است و Repository Pattern یا معماری اضافه ندارد.

## Run

```bash
python -m venv .venv
```

PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Git Bash:

```bash
source .venv/Scripts/activate
```

CMD:

```cmd
.venv\Scripts\activate
```

Install:

```bash
pip install -r requirements.txt
```

Run API:

```bash
uvicorn main:app --reload
```

## Endpoints

```text
GET     /
GET     /users
GET     /users/{user_id}
POST    /users
PUT     /users/{user_id}
DELETE  /users/{user_id}
GET     /users/{user_id}/profile
PUT     /users/{user_id}/profile
```

## curl — Git Bash

Create user:

```bash
curl -i -X POST http://127.0.0.1:8000/users \
  -H "Content-Type: application/json" \
  -d '{"email":"student@example.com"}'
```

Update profile:

```bash
curl -i -X PUT http://127.0.0.1:8000/users/1/profile \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Ali Ahmadi","bio":"Python student","avatar_url":null}'
```

## curl — Windows CMD

Create user:

```cmd
curl -i -X POST http://127.0.0.1:8000/users -H "Content-Type: application/json" -d "{\"email\":\"student@example.com\"}"
```

Or multi-line in CMD using `^`:

```cmd
curl -i -X POST http://127.0.0.1:8000/users ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"student@example.com\"}"
```

## Teaching focus

- Client / Server
- Request / Response
- FastAPI vs Uvicorn
- Route and HTTP methods
- Path Parameter
- Query Parameter
- Request Body with `Body()`
- Manual validation
- 400 / 404 / 422
- 201 / 204
- `HTTPException`
- `Depends(get_session)`
- SQLAlchemy service layer
- PostgreSQL integration
- JSON response with `to_dict()`
- `/docs`

این نسخه عمداً Repository Pattern، Authentication، async SQLAlchemy و Response Schema را وارد نمی‌کند تا تمرکز جلسه روی اصول FastAPI باقی بماند.

---

## Authentication with JWT — Add-on Lesson

این بخش به همان پروژه قبلی اضافه شده و ساختار اصلی پروژه حفظ شده است. فقط فایل‌های لازم برای Authentication و JWT اضافه شده‌اند.

## تغییرات جدید

```text
app/
├── dependencies/
│   └── auth.py
├── routers/
│   └── auth.py
├── services/
│   └── auth.py
└── models/
    └── user.py          # فقط password_hash اضافه شده

sql/
└── 01_add_password_hash.sql
```

## 1) تغییر دیتابیس

قبل از اجرای بخش Authentication، اسکریپت زیر را یک بار روی دیتابیس موجود اجرا کنید:

```sql
ALTER TABLE users
ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255);
```

فایل آماده آن در مسیر زیر قرار دارد:

```text
sql/01_add_password_hash.sql
```

ستون `password_hash` عمداً nullable است تا Userهایی که در جلسه قبلی ساخته شده‌اند همچنان معتبر بمانند. فقط Userهایی که از `/auth/register` ساخته می‌شوند می‌توانند Login کنند.

## 2) نصب Dependencyهای جدید

```bash
pip install -r requirements.txt
```

Dependencyهای جدید:

```text
pyjwt
pwdlib[argon2]
python-multipart
```

## 3) Endpointهای جدید

```text
POST  /auth/register
POST  /auth/login
GET   /auth/me
```

### Register

```json
POST /auth/register

{
  "email": "student@example.com",
  "password": "12345678"
}
```

Password قبل از ذخیره شدن Hash می‌شود و خود Password داخل دیتابیس ذخیره نمی‌شود.

### Login

`/auth/login` از `OAuth2PasswordRequestForm` استفاده می‌کند. در Swagger مقدار فیلد `username` را برابر Email وارد کنید.

```text
username = student@example.com
password = 12345678
```

Response:

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

### Protected Route

```text
GET /auth/me
```

این Route از Dependency زیر استفاده می‌کند:

```python
current_user: User = Depends(get_current_user)
```

## 4) Flow آموزشی

```text
Register
   ↓
Hash Password
   ↓
Login
   ↓
Verify Password
   ↓
Create JWT Access Token
   ↓
Authorization: Bearer <token>
   ↓
OAuth2PasswordBearer
   ↓
get_current_user
   ↓
GET /auth/me
```

## 5) تست در Swagger

برنامه را اجرا کنید:

```bash
uvicorn main:app --reload --port 8000
```

سپس:

1. با `POST /auth/register` یک User بسازید.
2. روی دکمه **Authorize** در Swagger کلیک کنید.
3. Email را در فیلد `username` و Password را در فیلد `password` وارد کنید.
4. `GET /auth/me` را اجرا کنید.

## نکته آموزشی

برای ساده ماندن پروژه، هنوز از Pydantic Schema، Refresh Token، Role/Permission، Logout، Email Verification و Alembic استفاده نشده است. هدف این بخش فقط آموزش مسیر اصلی زیر است:

```text
Password Hashing → Login → JWT → Bearer Token → get_current_user → Protected Route
```
