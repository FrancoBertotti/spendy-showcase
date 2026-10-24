"""
Rate limiting en el endpoint de login con slowapi.

Protege contra fuerza bruta sobre credenciales.
10 intentos por minuto por IP antes de recibir 429.
"""
from fastapi import APIRouter, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login")
@limiter.limit("10/minute")
async def login(request: Request, credentials: LoginPayload, db: Session = Depends(get_db)):
    user = authenticate_user(db, credentials.email, credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    token = create_access_token(subject=user.id)
    return {"access_token": token, "token_type": "bearer", "user": user}


# En main.py también se registra el handler de slowapi:
# app.state.limiter = limiter
# app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
