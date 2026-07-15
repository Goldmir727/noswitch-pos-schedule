from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class EstadoVenta(str, enum.Enum):
    pendiente = "pendiente"
    pagada = "pagada"
    anulada = "anulada"
    contigencia = "contingencia"


class MetodoPago(str, enum.Enum):
    efectivo = "efectivo"
    tarjeta = "tarjeta"
    nequi = "nequi"
    daviplata = "daviplata"
    pse = "pse"


class MedioPago(Base):
    __tablename__ = "medios_pago"

    id_medio_pago: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(50))
    tipo: Mapped[MetodoPago] = mapped_column(Enum(MetodoPago, name="metodo_pago_enum"), unique=True)
    comision_porcentaje: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    requiere_qr: Mapped[bool] = mapped_column(default=False)
    requiere_referencia: Mapped[bool] = mapped_column(default=False)
    activo: Mapped[bool] = mapped_column(default=True)


class Venta(Base):
    __tablename__ = "ventas"

    id_venta: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_sesion_caja: Mapped[int] = mapped_column(Integer, ForeignKey("sesiones_caja.id_sesion_caja"), index=True)
    id_usuario: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id_usuario"))
    id_cliente: Mapped[int | None] = mapped_column(Integer, ForeignKey("clientes.id_cliente"))
    fecha_venta: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    subtotal: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    impuestos: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    descuento_total: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    total: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    estado: Mapped[EstadoVenta] = mapped_column(Enum(EstadoVenta, name="estado_venta_enum"), default=EstadoVenta.pendiente)
    observacion: Mapped[str | None] = mapped_column(Text)

    id_sucursal: Mapped[int] = mapped_column(Integer, ForeignKey("sucursales.id_sucursal"), index=True)

    detalles: Mapped[list[VentaDetalle]] = relationship(back_populates="venta", cascade="all, delete-orphan")
    pagos: Mapped[list[VentaPago]] = relationship(back_populates="venta", cascade="all, delete-orphan")
    comprobantes: Mapped[list["Comprobante"]] = relationship(back_populates="venta")


class VentaDetalle(Base):
    __tablename__ = "venta_detalle"

    id_detalle: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_venta: Mapped[int] = mapped_column(Integer, ForeignKey("ventas.id_venta"), index=True)
    id_producto: Mapped[int] = mapped_column(Integer, ForeignKey("productos.id_producto"))
    cantidad: Mapped[float] = mapped_column(Numeric(12, 2))
    precio_unitario: Mapped[float] = mapped_column(Numeric(12, 2))
    descuento: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    iva_porcentaje: Mapped[float] = mapped_column(Numeric(5, 2), default=19.0)
    subtotal: Mapped[float] = mapped_column(Numeric(12, 2))

    venta: Mapped[Venta] = relationship(back_populates="detalles")
    producto: Mapped["Producto"] = relationship()


class VentaPago(Base):
    __tablename__ = "venta_pago"

    id_pago_venta: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_venta: Mapped[int] = mapped_column(Integer, ForeignKey("ventas.id_venta"), index=True)
    id_medio_pago: Mapped[int] = mapped_column(Integer, ForeignKey("medios_pago.id_medio_pago"))
    monto: Mapped[float] = mapped_column(Numeric(12, 2))
    referencia_manual: Mapped[str | None] = mapped_column(String(100))
    fecha_pago: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    venta: Mapped[Venta] = relationship(back_populates="pagos")
    medio_pago: Mapped[MedioPago] = relationship()
