from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import Base, async_session_factory, engine
from app.models.configuracion import Configuracion
from app.models.sucursal import Sucursal
from app.models.usuario import Permiso, Permiso, RolEnum, Usuario
from app.services.auth_service import hash_contrasena


PERMISOS = [
    ("caja.abrir", "Abrir sesion de caja"),
    ("caja.cerrar", "Cerrar sesion de caja"),
    ("caja.ver_panel", "Ver panel doble de caja"),
    ("ventas.crear", "Crear ventas"),
    ("ventas.ver", "Ver ventas"),
    ("productos.crear", "Crear productos"),
    ("productos.editar", "Editar productos"),
    ("productos.ver", "Ver productos"),
    ("turnos.crear", "Crear turnos"),
    ("turnos.aprobar_reemplazo", "Aprobar reemplazos"),
    ("turnos.ver", "Ver turnos"),
    ("pagos.crear", "Crear pagos de sueldo"),
    ("pagos.ver", "Ver pagos de sueldo"),
    ("reportes.ver", "Ver reportes"),
    ("configuracion.editar", "Editar configuracion"),
    ("usuarios.crear", "Crear usuarios"),
    ("usuarios.editar", "Editar usuarios"),
    ("usuarios.ver", "Ver usuarios"),
]

CONFIGURACION_DEFAULT = [
    ("productos.margen_ganancia_default", "30", "number", "Porcentaje de ganancia default al crear productos (0 = desactivado)"),
    ("turnos.hora_inicio", "6", "number", "Hora de inicio del calendario de turnos (0-23)"),
    ("turnos.hora_fin", "22", "number", "Hora de fin del calendario de turnos (0-23)"),
]


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as db:
        sucursal = Sucursal(
            nombre="Sucursal Principal",
            direccion="Calle 123 #45-67",
            telefono="3001234567",
            activa=True,
        )
        db.add(sucursal)
        await db.flush()

        for codigo, descripcion in PERMISOS:
            permiso = Permiso(codigo=codigo, descripcion=descripcion)
            db.add(permiso)

        for clave, valor, tipo, descripcion in CONFIGURACION_DEFAULT:
            config = Configuracion(clave=clave, valor=valor, tipo=tipo, descripcion=descripcion)
            db.add(config)

        admin = Usuario(
            nombre_completo="Administrador Principal",
            documento_identidad="1000000000",
            contrasena_hash=hash_contrasena("admin123"),
            rol=RolEnum.administrador,
            activo=True,
            id_sucursal=sucursal.id_sucursal,
        )
        db.add(admin)

        cajero = Usuario(
            nombre_completo="Cajero Demo",
            documento_identidad="1000000001",
            contrasena_hash=hash_contrasena("cajero123"),
            rol=RolEnum.cajero,
            activo=True,
            id_sucursal=sucursal.id_sucursal,
        )
        db.add(cajero)

        await db.commit()
        print("Seed completado:")
        print(f"  Sucursal: {sucursal.nombre} (ID {sucursal.id_sucursal})")
        print("  Admin: 1000000000 / admin123")
        print("  Cajero: 1000000001 / cajero123")
        print(f"  {len(PERMISOS)} permisos creados")
        print(f"  {len(CONFIGURACION_DEFAULT)} configuraciones default")


if __name__ == "__main__":
    asyncio.run(seed())
