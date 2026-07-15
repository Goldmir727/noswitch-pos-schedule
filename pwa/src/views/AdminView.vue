<script setup lang="ts">
</script>

<template>
  <div class="page">
    <header class="page-header">
      <h1>Administracion</h1>
      <router-link to="/" class="btn-back">Volver</router-link>
    </header>
    <nav class="admin-nav">
      <router-link to="/admin/usuarios" class="nav-card card">Usuarios</router-link>
      <router-link to="/admin/productos" class="nav-card card">Productos</router-link>
      <router-link to="/admin/turnos" class="nav-card card">Calendario Turnos</router-link>
      <router-link to="/admin/reportes" class="nav-card card">Reportes</router-link>
      <router-link to="/admin/configuracion" class="nav-card card">Configuracion</router-link>
    </nav>
  </div>
</template>

<style scoped>
.page { padding: 24px; max-width: 1200px; margin: 0 auto; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.btn-back { color: var(--accent); text-decoration: none; }
.admin-nav { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 16px; }
.nav-card { display: flex; align-items: center; justify-content: center; text-decoration: none; color: var(--text); font-size: 16px; font-weight: 600; padding: 40px; transition: transform 0.2s; }
.nav-card:hover { transform: translateY(-2px); border-color: var(--accent); }
</style>
