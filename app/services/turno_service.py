from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import and_, extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.turno import TurnoCalendario, TurnoPlantilla


async def calcular_horas_semana_empleado(
    db: AsyncSession,
    id_usuario: int,
    fecha: date,
) -> float:
    year, week, _ = fecha.isocalendar()
    start_week = date.fromisocalendar(year, week, 1)
    end_week = start_week + timedelta(days=6)

    result = await db.execute(
        select(TurnoCalendario).where(
            and_(
                TurnoCalendario.fecha >= start_week,
                TurnoCalendario.fecha <= end_week,
                (TurnoCalendario.id_usuario_titular == id_usuario)
                | (TurnoCalendario.id_usuario_reemplazo == id_usuario),
                TurnoCalendario.estado_turno.in_(["activo", "finalizado"]),
            )
        )
    )
    turnos = result.scalars().all()

    total_horas = 0.0
    for t in turnos:
        horas = (t.hora_fin.hour + t.hora_fin.minute / 60) - (t.hora_inicio.hour + t.hora_inicio.minute / 60)
        if t.id_usuario_reemplazo == id_usuario and t.horas_reemplazadas_parcial > 0:
            horas = float(t.horas_reemplazadas_parcial)
        total_horas += horas

    return total_horas


async def generar_turnos_desde_plantilla(
    db: AsyncSession,
    fecha_desde: date,
    fecha_hasta: date,
) -> int:
    result = await db.execute(select(TurnoPlantilla).where(TurnoPlantilla.activa == True))
    plantillas = result.scalars().all()

    count = 0
    current = fecha_desde
    while current <= fecha_hasta:
        for plantilla in plantillas:
            if current.weekday() == plantilla.dia_semana.value:
                existing = await db.execute(
                    select(TurnoCalendario).where(
                        and_(
                            TurnoCalendario.id_usuario_titular == plantilla.id_usuario_titular,
                            TurnoCalendario.fecha == current,
                        )
                    )
                )
                if not existing.scalar_one_or_none():
                    turno = TurnoCalendario(
                        id_usuario_titular=plantilla.id_usuario_titular,
                        fecha=current,
                        hora_inicio=plantilla.hora_inicio,
                        hora_fin=plantilla.hora_fin,
                        valor_total_turno=plantilla.valor_total_turno,
                        id_sucursal=plantilla.id_sucursal,
                    )
                    db.add(turno)
                    count += 1
        current += timedelta(days=1)

    return count


async def procesar_solicitud_reemplazo(
    db: AsyncSession,
    id_turno: int,
    id_usuario_solicitante: int,
) -> None:
    from app.models.turno import EstadoTurno

    result = await db.execute(
        select(TurnoCalendario).where(TurnoCalendario.id_turno == id_turno)
    )
    turno = result.scalar_one_or_none()
    if not turno:
        from app.exceptions import NotFoundError
        raise NotFoundError("Turno", id_turno)

    if turno.id_usuario_titular != id_usuario_solicitante:
        from app.exceptions import AuthorizationError
        raise AuthorizationError("Solo el titular puede solicitar reemplazo")

    turno.estado_turno = EstadoTurno.solicitud_reemplazo
