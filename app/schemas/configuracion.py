from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ConfiguracionRead(BaseModel):
    id_config: int
    clave: str
    valor: str
    tipo: str
    descripcion: str | None = None
    updated_at: datetime

    model_config = {"from_attributes": True}


class ConfiguracionUpdate(BaseModel):
    valor: str
    tipo: str | None = None
    descripcion: str | None = None
