from __future__ import annotations

from PIL import Image
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer


def generar_qr_pago(
    banco: str,
    numero_cuenta: str,
    monto: float,
    nombre_beneficiario: str = "",
) -> Image.Image:
    payload = f"BANCO:{banco}\nCUENTA:{numero_cuenta}\nMONTO:{monto:.2f}"
    if nombre_beneficiario:
        payload = f"NOMBRE:{nombre_beneficiario}\n{payload}"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(payload)
    qr.make(fit=True)

    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(),
        fill_color="black",
        back_color="white",
    )
    return img


def generar_qr_base64(
    banco: str,
    numero_cuenta: str,
    monto: float,
    nombre_beneficiario: str = "",
) -> str:
    import base64
    from io import BytesIO

    img = generar_qr_pago(banco, numero_cuenta, monto, nombre_beneficiario)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()
