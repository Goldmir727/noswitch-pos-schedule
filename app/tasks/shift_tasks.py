from __future__ import annotations

from celery import shared_task
from sqlalchemy import and_, select

from app.database import async_session_factory
from app.models.turno import EstadoTurno, TurnoCalendario
from app.services.notificacion_service import enviar_push


@shared_task(bind=True)
def check_shift_end_alerts(self) -> dict:
    async def _check():
        from datetime import datetime, timedelta

        async with async_session_factory() as db:
            now = datetime.utcnow()
            in_15_min = now + timedelta(minutes=15)

            result = await db.execute(
                select(TurnoCalendario).where(
                    and_(
                        TurnoCalendario.estado_turno == EstadoTurno.activo,
                        TurnoCalendario.fecha == now.date(),
                    )
                )
            )
            turnos = result.scalars().all()

            alerts_sent = 0
            for turno in turnos:
                hora_fin_dt = turno.hora_fin
                turno_end = datetime.combine(turno.fecha, hora_fin_dt)

                if now <= turno_end <= in_15_min:
                    usuario_id = turno.id_usuario_titular
                    await enviar_push(
                        db,
                        usuario_id,
                        "Tu turno termina pronto",
                        f"Tu turno finaliza a las {hora_fin_dt.strftime('%H:%M')}. Inicia cierre de caja.",
                        tipo="cierre_turno",
                        id_referencia=turno.id_turno,
                    )
                    alerts_sent += 1

            return {"alerts_sent": alerts_sent}

    import asyncio
    return asyncio.get_event_loop().run_until_complete(_check())


@shared_task(bind=True)
def check_weekly_hour_limits(self) -> dict:
    async def _check():
        from datetime import date, timedelta

        async with async_session_factory() as db:
            today = date.today()
            year, week, _ = today.isocalendar()

            from app.services.turno_service import calcular_horas_semana_empleado

            from app.models.usuario import Usuario

            result = await db.execute(select(Usuario).where(Usuario.activo == True))
            usuarios = result.scalars().all()

            alerts = []
            for user in usuarios:
                horas = await calcular_horas_semana_empleado(db, user.id_usuario, today)
                if horas > 40:
                    alerts.append({"usuario": user.nombre_completo, "horas": horas})

            return {"alerts": alerts}

    import asyncio
    return asyncio.get_event_loop().run_until_complete(_check())
