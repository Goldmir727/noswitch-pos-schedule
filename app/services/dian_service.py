from __future__ import annotations

from datetime import datetime
from decimal import Decimal
import hashlib
import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.exceptions import DIANError
from app.models.comprobante import Comprobante, EstadoComprobante, NumeracionDIAN, TipoComprobante

settings = get_settings()


def calcular_cufe(
    numero_documento: str,
    fecha_emision: str,
    total: str,
    nit_empresa: str,
    codigo_producto: str,
) -> str:
    data = f"{numero_documento}{fecha_emision}{total}{nit_empresa}{codigo_producto}"
    return hashlib.sha256(data.encode()).hexdigest().upper()


async def obtener_siguiente_numero(
    db: AsyncSession,
    id_sucursal: int,
    tipo: TipoComprobante,
) -> tuple[str, int]:
    result = await db.execute(
        select(NumeracionDIAN).where(
            NumeracionDIAN.id_sucursal == id_sucursal,
            NumeracionDIAN.activa == True,
        )
    )
    numeracion = result.scalar_one_or_none()
    if not numeracion:
        raise DIANError("No hay numeración DIAN configurada para esta sucursal")

    if numeracion.siguiente_numero > numeracion.rango_fin:
        raise DIANError("Rango de numeración agotado")

    numero = numeracion.siguiente_numero
    numeracion.siguiente_numero += 1

    return f"{numeracion.prefijo}{numero:010d}", numero


def generar_qr_data(
    cufe: str,
    fecha: datetime,
    total: float,
    link_resolucion: str,
) -> str:
    return f"{link_resolucion}?cufe={cufe}&fecha={fecha.isoformat()}&total={total:.2f}"


async def crear_comprobante_pendiente(
    db: AsyncSession,
    id_venta: int,
    id_sucursal: int,
    tipo: TipoComprobante,
    total: float,
) -> Comprobante:
    from app.models.venta import Venta

    numero_str, numero_sec = await obtener_siguiente_numero(db, id_sucursal, tipo)

    venta_result = await db.execute(
        select(Venta).where(Venta.id_venta == id_venta)
    )
    venta = venta_result.scalar_one()

    cufe = calcular_cufe(
        numero_documento=numero_str,
        fecha_emision=venta.fecha_venta.isoformat(),
        total=f"{total:.2f}",
        nit_empresa=settings.DIAN_NIT,
        codigo_producto="",
    )

    qr_data = generar_qr_data(
        cufe=cufe,
        fecha=venta.fecha_venta,
        total=total,
        link_resolucion="https://catalogo.dian.gov.co/sdp/querying",
    )

    comprobante = Comprobante(
        id_venta=id_venta,
        tipo=tipo,
        numero_serie=numero_str,
        numero_secuencial=numero_sec,
        cufe=cufe,
        qr_data=qr_data,
        estado=EstadoComprobante.pendiente,
        id_sucursal=id_sucursal,
    )
    db.add(comprobante)
    await db.flush()

    return comprobante
