<script setup lang="ts">
import { RouterView } from "vue-router";
</script>

<template>
  <RouterView />
</template>

<style>
:root {
  --primary: #1a1a2e;
  --primary-light: #16213e;
  --accent: #e94560;
  --accent-hover: #c7384f;
  --text: #eee;
  --text-muted: #aaa;
  --bg: #0f0f23;
  --bg-card: #1a1a2e;
  --border: #2a2a4a;
  --success: #27ae60;
  --warning: #f39c12;
  --danger: #e74c3c;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: "Inter", -apple-system, BlinkMacSystemFont, sans-serif;
  background-color: var(--bg);
  color: var(--text);
  -webkit-font-smoothing: antialiased;
}

button {
  cursor: pointer;
  border: none;
  border-radius: 8px;
  padding: 10px 20px;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s;
}

button.primary {
  background-color: var(--accent);
  color: white;
}

button.primary:hover {
  background-color: var(--accent-hover);
}

input, select {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--bg-card);
  color: var(--text);
  font-size: 14px;
}

input:focus, select:focus {
  outline: none;
  border-color: var(--accent);
}

.card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 20px;
}
</style>
