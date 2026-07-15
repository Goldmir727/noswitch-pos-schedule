from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.exceptions import ConflictError, HourLimitExceededError, NotFoundError
from app.models.turno import EstadoTurno, TurnoCalendario, TurnoPlantilla
from app.models.usuario import Usuario
from app.schemas.common import PaginatedResponse, MessageResponse
from app.schemas.turno import (
    AprobacionReemplazo,
    SolicitudReemplazo,
    TurnoCreate,
    TurnoPlantillaCreate,
    TurnoPlantillaRead,
    TurnoRead,
)
from app.services.auth_service import get_current_user, get_current_admin
from app.services.turno_service import (
    calcular_horas_semana_empleado,
    generar_turnos_desde_plantilla,
    procesar_solicitud_reemplazo,
)

router = APIRouter()

WEEKLY_HOUR_LIMIT = 44.0


@router.get("/", response_model=None)
async def list_turnos(
    db: Annotated[AsyncSession, Depends(get_db)],
    _current: Annotated[Usuario, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    fecha_desde: date | None = None,
    fecha_hasta: date | None = None,
    id_usuario: int | None = None,
    id_sucursal: int | None = None,
    estado: str | None = None,
) -> PaginatedResponse[TurnoRead]:
    query = select(TurnoCalendario)
    count_query = select(func.count()).select_from(TurnoCalendario)

    filters = []
    if fecha_desde:
        filters.append(TurnoCalendario.fecha >= fecha_desde)
    if fecha_hasta:
        filters.append(TurnoCalendario.fecha <= fecha_hasta)
    if id_usuario:
        filters.append(
            (TurnoCalendario.id_usuario_titular == id_usuario)
            | (TurnoCalendario.id_usuario_reemplazo == id_usuario)
        )
    if id_sucursal:
        filters.append(TurnoCalendario.id_sucursal == id_sucursal)
    if estado:
        filters.append(TurnoCalendario.estado_turno == estado)

    if filters:
        query = query.where(and_(*filters))
        count_query = count_query.where(and_(*filters))

    total = (await db.execute(count_query)).scalar() or 0
    offset = (page - 1) * page_size
    result = await db.execute(query.offset(offset).limit(page_size).order_by(TurnoCalendario.fecha))
    items = result.scalars().all()

    return PaginatedResponse(
        items=[TurnoRead.model_validate(i) for i in items],
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.post("/", response_model=None, status_code=201)
async def create_turno(
    body: TurnoCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _current: Annotated[Usuario, Depends(get_current_admin)],
) -> TurnoRead:
    turno = TurnoCalendario(**body.model_dump())
    db.add(turno)
    await db.flush()
    return TurnoRead.model_validate(turno)


@router.post("/plantilla", response_model=None, status_code=201)
async def create_plantilla(
    body: TurnoPlantillaCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _current: Annotated[Usuario, Depends(get_current_admin)],
) -> TurnoPlantillaRead:
    plantilla = TurnoPlantilla(**body.model_dump())
    db.add(plantilla)
    await db.flush()
    return TurnoPlantillaRead.model_validate(plantilla)


@router.post("/generar-desde-plantilla", response_model=None)
async def generar_turnos(
    fecha_desde: date,
    fecha_hasta: date,
    db: Annotated[AsyncSession, Depends(get_db)],
    _current: Annotated[Usuario, Depends(get_current_admin)],
) -> MessageResponse:
    count = await generar_turnos_desde_plantilla(db, fecha_desde, fecha_hasta)
    return MessageResponse(message=f"Se generaron {count} turnos desde plantillas")


@router.post("/solicitud-reemplazo", response_model=None)
async def solicitud_reemplazo(
    body: SolicitudReemplazo,
    db: Annotated[AsyncSession, Depends(get_db)],
    _current: Annotated[Usuario, Depends(get_current_user)],
) -> MessageResponse:
    await procesar_solicitud_reemplazo(db, body.id_turno, _current.id_usuario)
    return MessageResponse(message="Solicitud de reemplazo enviada")


@router.post("/aprobar-reemplazo", response_model=None)
async def aprobar_reemplazo(
    body: AprobacionReemplazo,
    db: Annotated[AsyncSession, Depends(get_db)],
    _current: Annotated[Usuario, Depends(get_current_admin)],
) -> MessageResponse:
    result = await db.execute(
        select(TurnoCalendario).where(TurnoCalendario.id_turno == body.id_turno)
    )
    turno = result.scalar_one_or_none()
    if not turno:
        raise NotFoundError("Turno", body.id_turno)

    if body.aprobar:
        horas_empleado = await calcular_horas_semana_empleado(db, body.id_usuario_reemplazo, turno.fecha)
        turno_horas = (turno.hora_fin.hour + turno.hora_fin.minute / 60) - (turno.hora_inicio.hour + turno.hora_inicio.minute / 60)

        if horas_empleado + turno_horas > WEEKLY_HOUR_LIMIT:
            raise HourLimitExceededError(
                f"Empleado {body.id_usuario_reemplazo}",
                horas_empleado + turno_horas,
                WEEKLY_HOUR_LIMIT,
            )

        turno.id_usuario_reemplazo = body.id_usuario_reemplazo
        turno.estado_turno = EstadoTurno.activo
    else:
        turno.estado_turno = EstadoTurno.programado

    return MessageResponse(message="Reemplazo aprobado" if body.aprobar else "Reemplazo rechazado")


@router.delete("/{turno_id}", response_model=None)
async def delete_turno(
    turno_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _current: Annotated[Usuario, Depends(get_current_admin)],
) -> MessageResponse:
    result = await db.execute(
        select(TurnoCalendario).where(TurnoCalendario.id_turno == turno_id)
    )
    turno = result.scalar_one_or_none()
    if not turno:
        raise NotFoundError("Turno", turno_id)

    await db.delete(turno)
    return MessageResponse(message="Turno eliminado")
