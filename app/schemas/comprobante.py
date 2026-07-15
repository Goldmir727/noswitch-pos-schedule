from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.models.comprobante import EstadoComprobante, TipoComprobante


class ComprobanteRead(BaseModel):
    id_comprobante: int
    id_venta: int
    tipo: TipoComprobante
    numero_serie: str
    numero_secuencial: int
    cufe: str | None = None
    estado: EstadoComprobante
    fecha_emision: datetime

    model_config = {"from_attributes": True}
