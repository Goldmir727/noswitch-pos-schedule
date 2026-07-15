<script setup lang="ts">
import { ref, onMounted } from "vue";
import api from "../api/client";

interface ConfigItem {
  id_config: number;
  clave: string;
  valor: string;
  tipo: string;
  descripcion: string | null;
}

const configs = ref<ConfigItem[]>([]);
const loading = ref(true);
const saving = ref(false);
const successMsg = ref("");

const editValues: Record<string, string> = {};

function getEditValue(clave: string, valor: string): string {
  if (!(clave in editValues)) {
    editValues[clave] = valor;
  }
  return editValues[clave];
}

function setEditValue(clave: string, val: string) {
  editValues[clave] = val;
}

async function fetchConfigs() {
  loading.value = true;
  try {
    const response = await api.get("/configuracion/");
    configs.value = response.data;
  } catch {} finally {
    loading.value = false;
  }
}

async function saveConfig(clave: string) {
  saving.value = true;
  successMsg.value = "";
  try {
    await api.put(`/configuracion/${clave}`, {
      valor: editValues[clave],
    });
    successMsg.value = "Configuracion guardada";
    setTimeout(() => (successMsg.value = ""), 3000);
  } catch (e: any) {
    alert(e.response?.data?.error?.message || "Error al guardar");
  } finally {
    saving.value = false;
  }
}

function formatLabel(clave: string): string {
  const labels: Record<string, string> = {
    "productos.margen_ganancia_default": "Margen de Ganancia Default (%)",
    "turnos.hora_inicio": "Hora Inicio Calendario",
    "turnos.hora_fin": "Hora Fin Calendario",
  };
  return labels[clave] || clave;
}

onMounted(fetchConfigs);
</script>

<template>
  <div class="page">
    <header class="page-header">
      <h1>Configuracion</h1>
      <router-link to="/admin" class="btn-back">Volver</router-link>
    </header>

    <div v-if="loading" class="loading">Cargando...</div>

    <div v-else class="config-list">
      <div v-if="successMsg" class="success-banner">{{ successMsg }}</div>

      <div v-for="config in configs" :key="config.id_config" class="config-card card">
        <div class="config-header">
          <div class="config-info">
            <span class="config-label">{{ formatLabel(config.clave) }}</span>
            <span class="config-key">{{ config.clave }}</span>
            <span v-if="config.descripcion" class="config-desc">{{ config.descripcion }}</span>
          </div>
        </div>
        <div class="config-body">
          <div class="config-input-row">
            <input
              v-if="config.tipo === 'number'"
              :value="getEditValue(config.clave, config.valor)"
              @input="setEditValue(config.clave, ($event.target as HTMLInputElement).value)"
              type="number"
              min="0"
              max="23"
              class="config-input"
            />
            <input
              v-else
              :value="getEditValue(config.clave, config.valor)"
              @input="setEditValue(config.clave, ($event.target as HTMLInputElement).value)"
              type="text"
              class="config-input"
            />
            <button class="primary btn-save" :disabled="saving" @click="saveConfig(config.clave)">
              Guardar
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page {
  padding: 24px;
  max-width: 800px;
  margin: 0 auto;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.btn-back {
  color: var(--accent);
  text-decoration: none;
}
.loading {
  text-align: center;
  color: var(--text-muted);
  padding: 40px;
}
.success-banner {
  background: var(--success);
  color: white;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 16px;
  font-size: 14px;
  font-weight: 500;
}
.config-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.config-card {
  padding: 20px;
}
.config-header {
  margin-bottom: 16px;
}
.config-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.config-label {
  font-size: 16px;
  font-weight: 600;
}
.config-key {
  font-size: 12px;
  color: var(--text-muted);
  font-family: monospace;
}
.config-desc {
  font-size: 13px;
  color: var(--text-muted);
  margin-top: 4px;
}
.config-input-row {
  display: flex;
  gap: 12px;
  align-items: center;
}
.config-input {
  flex: 1;
  max-width: 200px;
}
.btn-save {
  padding: 10px 24px;
  white-space: nowrap;
}
</style>
