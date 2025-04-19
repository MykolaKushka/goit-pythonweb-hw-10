# 📦 Contacts API

Контактний REST API на базі FastAPI з підтримкою:
- 🔐 JWT-аутентифікації та авторизації
- 📧 Верифікації email
- ☁️ Завантаження аватара користувача через Cloudinary
- 🐳 Розгортання через Docker + PostgreSQL
- 🧃 Документація через Swagger UI

## 🏗️ Стек технологій

- **FastAPI**
- **PostgreSQL**
- **SQLAlchemy (async)**
- **Pydantic**
- **JWT**
- **Cloudinary**
- **Docker & Docker Compose**
- **Swagger UI**

## ⚙️ Встановлення (локально без Docker)

1. **Клонуй репозиторій**  
   ```bash
   git clone https://github.com/your-name/contacts-api.git
   cd contacts-api
   ```

2. **Створи віртуальне середовище**
   ```bash
   python -m venv venv
   source venv/bin/activate  # або venv\Scripts\activate для Windows
   ```

3. **Встанови залежності**
   ```bash
   pip install -r requirements.txt
   ```

4. **Налаштуй змінні середовища у `.env`**
   ```env
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_DB=contacts
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/contacts

   SECRET_KEY=your_super_secret_key

   CLOUDINARY_NAME=your_cloud_name
   CLOUDINARY_API_KEY=your_api_key
   CLOUDINARY_API_SECRET=your_secret
   ```

5. **Запусти сервер**
   ```bash
   uvicorn app.main:app --reload
   ```

## 🐳 Запуск у Docker

1. **Переконайся, що Docker встановлено**
2. **У корені проєкту повинен бути `Dockerfile`, `docker-compose.yml`, `.env`**

3. **Запусти**
   ```bash
   docker-compose up --build
   ```

4. **Доступ до API**
   - Swagger: http://localhost:8000/docs
   - OpenAPI: http://localhost:8000/openapi.json

## 🔐 Авторизація

- Реєстрація: `POST /auth/signup`
- Логін: `POST /auth/login` → повертає `access_token`
- Підтвердження email: `GET /auth/verify-email/{token}`
- Аватарка: `POST /auth/avatar` (потрібен файл `multipart/form-data`)
- Персональна інформація: `GET /auth/me` (авторизований, підтверджений)

## 🧪 Тестування в Swagger

1. Залогінься через `/auth/login`
2. Натисни "Authorize" 🔐 і встав токен:
   ```
   Bearer <access_token>
   ```

## 📂 Структура проєкту

```
project/
├── contacts_api/
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── routes.py
│   │   ├── routes_auth.py
│   │   ├── auth.py
│   │   ├── database.py
│   │   ├── schemas.py
│   │   └── cloudinary_utils.py
│   └── venv/
├── .env
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .gitignore
```

## 🛡️ Безпека

- Паролі зберігаються у хешованому вигляді (`bcrypt`)
- JWT-токени з підписом
- Верифікація електронної пошти
- Rate limit на `/auth/me`
- Всі чутливі дані у `.env`