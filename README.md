# Spendy

PWA de finanzas personales con clasificación híbrida (reglas locales + IA), sistema de roles y acceso controlado por lista blanca.

[![Live Demo](https://img.shields.io/badge/demo-live-brightgreen)](https://spendy.practical.com.ar)
[![Stack](https://img.shields.io/badge/stack-FastAPI%20%7C%20React%20%7C%20PostgreSQL-blue)](#stack-tecnológico)
[![Landing](https://img.shields.io/badge/showcase-landing%20page-indigo)](https://francobertotti.github.io/spendy-showcase)

> **Acceso demo:** el registro está controlado por lista blanca. Para probar la app con una cuenta de prueba, contactame en [LinkedIn](https://www.linkedin.com/in/franco-bertotti/).

---

## Screenshots

<!-- Reemplazar con screenshots reales -->

| Dashboard | Carga de transacción | Panel admin |
|-----------|----------------------|-------------|
| ![Dashboard](assets/screenshot-dashboard.png) | ![Carga](assets/screenshot-carga.png) | ![Admin](assets/screenshot-admin.png) |

<!-- Demo en video -->
<!-- ![Demo](assets/demo.gif) -->

---

## ¿Qué es Spendy?

El usuario registra movimientos en texto natural — _"pagué 5000 de alquiler"_, _"cobré el sueldo"_ — y el sistema los clasifica automáticamente en categorías y pilares financieros (Necesidades · Deseos · Ahorro/Inversión) siguiendo la regla 50/30/20.

El registro está protegido por una **lista blanca de emails** que administra el SuperAdmin. Sin autorización previa, no se puede crear cuenta.

---

## Clasificación híbrida

El núcleo del sistema es un pipeline de dos pasos:

```
texto del usuario
       │
       ▼
┌─────────────────────────┐
│   Clasificador local    │  ← reglas + regex, sin llamadas externas
│   classifier.py         │
└────────┬────────────────┘
         │ match encontrado         │ texto ambiguo / sin match
         ▼                          ▼
  resultado inmediato         ┌──────────────┐
                              │   Groq API   │  ← LLM como fallback
                              └──────┬───────┘
                                     ▼
                              resultado estructurado
```

El clasificador local resuelve la mayoría de los casos sin costo y sin latencia. Solo los textos ambiguos se envían a la IA. Ver los snippets de implementación en [`snippets/`](snippets/).

---

## Stack tecnológico

### Backend
- **FastAPI** — framework HTTP
- **SQLAlchemy 2.0** — ORM (sync)
- **PostgreSQL** — base de datos relacional
- **python-jose** — JWT HS256, 7 días de expiración
- **Groq API** — LLM para clasificación fallback
- **passlib[bcrypt]** — hash de contraseñas

### Frontend
- **React 19** + TypeScript
- **Vite 8** — build tool
- **TailwindCSS v4** — estilos utilitarios
- **React Router v7** — SPA
- **vite-plugin-pwa** + **Workbox** — PWA instalable

### Infraestructura
- **Vercel** — frontend (main → prod, staging → preview)
- **Render** — backend (web service, deploy por rama)
- **Supabase** — PostgreSQL gestionado
- **Cloudflare** — dominio y DNS

---

## Arquitectura

```
┌─────────────────────────────────────────────┐
│               FRONTEND (React/Vite)          │
│  /dashboard  /transactions  /settings        │
│  /admin  /admin/whitelist  /admin/categories │
│  AuthContext → isSuperAdmin                  │
│  AdminRoute (guard de ruta)                  │
└──────────────┬──────────────────────────────┘
               │ HTTP / JWT Bearer
┌──────────────▼──────────────────────────────┐
│              BACKEND (FastAPI)               │
│  /auth  /transactions  /budget  /cierre      │
│  /ai-parser  /admin                          │
│                                              │
│  core/classifier.py  →  Groq API (fallback)  │
└──────────────┬──────────────────────────────┘
               │ psycopg2 / SQLAlchemy
┌──────────────▼──────────────────────────────┐
│         POSTGRESQL (Supabase)                │
│  usuarios · transacciones · categorias       │
│  presupuestos · cierres_mes · lista_blanca   │
└─────────────────────────────────────────────┘
```

---

## Seguridad

- **JWT HS256** — 7 días de expiración, firmado con `SECRET_KEY`
- **IDOR corregido** — `usuario_id` siempre viene del token JWT, nunca de params del request
- **Lista blanca** — el registro está bloqueado para emails no autorizados
- **`require_superadmin`** — dependencia FastAPI que protege todos los endpoints `/admin/*`
- **Passwords** hasheados con bcrypt

---

## Roles

| Rol | Acceso |
|-----|--------|
| `user` | Dashboard, transacciones, presupuesto, cierre de mes, configuración |
| `superadmin` | Todo lo anterior + panel `/admin` (whitelist, categorías, usuarios) |

---

## Decisiones técnicas

Ver [`docs/architecture-decisions.md`](docs/architecture-decisions.md) para los ADRs del proyecto:

- ADR-01: Clasificación local antes de delegar a IA (costo/latencia)
- ADR-02: Registro por lista blanca en lugar de registro abierto
- ADR-03: SQLAlchemy síncrono sobre async
- ADR-04: Supabase como PostgreSQL gestionado
- ADR-05: Dos entornos `main` → prod / `staging` → test

Ver [`docs/deployment-flow.md`](docs/deployment-flow.md) para el flujo completo de infraestructura y variables de entorno.

---

## Snippets de implementación

Los archivos en [`snippets/`](snippets/) muestran fragmentos seleccionados del código real:

**Backend**
- [`classifier_excerpt.py`](snippets/backend/classifier_excerpt.py) — motor de clasificación local: extracción de monto, detección de tipo y matching por categoría
- [`ai_parser_excerpt.py`](snippets/backend/ai_parser_excerpt.py) — orquestador híbrido: decide cuándo usar reglas locales y cuándo delegar a la IA
- [`security_excerpt.py`](snippets/backend/security_excerpt.py) — JWT, bcrypt y dependencias FastAPI (`get_current_user`, `require_superadmin`)
- [`admin_router_excerpt.py`](snippets/backend/admin_router_excerpt.py) — router del panel admin: whitelist, usuarios y categorías

**Frontend**
- [`AuthContext_excerpt.tsx`](snippets/frontend/AuthContext_excerpt.tsx) — estado global de auth, `isSuperAdmin` derivado, re-validación de sesión
- [`AdminRoute_excerpt.tsx`](snippets/frontend/AdminRoute_excerpt.tsx) — guard de ruta React Router v7

**Infraestructura**
- [`Dockerfile`](snippets/infra/Dockerfile) — imagen del backend
- [`docker-compose.yml`](snippets/infra/docker-compose.yml) — stack local de desarrollo

---

## Contacto

Para acceder a una cuenta demo o consultas sobre el proyecto:

**[Franco Bertotti en LinkedIn](https://www.linkedin.com/in/franco-bertotti/)**

---

*Franco Bertotti — Practical Thinking*
