from __future__ import annotations

import enum
from datetime import date, datetime, time

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    Time,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class EstadoTurno(str, enum.Enum):
    programado = "programado"
    solicitud_reemplazo = "solicitud_reemplazo"
    reemplazo_pendiente_aprobacion = "reemplazo_pendiente_aprobacion"
    activo = "activo"
    finalizado = "finalizado"
    pagado = "pagado"


class DiaSemana(int, enum.Enum):
    lunes = 0
    martes = 1
    miercoles = 2
    jueves = 3
    viernes = 4
    sabado = 5
    domingo = 6


class TurnoCalendario(Base):
    __tablename__ = "turnos_calendario"

    id_turno: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_usuario_titular: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id_usuario"), index=True)
    id_usuario_reemplazo: Mapped[int | None] = mapped_column(Integer, ForeignKey("usuarios.id_usuario"))
    fecha: Mapped[date] = mapped_column(index=True)
    hora_inicio: Mapped[time] = mapped_column(Time)
    hora_fin: Mapped[time] = mapped_column(Time)
    valor_total_turno: Mapped[float] = mapped_column(Numeric(12, 2))
    horas_reemplazadas_parcial: Mapped[int] = mapped_column(Integer, default=0)
    estado_turno: Mapped[EstadoTurno] = mapped_column(
        Enum(EstadoTurno, name="estado_turno_enum"), default=EstadoTurno.programado
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    id_sucursal: Mapped[int] = mapped_column(Integer, ForeignKey("sucursales.id_sucursal"), index=True)

    titular: Mapped["Usuario"] = relationship(
        foreign_keys=[id_usuario_titular], back_populates="turnos_titular"
    )
    reemplazo: Mapped["Usuario | None"] = relationship(
        foreign_keys=[id_usuario_reemplazo], back_populates="turnos_reemplazo"
    )


class TurnoPlantilla(Base):
    __tablename__ = "turno_plantillas"

    id_plantilla: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100))
    dia_semana: Mapped[DiaSemana] = mapped_column(Enum(DiaSemana, name="dia_semana_enum"))
    hora_inicio: Mapped[time] = mapped_column(Time)
    hora_fin: Mapped[time] = mapped_column(Time)
    valor_total_turno: Mapped[float] = mapped_column(Numeric(12, 2))
    id_usuario_titular: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id_usuario"))
    activa: Mapped[bool] = mapped_column(Boolean, default=True)
    id_sucursal: Mapped[int] = mapped_column(Integer, ForeignKey("sucursales.id_sucursal"))


class Festivo(Base):
    __tablename__ = "festivos"

    id_festivo: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fecha: Mapped[date] = mapped_column(unique=True)
    nombre: Mapped[str] = mapped_column(String(100))
    recurrente_anual: Mapped[bool] = mapped_column(Boolean, default=False)


class DispositivoUsuario(Base):
    __tablename__ = "dispositivos_usuario"

    id_dispositivo: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_usuario: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id_usuario"), index=True)
    endpoint: Mapped[str] = mapped_column(Text, unique=True)
    p256dh: Mapped[str] = mapped_column(String(255))
    auth_key: Mapped[str] = mapped_column(String(255))
    plataforma: Mapped[str] = mapped_column(String(20))
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    ultimo_acceso: Mapped[datetime | None] = mapped_column(DateTime)


class Notificacion(Base):
    __tablename__ = "notificaciones"

    id_notificacion: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_usuario_destino: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id_usuario"), index=True)
    tipo: Mapped[str] = mapped_column(String(50))
    titulo: Mapped[str] = mapped_column(String(200))
    cuerpo: Mapped[str] = mapped_column(Text)
    leida: Mapped[bool] = mapped_column(Boolean, default=False)
    fecha_envio: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    id_referencia: Mapped[int | None] = mapped_column(Integer)
    tabla_referencia: Mapped[str | None] = mapped_column(String(50))
