from __future__ import annotations

from celery import shared_task
from sqlalchemy import func, select

from app.database import async_session_factory
from app.models.venta import Venta


@shared_task(bind=True)
def daily_sales_report(self) -> dict:
    async def _report():
        from datetime import date

        async with async_session_factory() as db:
            today = date.today()

            result = await db.execute(
                select(
                    func.sum(Venta.total).label("total_ventas"),
                    func.count(Venta.id_venta).label("cantidad_ventas"),
                ).where(Venta.fecha_venta >= today)
            )
            row = result.one_or_none()

            return {
                "fecha": today.isoformat(),
                "total_ventas": float(row.total_ventas or 0),
                "cantidad_ventas": row.cantidad_ventas or 0,
            }

    import asyncio
    return asyncio.get_event_loop().run_until_complete(_report())
