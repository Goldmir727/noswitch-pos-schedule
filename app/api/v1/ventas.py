from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.exceptions import NotFoundError, StockInsufficientError
from app.models.caja import SesionCaja
from app.models.producto import Producto
from app.models.usuario import Usuario
from app.models.venta import Venta, VentaDetalle, VentaPago
from app.schemas.common import PaginatedResponse
from app.schemas.venta import VentaCreate, VentaRead
from app.services.auth_service import get_current_user
from app.services.venta_service import procesar_venta

router = APIRouter()


@router.get("/", response_model=None)
async def list_ventas(
    db: Annotated[AsyncSession, Depends(get_db)],
    _current: Annotated[Usuario, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    id_sucursal: int | None = None,
) -> PaginatedResponse[VentaRead]:
    query = select(Venta).options(selectinload(Venta.detalles), selectinload(Venta.pagos))
    count_query = select(func.count()).select_from(Venta)

    if id_sucursal:
        query = query.where(Venta.id_sucursal == id_sucursal)
        count_query = count_query.where(Venta.id_sucursal == id_sucursal)

    total = (await db.execute(count_query)).scalar() or 0
    offset = (page - 1) * page_size
    result = await db.execute(query.offset(offset).limit(page_size).order_by(Venta.fecha_venta.desc()))
    items = result.scalars().unique().all()

    return PaginatedResponse(
        items=[VentaRead.model_validate(i) for i in items],
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.post("/", response_model=None, status_code=201)
async def create_venta(
    body: VentaCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
) -> VentaRead:
    for det in body.detalles:
        result = await db.execute(select(Producto).where(Producto.id_producto == det.id_producto))
        prod = result.scalar_one_or_none()
        if not prod:
            raise NotFoundError("Producto", det.id_producto)
        if prod.stock_actual < det.cantidad:
            raise StockInsufficientError(prod.nombre_producto, float(prod.stock_actual), float(det.cantidad))

    venta = await procesar_venta(db, body, current_user.id_usuario)
    return VentaRead.model_validate(venta)
