<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import api from "../api/client";

const turnosPendientes = ref<any[]>([]);
const selected = ref<Set<number>>(new Set());
const loading = ref(true);

onMounted(async () => {
  try {
    const response = await api.get("/pagos/turnos-pendientes");
    turnosPendientes.value = response.data;
  } catch {} finally {
    loading.value = false;
  }
});

const totalSeleccionado = computed(() =>
  turnosPendientes.value
    .filter((t) => selected.value.has(t.id_turno))
    .reduce((sum, t) => sum + t.valor_total_turno, 0)
);

function toggle(id: number) {
  if (selected.value.has(id)) selected.value.delete(id);
  else selected.value.add(id);
}

async function procesarPago(metodo: string) {
  if (selected.value.size === 0) return;
  try {
    await api.post("/pagos/", {
      id_usuario_receptor: 0,
      metodo_pago: metodo,
      turnos_ids: Array.from(selected.value),
    });
    alert("Pago procesado");
    selected.value.clear();
    const response = await api.get("/pagos/turnos-pendientes");
    turnosPendientes.value = response.data;
  } catch (e: any) {
    alert(e.response?.data?.error?.message || "Error");
  }
}
</script>

<template>
  <div class="page">
    <header class="page-header">
      <h1>Mis Pagos</h1>
      <router-link to="/" class="btn-back">Volver</router-link>
    </header>
    <div v-if="loading" class="loading">Cargando...</div>
    <div v-else>
      <div v-if="turnosPendientes.length === 0" class="empty">No hay turnos pendientes por cobrar</div>
      <div v-else>
        <div v-for="turno in turnosPendientes" :key="turno.id_turno" class="turno-row card" @click="toggle(turno.id_turno)">
          <input type="checkbox" :checked="selected.has(turno.id_turno)" />
          <div class="turno-info">
            <span>{{ turno.fecha }} | {{ turno.hora_inicio }} - {{ turno.hora_fin }}</span>
            <span class="turno-valor">${{ turno.valor_total_turno.toLocaleString() }}</span>
          </div>
        </div>
        <div class="payment-bar">
          <span class="total-label">Seleccionados: {{ selected.size }} | Total: ${{ totalSeleccionado.toLocaleString() }}</span>
          <div class="payment-actions">
            <button @click="procesarPago('efectivo')" class="primary">Efectivo</button>
            <button @click="procesarPago('transferencia')" class="primary">Transferencia</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page { padding: 24px; max-width: 800px; margin: 0 auto; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.btn-back { color: var(--accent); text-decoration: none; }
.loading, .empty { text-align: center; color: var(--text-muted); padding: 40px; }
.turno-row { display: flex; align-items: center; gap: 12px; cursor: pointer; margin-bottom: 8px; }
.turno-row:hover { border-color: var(--accent); }
.turno-info { display: flex; justify-content: space-between; flex: 1; }
.turno-valor { font-weight: 700; color: var(--accent); }
.payment-bar { position: fixed; bottom: 0; left: 0; right: 0; background: var(--primary); border-top: 1px solid var(--border); padding: 16px 24px; display: flex; justify-content: space-between; align-items: center; }
.total-label { font-weight: 600; }
.payment-actions { display: flex; gap: 8px; }
</style>
