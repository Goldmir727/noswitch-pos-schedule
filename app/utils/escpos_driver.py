from __future__ import annotations

from app.services.impresion_service import get_printer, abrir_cajon


def test_printer_connection() -> dict:
    try:
        p = get_printer()
        p.set(align="center", bold=True)
        p.text("TEST CONEXION\n")
        p.text("OK\n")
        p.cut()
        p.close()
        return {"status": "connected", "message": "Impresora responde correctamente"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def test_cash_drawer() -> dict:
    try:
        abrir_cajon()
        return {"status": "ok", "message": "Cajón abierto correctamente"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
