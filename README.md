# George's Youth Icon Shop

Enterprise-grade footwear e-commerce platform scaffold.

## Structure

- `backend/` - FastAPI service, SQLAlchemy, Alembic, auth, health checks.
- `frontend/` - React + Vite + TypeScript + MUI + Tailwind.
- `docker-compose.yml` - local development containers for backend, frontend, and PostgreSQL.

## Tech Stack

- **Frontend**: Vercel
- **Backend**: Railway
- **Database**: Neon PostgreSQL
- **Images**: Cloudinary

## Local Development

```bash
docker compose up --build
```

- Backend: `http://localhost:8000/docs`
- Frontend: `http://localhost:5173`

## Cloud Deployment

### Environment Variables (Backend)

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | Neon PostgreSQL connection string | Yes |
| `SECRET_KEY` | Application secret key | Yes |
| `JWT_SECRET` | JWT signing secret | Yes |
| `JWT_REFRESH_SECRET` | JWT refresh token secret | Yes |
| `CORS_ORIGINS` | Comma-separated allowed origins | Yes |
| `ENVIRONMENT` | development/production | Yes |
| `FRONTEND_URL` | Frontend URL for redirects | Yes |
| `BACKEND_URL` | Backend URL for webhooks | Yes |
| `CLOUDINARY_URL` | Cloudinary connection URL | Optional |

### Environment Variables (Frontend)

| Variable | Description | Required |
|----------|-------------|----------|
| `VITE_API_BASE_URL` | Backend API URL | Yes |
| `APP_ENV` | development/production | Yes |

### One-Click Deployment

1. **Backend (Railway)**
   - Connect GitHub repository
   - Set environment variables
   - Deploy

2. **Frontend (Vercel)**
   - Connect GitHub repository
   - Set `VITE_API_BASE_URL` to Railway URL
   - Deploy

3. **Database (Neon)**
   - Create PostgreSQL database
   - Copy connection string to `DATABASE_URL`

4. **Images (Cloudinary)**
   - Create account
   - Copy credentials to environment variables

### CORS Configuration

Production origins are automatically configured in `.env.example`.

### Security Headers

Production deployment includes secure cookie settings and CSRF protection.