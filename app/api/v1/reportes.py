from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.caja import SesionCaja
from app.models.usuario import Usuario
from app.models.venta import Venta
from app.services.auth_service import get_current_admin, get_current_user

router = APIRouter()


@router.get("/ventas-por-dia")
async def ventas_por_dia(
    db: Annotated[AsyncSession, Depends(get_db)],
    _current: Annotated[Usuario, Depends(get_current_admin)],
    fecha_desde: date = Query(...),
    fecha_hasta: date = Query(...),
    id_sucursal: int | None = None,
) -> list[dict]:
    query = (
        select(
            Venta.fecha_venta,
            func.sum(Venta.total).label("total_ventas"),
            func.count(Venta.id_venta).label("cantidad_ventas"),
        )
        .where(Venta.fecha_venta.between(fecha_desde, fecha_hasta))
        .group_by(Venta.fecha_venta)
        .order_by(Venta.fecha_venta)
    )
    if id_sucursal:
        query = query.where(Venta.id_sucursal == id_sucursal)

    result = await db.execute(query)
    rows = result.all()
    return [
        {"fecha": r.fecha_venta.isoformat(), "total": float(r.total_ventas), "cantidad": r.cantidad_ventas}
        for r in rows
    ]


@router.get("/stock-critico")
async def stock_critico(
    db: Annotated[AsyncSession, Depends(get_db)],
    _current: Annotated[Usuario, Depends(get_current_user)],
    id_sucursal: int | None = None,
) -> list[dict]:
    from app.models.producto import Producto

    query = select(Producto).where(Producto.stock_actual <= Producto.stock_minimo_alerta)
    if id_sucursal:
        query = query.where(Producto.id_sucursal == id_sucursal)

    result = await db.execute(query)
    productos = result.scalars().all()
    return [
        {
            "id_producto": p.id_producto,
            "nombre": p.nombre_producto,
            "stock_actual": float(p.stock_actual),
            "stock_minimo": float(p.stock_minimo_alerta),
        }
        for p in productos
    ]


@router.get("/descuadres-caja")
async def descuadres_caja(
    db: Annotated[AsyncSession, Depends(get_db)],
    _current: Annotated[Usuario, Depends(get_current_admin)],
    id_sucursal: int | None = None,
) -> list[dict]:
    query = select(SesionCaja).where(SesionCaja.descuadre.isnot(None), SesionCaja.descuadre != 0)
    if id_sucursal:
        query = query.where(SesionCaja.id_sucursal == id_sucursal)

    result = await db.execute(query)
    sesiones = result.scalars().all()
    return [
        {
            "id_sesion": s.id_sesion_caja,
            "fecha": s.fecha_apertura.isoformat(),
            "usuario": s.id_usuario_creador,
            "descuadre": float(s.descuadre),
        }
        for s in sesiones
    ]
