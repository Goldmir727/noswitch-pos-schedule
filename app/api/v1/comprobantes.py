from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.exceptions import NotFoundError
from app.models.comprobante import Comprobante
from app.models.usuario import Usuario
from app.schemas.comprobante import ComprobanteRead
from app.schemas.common import MessageResponse
from app.services.auth_service import get_current_user

router = APIRouter()


@router.get("/venta/{venta_id}", response_model=None)
async def get_comprobantes_venta(
    venta_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _current: Annotated[Usuario, Depends(get_current_user)],
) -> list[ComprobanteRead]:
    result = await db.execute(
        select(Comprobante).where(Comprobante.id_venta == venta_id)
    )
    comprobantes = result.scalars().all()
    return [ComprobanteRead.model_validate(c) for c in comprobantes]


@router.post("/reenviar/{comprobante_id}", response_model=None)
async def reenviar_comprobante(
    comprobante_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _current: Annotated[Usuario, Depends(get_current_user)],
) -> MessageResponse:
    from app.tasks.dian_tasks import enviar_comprobante_dian

    result = await db.execute(
        select(Comprobante).where(Comprobante.id_comprobante == comprobante_id)
    )
    comprobante = result.scalar_one_or_none()
    if not comprobante:
        raise NotFoundError("Comprobante", comprobante_id)

    enviar_comprobante_dian.delay(comprobante_id)
    return MessageResponse(message="Comprobante en cola de reenvío")
