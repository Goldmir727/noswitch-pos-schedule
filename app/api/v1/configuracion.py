from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.exceptions import NotFoundError
from app.models.configuracion import Configuracion
from app.models.usuario import Usuario
from app.schemas.common import MessageResponse
from app.schemas.configuracion import ConfiguracionRead, ConfiguracionUpdate
from app.services.auth_service import get_current_admin, get_current_user

router = APIRouter()


@router.get("/public", response_model=None)
async def get_public_config(
    db: Annotated[AsyncSession, Depends(get_db)],
    _current: Annotated[Usuario, Depends(get_current_user)],
) -> dict:
    public_keys = ["turnos.hora_inicio", "turnos.hora_fin", "productos.margen_ganancia_default"]
    result = await db.execute(
        select(Configuracion).where(Configuracion.clave.in_(public_keys))
    )
    configs = result.scalars().all()
    return {c.clave: c.valor for c in configs}


@router.get("/", response_model=None)
async def list_config(
    db: Annotated[AsyncSession, Depends(get_db)],
    _current: Annotated[Usuario, Depends(get_current_admin)],
) -> list[ConfiguracionRead]:
    result = await db.execute(select(Configuracion).order_by(Configuracion.clave))
    configs = result.scalars().all()
    return [ConfiguracionRead.model_validate(c) for c in configs]


@router.get("/{clave}", response_model=None)
async def get_config(
    clave: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    _current: Annotated[Usuario, Depends(get_current_admin)],
) -> ConfiguracionRead:
    result = await db.execute(select(Configuracion).where(Configuracion.clave == clave))
    config = result.scalar_one_or_none()
    if not config:
        raise NotFoundError("Configuracion", clave)
    return ConfiguracionRead.model_validate(config)


@router.put("/{clave}", response_model=None)
async def update_config(
    clave: str,
    body: ConfiguracionUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _current: Annotated[Usuario, Depends(get_current_admin)],
) -> ConfiguracionRead:
    result = await db.execute(select(Configuracion).where(Configuracion.clave == clave))
    config = result.scalar_one_or_none()
    if not config:
        raise NotFoundError("Configuracion", clave)

    config.valor = body.valor
    if body.tipo:
        config.tipo = body.tipo
    if body.descripcion:
        config.descripcion = body.descripcion

    return ConfiguracionRead.model_validate(config)
