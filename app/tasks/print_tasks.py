from __future__ import annotations

import json

from celery import shared_task
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_factory
from app.services.impresion_service import imprimir_ticket_venta, imprimir_comprobante_pago


@shared_task(bind=True)
def imprimir_ticket(self, venta_data: dict, detalles: list[dict], pagos: list[dict]) -> dict:
    try:
        imprimir_ticket_venta(venta_data, detalles, pagos)
        return {"status": "success", "venta_id": venta_data.get("id_venta")}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@shared_task(bind=True)
def imprimir_comprobante_pago_task(self, pago_data: dict, copias: int = 2) -> dict:
    try:
        imprimir_comprobante_pago(pago_data, copias)
        return {"status": "success", "pago_id": pago_data.get("id_pago")}
    except Exception as e:
        return {"status": "error", "error": str(e)}
