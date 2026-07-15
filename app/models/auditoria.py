from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class LogAuditoria(Base):
    __tablename__ = "logs_auditoria"

    id_log: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fecha_hora: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    id_usuario_afectado: Mapped[int | None] = mapped_column(Integer, ForeignKey("usuarios.id_usuario"))
    tipo_evento: Mapped[str] = mapped_column(String(50), index=True)
    descripcion: Mapped[str] = mapped_column(Text)
    datos_extra: Mapped[str | None] = mapped_column(Text)
    ip_address: Mapped[str | None] = mapped_column(String(45))

    id_sucursal: Mapped[int | None] = mapped_column(Integer, ForeignKey("sucursales.id_sucursal"))


class AuditoriaCambio(Base):
    __tablename__ = "auditoria_cambios"

    id_cambio: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tabla_afectada: Mapped[str] = mapped_column(String(50), index=True)
    id_registro: Mapped[int] = mapped_column(Integer)
    campo: Mapped[str] = mapped_column(String(50))
    valor_anterior: Mapped[str | None] = mapped_column(Text)
    valor_nuevo: Mapped[str | None] = mapped_column(Text)
    id_usuario: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id_usuario"))
    fecha: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
