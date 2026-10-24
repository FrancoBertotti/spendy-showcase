# Architecture Decision Records — Spendy

Decisiones de diseño técnico tomadas durante el desarrollo. Cada ADR documenta el contexto, la decisión y el razonamiento.

---

## ADR-01 · Clasificación local antes de delegar a IA

**Contexto:** El flujo principal de la app es que el usuario ingrese texto natural ("pagué 5000 de alquiler") y el sistema lo clasifique automáticamente. La clasificación podría hacerse 100% vía LLM.

**Decisión:** Implementar un clasificador local (regex + diccionario de palabras clave) que resuelve el caso antes de llamar a la API de Groq. Solo si no hay match o el texto es ambiguo se delega a la IA.

**Razonamiento:**
- **Costo**: la mayoría de las transacciones son repetitivas (supermercado, transporte, sueldo). El clasificador local resuelve ~70% de los casos sin costo.
- **Latencia**: una llamada a la API agrega ~1-2 segundos. El clasificador local es instantáneo.
- **Sin vendor lock-in**: el comportamiento principal no depende de la disponibilidad de Groq.
- **Fallback entre modelos**: si Groq falla, el servicio itera sobre una lista de modelos alternativos antes de lanzar error.

---

## ADR-02 · Registro controlado por lista blanca de emails

**Contexto:** La app es un producto personal en uso real. Un registro abierto generaría cuentas de prueba, datos ruidosos y costos en la API de IA.

**Decisión:** El endpoint `/auth/register` verifica contra una tabla `lista_blanca` antes de crear la cuenta. Sin email autorizado → 403. El superadmin gestiona la whitelist desde el panel `/admin/whitelist`.

**Razonamiento:**
- Control total sobre quién accede durante la fase de uso personal / beta cerrada.
- Protección implícita contra scraping y bots.
- Permite escalar a invitación cuando se quiera abrir sin reescribir el flujo de auth.

---

## ADR-03 · SQLAlchemy síncrono sobre async

**Contexto:** FastAPI soporta `async def` handlers y SQLAlchemy 2.0 tiene soporte para async. La tendencia en el ecosistema es migrar a async.

**Decisión:** Usar SQLAlchemy en modo síncrono con `Session` estándar, no `AsyncSession`.

**Razonamiento:**
- Para una app de finanzas personales con carga baja, el overhead de async no agrega valor real.
- El modo síncrono es más predecible en debugging, tracing de errores y transacciones.
- SQLAlchemy async agrega complejidad en los Depends() de FastAPI (lazy loading, greenlets). No vale la pena en este scope.
- Si la carga creciera, el camino de migración está documentado en SQLAlchemy 2.0.

---

## ADR-04 · Supabase (PostgreSQL gestionado) sobre autohosteado

**Contexto:** La base de datos necesita ser accesible desde Render (backend en la nube). Opciones: Supabase, AWS RDS, Railway, Neon, o un Postgres en el mismo servidor.

**Decisión:** Supabase como proveedor de PostgreSQL gestionado.

**Razonamiento:**
- **Free tier generoso**: suficiente para uso personal sin costo operativo.
- **PostgreSQL estándar**: no hay lock-in de API propietaria; se conecta con psycopg2 como cualquier Postgres.
- **Dashboard incluido**: permite inspeccionar datos en producción sin SSH ni psql.
- **Backups automáticos**: sin ops.
- Trade-off aceptado: cold start en plan gratuito (~1s en queries tras inactividad). Para una app personal es tolerable.

---

## ADR-05 · Dos entornos: `main` → producción, `staging` → pruebas

**Contexto:** La app está en uso real. Necesitaba un entorno seguro para probar cambios sin afectar datos reales.

**Decisión:** Dos ramas permanentes con pipelines de despliegue automático independientes:
- `main` → producción: Vercel (frontend) + Render (backend) + Supabase DB prod
- `staging` → test: Vercel preview + Render service staging + Supabase DB staging

**Razonamiento:**
- Cambios en el esquema de BD se prueban primero contra la DB de staging.
- Vercel crea deployments de preview automáticamente por rama; Render también soporta múltiples services.
- Permite hacer QA real en un entorno idéntico al de producción antes de mergear a `main`.
