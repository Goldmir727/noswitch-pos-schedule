from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class EstadoComprobante(str, enum.Enum):
    pendiente = "pendiente"
    enviado = "enviado"
    aceptado = "aceptado"
    rechazado = "rechazado"
    contingencia = "contingencia"


class TipoComprobante(str, enum.Enum):
    factura = "factura"
    nota_credito = "nota_credito"
    documento_soporte = "documento_soporte"


class Comprobante(Base):
    __tablename__ = "comprobantes"

    id_comprobante: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_venta: Mapped[int] = mapped_column(Integer, ForeignKey("ventas.id_venta"), index=True)
    tipo: Mapped[TipoComprobante] = mapped_column(Enum(TipoComprobante, name="tipo_comprobante_enum"))
    numero_serie: Mapped[str] = mapped_column(String(20))
    numero_secuencial: Mapped[int] = mapped_column(Integer)
    cufe: Mapped[str | None] = mapped_column(String(100), unique=True)
    qr_data: Mapped[str | None] = mapped_column(Text)
    xml_firmado: Mapped[str | None] = mapped_column(Text)
    estado: Mapped[EstadoComprobante] = mapped_column(
        Enum(EstadoComprobante, name="estado_comprobante_enum"), default=EstadoComprobante.pendiente
    )
    fecha_emision: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    respuesta_pac: Mapped[str | None] = mapped_column(Text)
    intentos_envio: Mapped[int] = mapped_column(Integer, default=0)
    ultimo_intento: Mapped[datetime | None] = mapped_column(DateTime)

    id_sucursal: Mapped[int] = mapped_column(Integer, ForeignKey("sucursales.id_sucursal"))

    venta: Mapped["Venta"] = relationship(back_populates="comprobantes")


class NumeracionDIAN(Base):
    __tablename__ = "numeracion_dian"

    id_numeracion: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_sucursal: Mapped[int] = mapped_column(Integer, ForeignKey("sucursales.id_sucursal"))
    prefijo: Mapped[str] = mapped_column(String(10))
    resolucion: Mapped[str] = mapped_column(String(50))
    rango_inicio: Mapped[int] = mapped_column(Integer)
    rango_fin: Mapped[int] = mapped_column(Integer)
    siguiente_numero: Mapped[int] = mapped_column(Integer)
    vigencia_desde: Mapped[datetime] = mapped_column(DateTime)
    vigencia_hasta: Mapped[datetime] = mapped_column(DateTime)
    activa: Mapped[bool] = mapped_column(default=True)
