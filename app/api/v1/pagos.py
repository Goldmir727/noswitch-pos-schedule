from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.exceptions import NotFoundError
from app.models.pago import PagoSueldo, PagoTurnoDetalle
from app.models.turno import EstadoTurno, TurnoCalendario
from app.models.usuario import Usuario
from app.schemas.common import PaginatedResponse, MessageResponse
from app.schemas.pago import PagoCreate, PagoRead
from app.services.auth_service import get_current_user, get_current_admin
from app.services.pago_service import procesar_pago_sueldo

router = APIRouter()


@router.get("/turnos-pendientes")
async def get_turnos_pendientes_pago(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
) -> list[dict]:
    query = (
        select(TurnoCalendario)
        .where(
            TurnoCalendario.id_usuario_titular == current_user.id_usuario,
            TurnoCalendario.estado_turno == EstadoTurno.finalizado,
        )
        .order_by(TurnoCalendario.fecha)
    )
    result = await db.execute(query)
    turnos = result.scalars().all()
    return [
        {
            "id_turno": t.id_turno,
            "fecha": t.fecha.isoformat(),
            "hora_inicio": t.hora_inicio.isoformat(),
            "hora_fin": t.hora_fin.isoformat(),
            "valor_total_turno": float(t.valor_total_turno),
        }
        for t in turnos
    ]


@router.post("/", response_model=None, status_code=201)
async def create_pago(
    body: PagoCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_admin: Annotated[Usuario, Depends(get_current_admin)],
) -> PagoRead:
    pago = await procesar_pago_sueldo(db, body, current_admin.id_usuario)
    return PagoRead.model_validate(pago)


@router.get("/", response_model=None)
async def list_pagos(
    db: Annotated[AsyncSession, Depends(get_db)],
    _current: Annotated[Usuario, Depends(get_current_admin)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PaginatedResponse[PagoRead]:
    query = select(PagoSueldo).options(selectinload(PagoSueldo.detalles))
    count_query = select(func.count()).select_from(PagoSueldo)

    total = (await db.execute(count_query)).scalar() or 0
    offset = (page - 1) * page_size
    result = await db.execute(query.offset(offset).limit(page_size).order_by(PagoSueldo.fecha_pago.desc()))
    items = result.scalars().unique().all()

    return PaginatedResponse(
        items=[PagoRead.model_validate(i) for i in items],
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )
