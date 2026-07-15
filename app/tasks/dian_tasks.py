from __future__ import annotations

import json
from datetime import datetime

import httpx
from celery import shared_task
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.config import get_settings
from app.database import async_session_factory
from app.models.comprobante import Comprobante, EstadoComprobante
from app.services.dian_service import calcular_cufe, generar_qr_data

settings = get_settings()


async def _enviar_a_pac(comprobante: Comprobante, xml_firmado: str) -> dict:
    creds = settings.pac_credentials
    provider = settings.PAC_PROVIDER

    if provider == "carvajal":
        url = creds.get("url_envio", "https://api-homologacion.carvajal.com/v1/send")
        headers = {
            "Authorization": f"Bearer {creds.get('token', '')}",
            "Content-Type": "application/xml",
        }
    elif provider == "tecnosoft":
        url = creds.get("url_envio", "https://api-homologacion.tecnosoft.com.co/v1/documents")
        headers = {
            "Authorization": f"Bearer {creds.get('token', '')}",
            "Content-Type": "application/xml",
        }
    else:
        raise ValueError(f"PAC provider no soportado: {provider}")

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(url, content=xml_firmado.encode("utf-8"), headers=headers)
        response.raise_for_status()
        return response.json()


@shared_task(bind=True, max_retries=5, default_retry_delay=60)
def enviar_comprobante_dian(self, comprobante_id: int) -> dict:
    async def _process():
        async with async_session_factory() as db:
            result = await db.execute(
                select(Comprobante).where(Comprobante.id_comprobante == comprobante_id)
            )
            comprobante = result.scalar_one_or_none()

            if not comprobante:
                return {"error": "Comprobante no encontrado"}

            if comprobante.estado == EstadoComprobante.aceptado:
                return {"status": "ya_aceptado"}

            try:
                respuesta = await _enviar_a_pac(comprobante, comprobante.xml_firmado or "")

                if respuesta.get("status") == "accepted":
                    comprobante.estado = EstadoComprobante.aceptado
                    comprobante.respuesta_pac = json.dumps(respuesta)
                else:
                    comprobante.estado = EstadoComprobante.rechazado
                    comprobante.respuesta_pac = json.dumps(respuesta)

                comprobante.intentos_envio += 1
                comprobante.ultimo_intento = datetime.utcnow()

            except Exception as e:
                comprobante.intentos_envio += 1
                comprobante.ultimo_intento = datetime.utcnow()
                comprobante.respuesta_pac = json.dumps({"error": str(e)})

                if comprobante.intentos_envio >= 5:
                    comprobante.estado = EstadoComprobante.contingencia

                raise self.retry(exc=e)

            return {"comprobante_id": comprobante_id, "estado": comprobante.estado.value}

    import asyncio
    return asyncio.get_event_loop().run_until_complete(_process())
