from __future__ import annotations

from typing import Any

from app.config import get_settings
from app.exceptions import PrinterError

settings = get_settings()

DENOMINACIONES_IMPRESORA = {
    "billete_50000": "$50.000",
    "billete_20000": "$20.000",
    "billete_10000": "$10.000",
    "billete_5000": "$5.000",
    "billete_2000": "$2.000",
    "billete_1000": "$1.000",
    "moneda_500": "$500",
    "moneda_200": "$200",
    "moneda_100": "$100",
    "moneda_50": "$50",
}


def get_printer():
    try:
        from escpos.printer import Usb, Network

        if settings.IMPRESORA_TIPO == "usb":
            vid = int(settings.IMPRESORA_USB_VID, 16)
            pid = int(settings.IMPRESORA_USB_PID, 16)
            return Usb(vid, pid)
        elif settings.IMPRESORA_TIPO == "red":
            return Network(settings.IMPRESORA_RED_HOST, settings.IMPRESORA_RED_PORT)
    except Exception as e:
        raise PrinterError(f"No se pudo conectar impresora: {e}")


def imprimir_ticket_venta(venta_data: dict[str, Any], detalles: list[dict], pagos: list[dict]) -> None:
    p = get_printer()
    try:
        p.set(align="center", bold=True, double_height=True)
        p.text("=== TICKET DE VENTA ===\n")
        p.set(align="left", bold=False, double_height=False)
        p.text(f"Venta #: {venta_data['id_venta']}\n")
        p.text(f"Fecha: {venta_data['fecha_venta']}\n")
        p.text(f"Cajero: {venta_data.get('cajero', 'N/A')}\n")
        p.text("-" * 40 + "\n")

        for det in detalles:
            p.text(f"{det['nombre'][:25]:25} {det['cantidad']:>5} x ${det['precio']:>10.2f}\n")

        p.text("-" * 40 + "\n")
        p.text(f"{'Subtotal:':<30} ${venta_data['subtotal']:>10.2f}\n")
        p.text(f"{'IVA:':<30} ${venta_data['impuestos']:>10.2f}\n")
        p.text(f"{'TOTAL:':<30} ${venta_data['total']:>10.2f}\n")
        p.text("-" * 40 + "\n")

        for pago in pagos:
            p.text(f"Pagado: ${pago['monto']:.2f} ({pago['metodo']})\n")

        p.text("\n")
        p.set(align="center")
        p.text("Gracias por su compra!\n")
        p.cut()
    except Exception as e:
        raise PrinterError(f"Error al imprimir ticket: {e}")
    finally:
        p.close()


def imprimir_comprobante_pago(pago_data: dict, copias: int = 2) -> None:
    for i in range(copias):
        p = get_printer()
        try:
            p.set(align="center", bold=True, double_height=True)
            p.text(f"=== COMPROBANTE DE PAGO ===\n")
            p.text(f"Copia {i + 1}/{copias}\n")
            p.set(align="left", bold=False, double_height=False)
            p.text("-" * 40 + "\n")
            p.text(f"Empleado: {pago_data.get('empleado', 'N/A')}\n")
            p.text(f"Fecha: {pago_data.get('fecha', 'N/A')}\n")
            p.text(f"Metodo: {pago_data.get('metodo', 'N/A')}\n")
            p.text(f"Total: ${pago_data.get('monto_total', 0):.2f}\n")
            p.text("-" * 40 + "\n")

            for turno in pago_data.get("turnos", []):
                p.text(f"Turno {turno['fecha']}: ${turno['monto']:.2f}\n")

            p.text("\n")
            p.set(align="center")
            p.text("_" * 30 + "\n")
            p.text("Firma empleado\n")
            p.text("\n")
            p.cut()
        except Exception as e:
            raise PrinterError(f"Error al imprimir comprobante: {e}")
        finally:
            p.close()


def abrir_cajon() -> None:
    p = get_printer()
    try:
        p.cashdraw(2)
    except Exception as e:
        raise PrinterError(f"Error al abrir cajón: {e}")
    finally:
        p.close()
