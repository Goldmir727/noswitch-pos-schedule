from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import NotFoundError
from app.models.pago import PagoSueldo, PagoTurnoDetalle
from app.models.turno import EstadoTurno, TurnoCalendario
from app.schemas.pago import PagoCreate


async def procesar_pago_sueldo(
    db: AsyncSession,
    data: PagoCreate,
    id_administrador: int,
) -> PagoSueldo:
    monto_total = Decimal("0")
    turnos_detalle = []

    for turno_id in data.turnos_ids:
        result = await db.execute(
            select(TurnoCalendario).where(TurnoCalendario.id_turno == turno_id)
        )
        turno = result.scalar_one_or_none()
        if not turno:
            raise NotFoundError("Turno", turno_id)

        if turno.estado_turno != EstadoTurno.finalizado:
            from app.exceptions import ConflictError
            raise ConflictError(f"Turno {turno_id} no está finalizado")

        monto_turno = Decimal(str(turno.valor_total_turno))
        if turno.horas_reemplazadas_parcial > 0:
            horas_totales = (
                (turno.hora_fin.hour + turno.hora_fin.minute / 60)
                - (turno.hora_inicio.hour + turno.hora_inicio.minute / 60)
            )
            valor_hora = monto_turno / Decimal(str(horas_totales))
            monto_turno = valor_hora * Decimal(str(turno.horas_reemplazadas_parcial))

        monto_total += monto_turno
        turnos_detalle.append((turno_id, monto_turno))

    pago = PagoSueldo(
        id_usuario_receptor=data.id_usuario_receptor,
        id_administrador_pagador=id_administrador,
        metodo_pago=data.metodo_pago,
        monto_total=float(monto_total),
    )
    db.add(pago)
    await db.flush()

    for turno_id, monto in turnos_detalle:
        detalle = PagoTurnoDetalle(
            id_pago=pago.id_pago,
            id_turno=turno_id,
            monto_liquidado_turno=float(monto),
        )
        db.add(detalle)

    for turno_id in data.turnos_ids:
        result = await db.execute(
            select(TurnoCalendario).where(TurnoCalendario.id_turno == turno_id)
        )
        turno = result.scalar_one()
        turno.estado_turno = EstadoTurno.pagado

    return pago
