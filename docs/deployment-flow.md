# Deployment Flow — Spendy

## Entornos

| Entorno | Rama | Frontend | Backend | Base de datos |
|---------|------|----------|---------|---------------|
| **Producción** | `main` | Vercel (dominio propio) | Render (web service) | Supabase prod |
| **Staging** | `staging` | Vercel (preview URL) | Render (service staging) | Supabase staging |

---

## Flujo de un deploy a producción

```
developer
    │
    ├── push → staging
    │       │
    │       ├── Vercel: deploy automático → preview URL
    │       └── Render: deploy automático → backend staging
    │                   └── conecta a Supabase staging DB
    │
    │   [QA en staging: tests manuales / smoke tests]
    │
    └── merge staging → main
            │
            ├── Vercel: deploy automático → dominio prod
            └── Render: deploy automático → backend prod
                        └── conecta a Supabase prod DB
```

---

## Servicios por capa

### Frontend — Vercel
- Build command: `npm run build` (Vite)
- Output: `dist/`
- Variables de entorno: `VITE_API_URL` apunta al backend correspondiente
- PWA: el service worker se regenera en cada build

### Backend — Render
- Imagen: Docker (`python:3.11-slim`)
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- Variables de entorno en Render: `DATABASE_URL`, `SECRET_KEY`, `GROQ_API_KEY`, `SUPERADMIN_EMAIL`, `SUPERADMIN_PASSWORD`, `CORS_ORIGINS`
- Health check: `GET /health` → `{"status": "ok"}`

### Base de datos — Supabase
- PostgreSQL 15 gestionado
- Conexión: `psycopg2` via `DATABASE_URL` (connection string estándar)
- Las tablas se crean via `Base.metadata.create_all()` en el arranque del backend
- El seed del superadmin y las categorías base también se ejecutan en el arranque (`seed_database()`)

---

## Variables de entorno requeridas (backend)

```bash
DATABASE_URL=postgresql://user:password@host:5432/db
SECRET_KEY=<token aleatorio seguro>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080   # 7 días
GROQ_API_KEY=<clave de Groq>
SUPERADMIN_EMAIL=<email del admin>
SUPERADMIN_PASSWORD=<password del admin>
CORS_ORIGINS=https://spendy.vercel.app,https://tu-dominio.com
```

Ver `.env.example` en el repo privado para la lista completa.

---

## Diagrama de infraestructura

```
┌──────────────┐     HTTPS      ┌──────────────────────────┐
│  Browser /   │◄──────────────►│  Vercel (React PWA)      │
│  Mobile PWA  │                │  spendy.vercel.app       │
└──────────────┘                └────────────┬─────────────┘
                                             │ fetch /api/v1/*
                                             │ Bearer JWT
                                ┌────────────▼─────────────┐
                                │  Render (FastAPI)        │
                                │  python:3.11-slim        │
                                │  uvicorn                 │
                                └────────────┬─────────────┘
                                             │ psycopg2
                                ┌────────────▼─────────────┐
                                │  Supabase (PostgreSQL)   │
                                │  managed, backups auto   │
                                └──────────────────────────┘
```
