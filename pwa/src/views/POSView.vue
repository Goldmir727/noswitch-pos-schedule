<script setup lang="ts">
import { ref, computed } from "vue";
import { usePOSStore } from "../stores/pos";
import api from "../api/client";

const posStore = usePOSStore();
const scanCode = ref("");
const searchQuery = ref("");
const showPayment = ref(false);
const total = computed(() => posStore.calcularTotal());

async function scanBarcode() {
  if (!scanCode.value) return;
  try {
    const response = await api.get(`/productos/buscar/${scanCode.value}`);
    posStore.agregarProducto(response.data);
    scanCode.value = "";
  } catch {
    alert("Producto no encontrado");
  }
}

function procesarPago(metodo: string) {
  showPayment.value = true;
}
</script>

<template>
  <div class="pos-layout">
    <div class="pos-left">
      <div class="scan-bar">
        <input v-model="scanCode" @keyup.enter="scanBarcode" placeholder="Escanear codigo de barras..." />
        <button @click="scanBarcode" class="primary">Buscar</button>
      </div>
      <div class="carrito">
        <div v-if="posStore.carrito.length === 0" class="empty">Carrito vacio</div>
        <div v-for="item in posStore.carrito" :key="item.id_producto" class="carrito-item">
          <div class="item-info">
            <span class="item-name">{{ item.nombre }}</span>
            <span class="item-qty">x{{ item.cantidad }}</span>
          </div>
          <div class="item-price">
            ${{ (item.precio_unitario * item.cantidad).toLocaleString() }}
            <button @click="posStore.eliminarProducto(item.id_producto)" class="btn-remove">X</button>
          </div>
        </div>
      </div>
      <div class="totals">
        <div class="total-line"><span>Subtotal:</span><span>${{ total.subtotal.toLocaleString() }}</span></div>
        <div class="total-line"><span>IVA:</span><span>${{ total.impuestos.toLocaleString() }}</span></div>
        <div class="total-line total"><span>TOTAL:</span><span>${{ total.total.toLocaleString() }}</span></div>
      </div>
    </div>
    <div class="pos-right">
      <h3>Medio de Pago</h3>
      <div class="payment-methods">
        <button @click="procesarPago('efectivo')" class="pay-btn">Efectivo</button>
        <button @click="procesarPago('tarjeta')" class="pay-btn">Tarjeta</button>
        <button @click="procesarPago('nequi')" class="pay-btn">Nequi</button>
        <button @click="procesarPago('daviplata')" class="pay-btn">Daviplata</button>
        <button @click="procesarPago('pse')" class="pay-btn">PSE</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.pos-layout {
  display: grid;
  grid-template-columns: 1fr 300px;
  height: 100vh;
}
.pos-left, .pos-right {
  padding: 16px;
  display: flex;
  flex-direction: column;
}
.pos-right {
  background: var(--primary);
  border-left: 1px solid var(--border);
}
.scan-bar {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}
.carrito {
  flex: 1;
  overflow-y: auto;
}
.empty {
  text-align: center;
  color: var(--text-muted);
  padding: 40px;
}
.carrito-item {
  display: flex;
  justify-content: space-between;
  padding: 12px;
  border-bottom: 1px solid var(--border);
}
.item-name {
  font-weight: 600;
}
.item-qty {
  color: var(--text-muted);
  margin-left: 8px;
}
.item-price {
  display: flex;
  align-items: center;
  gap: 8px;
}
.btn-remove {
  background: var(--danger);
  color: white;
  padding: 4px 8px;
  font-size: 11px;
}
.totals {
  border-top: 2px solid var(--border);
  padding-top: 12px;
}
.total-line {
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
  font-size: 14px;
}
.total-line.total {
  font-size: 20px;
  font-weight: 700;
  color: var(--accent);
}
h3 {
  margin-bottom: 16px;
}
.payment-methods {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.pay-btn {
  padding: 16px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  color: var(--text);
  font-size: 16px;
  text-align: center;
}
.pay-btn:hover {
  border-color: var(--accent);
  background: var(--primary-light);
}
</style>
