"""
Router del panel de administración.

Todos los endpoints están protegidos con `require_superadmin`,
un Depends() que primero valida el JWT y luego verifica que
el usuario tenga role == 'superadmin'.

Gestiona: lista blanca de emails, usuarios y categorías.
"""
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_superadmin
from app.models.user import Usuario
from app.modules.admin import schemas, services

router = APIRouter(prefix="/admin", tags=["SuperAdmin"])


# ---------------------------------------------------------------------------
# Lista blanca de emails
# Controla quién puede registrarse. Sin email en la whitelist → 403.
# ---------------------------------------------------------------------------

@router.get("/whitelist", response_model=List[schemas.ListaBlancaResponse])
def listar_whitelist(
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_superadmin),
):
    return services.listar_lista_blanca(db)


@router.post("/whitelist", response_model=schemas.ListaBlancaResponse, status_code=201)
def agregar_whitelist(
    data: schemas.ListaBlancaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_superadmin),
):
    return services.agregar_a_lista_blanca(db, data, current_user.id)


@router.delete("/whitelist/{entry_id}", status_code=204)
def eliminar_whitelist(
    entry_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_superadmin),
):
    services.eliminar_de_lista_blanca(db, entry_id)


# ---------------------------------------------------------------------------
# Gestión de usuarios
# ---------------------------------------------------------------------------

@router.get("/users", response_model=List[schemas.UsuarioAdminResponse])
def listar_usuarios(
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_superadmin),
):
    return services.listar_usuarios(db)


@router.patch("/users/{user_id}/role", response_model=schemas.UsuarioAdminResponse)
def cambiar_role(
    user_id: int,
    data: schemas.UsuarioRoleUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_superadmin),
):
    return services.actualizar_role(db, user_id, data)


@router.patch("/users/{user_id}/active", response_model=schemas.UsuarioAdminResponse)
def cambiar_activo(
    user_id: int,
    data: schemas.UsuarioActiveUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_superadmin),
):
    return services.actualizar_activo(db, user_id, data)


# ---------------------------------------------------------------------------
# Gestión de categorías
# ---------------------------------------------------------------------------

@router.get("/categories", response_model=List[schemas.CategoriaAdminResponse])
def listar_categorias(
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_superadmin),
):
    return services.listar_categorias(db)


@router.post("/categories", response_model=schemas.CategoriaAdminResponse, status_code=201)
def crear_categoria(
    data: schemas.CategoriaAdminCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_superadmin),
):
    return services.crear_categoria(db, data)


@router.delete("/categories/{cat_id}", status_code=204)
def eliminar_categoria(
    cat_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_superadmin),
):
    services.eliminar_categoria(db, cat_id)
