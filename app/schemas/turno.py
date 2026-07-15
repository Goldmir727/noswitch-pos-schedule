from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal

from pydantic import BaseModel

from app.models.turno import EstadoTurno


class TurnoBase(BaseModel):
    id_usuario_titular: int
    fecha: date
    hora_inicio: time
    hora_fin: time
    valor_total_turno: Decimal
    id_sucursal: int


class TurnoCreate(TurnoBase):
    pass


class TurnoRead(TurnoBase):
    id_turno: int
    id_usuario_reemplazo: int | None = None
    horas_reemplazadas_parcial: int = 0
    estado_turno: EstadoTurno
    created_at: datetime

    model_config = {"from_attributes": True}


class TurnoPlantillaBase(BaseModel):
    nombre: str
    dia_semana: int
    hora_inicio: time
    hora_fin: time
    valor_total_turno: Decimal
    id_usuario_titular: int
    id_sucursal: int


class TurnoPlantillaCreate(TurnoPlantillaBase):
    pass


class TurnoPlantillaRead(TurnoPlantillaBase):
    id_plantilla: int
    activa: bool

    model_config = {"from_attributes": True}


class SolicitudReemplazo(BaseModel):
    id_turno: int


class AprobacionReemplazo(BaseModel):
    id_turno: int
    id_usuario_reemplazo: int
    aprobar: bool
