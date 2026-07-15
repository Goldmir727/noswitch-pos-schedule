from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.exceptions import NotFoundError, StockInsufficientError
from app.models.caja import SesionCaja
from app.models.producto import MovimientoStock, Producto
from app.models.venta import EstadoVenta, MedioPago, Venta, VentaDetalle, VentaPago
from app.schemas.venta import VentaCreate


async def procesar_venta(
    db: AsyncSession,
    data: VentaCreate,
    id_usuario: int,
) -> Venta:
    resultado_subtotal = Decimal("0")
    resultado_impuestos = Decimal("0")
    resultado_descuento = Decimal("0")

    venta = Venta(
        id_sesion_caja=data.id_sesion_caja,
        id_usuario=id_usuario,
        id_cliente=data.id_cliente,
        observacion=data.observacion,
        id_sucursal=0,
    )
    db.add(venta)
    await db.flush()

    for det_data in data.detalles:
        result = await db.execute(select(Producto).where(Producto.id_producto == det_data.id_producto))
        producto = result.scalar_one()

        subtotal_linea = (det_data.precio_unitario - det_data.descuento) * det_data.cantidad
        iva_linea = subtotal_linea * (det_data.iva_porcentaje / Decimal("100"))

        detalle = VentaDetalle(
            id_venta=venta.id_venta,
            id_producto=det_data.id_producto,
            cantidad=det_data.cantidad,
            precio_unitario=det_data.precio_unitario,
            descuento=det_data.descuento,
            iva_porcentaje=det_data.iva_porcentaje,
            subtotal=float(subtotal_linea),
        )
        db.add(detalle)

        producto.stock_actual -= det_data.cantidad

        mov = MovimientoStock(
            id_producto=det_data.id_producto,
            tipo="salida",
            cantidad=det_data.cantidad,
            costo_unitario=producto.costo_compra,
            id_referencia=venta.id_venta,
            tabla_referencia="ventas",
            id_usuario=id_usuario,
            id_sucursal=producto.id_sucursal,
        )
        db.add(mov)

        resultado_subtotal += subtotal_linea
        resultado_impuestos += iva_linea
        resultado_descuento += det_data.descuento * det_data.cantidad

    venta.subtotal = float(resultado_subtotal)
    venta.impuestos = float(resultado_impuestos)
    venta.descuento_total = float(resultado_descuento)
    venta.total = float(resultado_subtotal + resultado_impuestos)
    venta.id_sucursal = data.id_sucursal if hasattr(data, "id_sucursal") else 0

    for pago_data in data.pagos:
        pago = VentaPago(
            id_venta=venta.id_venta,
            id_medio_pago=pago_data.id_medio_pago,
            monto=pago_data.monto,
            referencia_manual=pago_data.referencia_manual,
        )
        db.add(pago)

    result_caja = await db.execute(
        select(SesionCaja).where(SesionCaja.id_sesion_caja == data.id_sesion_caja)
    )
    sesion = result_caja.scalar_one_or_none()
    if sesion:
        total_efectivo = Decimal("0")
        total_digital = Decimal("0")
        total_tarjeta = Decimal("0")

        for pago_data in data.pagos:
            result_medio = await db.execute(
                select(MedioPago).where(MedioPago.id_medio_pago == pago_data.id_medio_pago)
            )
            medio = result_medio.scalar_one_or_none()
            if medio:
                if medio.tipo.value == "efectivo":
                    total_efectivo += pago_data.monto
                elif medio.tipo.value == "tarjeta":
                    total_tarjeta += pago_data.monto
                else:
                    total_digital += pago_data.monto

        sesion.ventas_efectivo = float(Decimal(str(sesion.ventas_efectivo)) + total_efectivo)
        sesion.ventas_digitales = float(Decimal(str(sesion.ventas_digitales)) + total_digital)
        sesion.total_tarjeta = float(Decimal(str(sesion.total_tarjeta)) + total_tarjeta)

    venta.estado = EstadoVenta.pagada

    return venta
