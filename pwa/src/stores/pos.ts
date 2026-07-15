import { defineStore } from "pinia";
import { ref } from "vue";
import api from "../api/client";

interface CarritoItem {
  id_producto: number;
  nombre: string;
  cantidad: number;
  precio_unitario: number;
  descuento: number;
  iva_porcentaje: number;
  subtotal: number;
}

export const usePOSStore = defineStore("pos", () => {
  const carrito = ref<CarritoItem[]>([]);
  const idSesionCaja = ref<number | null>(null);

  function agregarProducto(producto: any, cantidad: number = 1) {
    const existente = carrito.value.find((i) => i.id_producto === producto.id_producto);
    if (existente) {
      existente.cantidad += cantidad;
    } else {
      carrito.value.push({
        id_producto: producto.id_producto,
        nombre: producto.nombre_producto,
        cantidad,
        precio_unitario: Number(producto.precio_venta),
        descuento: 0,
        iva_porcentaje: 19,
        subtotal: Number(producto.precio_venta) * cantidad,
      });
    }
  }

  function eliminarProducto(id_producto: number) {
    carrito.value = carrito.value.filter((i) => i.id_producto !== id_producto);
  }

  function calcularTotal() {
    let subtotal = 0;
    let impuestos = 0;
    for (const item of carrito.value) {
      const sub = (item.precio_unitario - item.descuento) * item.cantidad;
      subtotal += sub;
      impuestos += sub * (item.iva_porcentaje / 100);
    }
    return { subtotal, impuestos, total: subtotal + impuestos };
  }

  async function procesarVenta(pagos: any[]) {
    const response = await api.post("/ventas", {
      id_sesion_caja: idSesionCaja.value,
      detalles: carrito.value.map((i) => ({
        id_producto: i.id_producto,
        cantidad: i.cantidad,
        precio_unitario: i.precio_unitario,
        descuento: i.descuento,
        iva_porcentaje: i.iva_porcentaje,
      })),
      pagos,
    });
    carrito.value = [];
    return response.data;
  }

  return { carrito, idSesionCaja, agregarProducto, eliminarProducto, calcularTotal, procesarVenta };
});
