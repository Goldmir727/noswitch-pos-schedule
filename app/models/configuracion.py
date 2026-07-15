from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Configuracion(Base):
    __tablename__ = "configuracion"
    __table_args__ = (UniqueConstraint("clave", name="uq_configuracion_clave"),)

    id_config: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    clave: Mapped[str] = mapped_column(String(100))
    valor: Mapped[str] = mapped_column(Text)
    tipo: Mapped[str] = mapped_column(String(20), default="string")
    descripcion: Mapped[str | None] = mapped_column(Text)
    id_sucursal: Mapped[int | None] = mapped_column(Integer)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
