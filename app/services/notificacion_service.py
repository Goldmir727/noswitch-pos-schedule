from __future__ import annotations

from datetime import datetime

from pywebpush import webpush
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.turno import DispositivoUsuario, Notificacion

settings = get_settings()


async def enviar_push(
    db: AsyncSession,
    id_usuario: int,
    titulo: str,
    cuerpo: str,
    tipo: str = "general",
    id_referencia: int | None = None,
    tabla_referencia: str | None = None,
) -> None:
    notificacion = Notificacion(
        id_usuario_destino=id_usuario,
        tipo=tipo,
        titulo=titulo,
        cuerpo=cuerpo,
        id_referencia=id_referencia,
        tabla_referencia=tabla_referencia,
    )
    db.add(notificacion)

    result = await db.execute(
        select(DispositivoUsuario).where(
            DispositivoUsuario.id_usuario == id_usuario,
            DispositivoUsuario.activo == True,
        )
    )
    dispositivos = result.scalars().all()

    if not settings.vapid_private_key:
        return

    for disp in dispositivos:
        try:
            subscription_info = {
                "endpoint": disp.endpoint,
                "keys": {"p256dh": disp.p256dh, "auth": disp.auth_key},
            }
            webpush(
                subscription_info=subscription_info,
                data=titulo,
                vapid_private_key=settings.vapid_private_key,
                vapid_claims={"sub": settings.VAPID_CLAIM_EMAIL},
            )
            disp.ultimo_acceso = datetime.utcnow()
        except Exception:
            disp.activo = False


async def notificar_reemplazos_disponibles(
    db: AsyncSession,
    id_turno: int,
    candidatos_ids: list[int],
) -> None:
    from app.models.turno import TurnoCalendario

    result = await db.execute(
        select(TurnoCalendario).where(TurnoCalendario.id_turno == id_turno)
    )
    turno = result.scalar_one()

    for cand_id in candidatos_ids:
        await enviar_push(
            db,
            cand_id,
            "Turno disponible para reemplazo",
            f"Se necesita reemplazo el {turno.fecha} de {turno.hora_inicio} a {turno.hora_fin}",
            tipo="reemplazo",
            id_referencia=id_turno,
            tabla_referencia="turnos_calendario",
        )
