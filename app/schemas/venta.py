from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.models.venta import EstadoVenta, MetodoPago


class VentaDetalleCreate(BaseModel):
    id_producto: int
    cantidad: Decimal
    precio_unitario: Decimal
    descuento: Decimal = Decimal("0")
    iva_porcentaje: Decimal = Decimal("19")


class VentaPagoCreate(BaseModel):
    id_medio_pago: int
    monto: Decimal
    referencia_manual: str | None = None


class VentaCreate(BaseModel):
    id_sesion_caja: int
    id_cliente: int | None = None
    detalles: list[VentaDetalleCreate]
    pagos: list[VentaPagoCreate]
    observacion: str | None = None


class VentaDetalleRead(BaseModel):
    id_detalle: int
    id_producto: int
    cantidad: Decimal
    precio_unitario: Decimal
    descuento: Decimal
    iva_porcentaje: Decimal
    subtotal: Decimal

    model_config = {"from_attributes": True}


class VentaPagoRead(BaseModel):
    id_pago_venta: int
    id_medio_pago: int
    monto: Decimal
    referencia_manual: str | None = None
    fecha_pago: datetime

    model_config = {"from_attributes": True}


class VentaRead(BaseModel):
    id_venta: int
    id_sesion_caja: int
    id_usuario: int
    fecha_venta: datetime
    subtotal: Decimal
    impuestos: Decimal
    descuento_total: Decimal
    total: Decimal
    estado: EstadoVenta
    detalles: list[VentaDetalleRead] = []
    pagos: list[VentaPagoRead] = []

    model_config = {"from_attributes": True}
