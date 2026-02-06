<template>
  <section class="panel">
    <h2>操作流水</h2>
    <div v-if="!logs.length" class="state empty">暂无流水记录</div>
    <ul v-else class="log-list">
      <li v-for="(log, index) in logs.slice(0, 12)" :key="`${log.at}-${index}`">
        <div class="log-head">
          <span class="stage">{{ log.stage }}</span>
          <span class="status" :class="log.status">{{ log.status }}</span>
        </div>
        <p>{{ log.message }}</p>
        <time>{{ formatTime(log.at) }}</time>
      </li>
    </ul>
  </section>
</template>

<script setup>
defineProps({
  logs: {
    type: Array,
    default: () => [],
  },
})

const formatTime = (iso) => {
  try {
    return new Date(iso).toLocaleString()
  } catch {
    return iso
  }
}
</script>

<style scoped>
.panel {
  background: #fff;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 16px;
  box-shadow: var(--card-shadow);
}

h2 {
  margin-top: 0;
  font-family: var(--font-heading);
}

.state {
  border-radius: 10px;
  padding: 12px;
  font-size: 14px;
}

.empty {
  background: #ecfeff;
  color: #155e75;
}

.log-list {
  margin: 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 8px;
}

.log-list li {
  border: 1px solid #e6f2f5;
  border-radius: 10px;
  padding: 10px;
}

.log-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}

.stage {
  font-size: 12px;
  color: var(--text-muted);
}

.status {
  font-size: 12px;
  border-radius: 999px;
  padding: 2px 8px;
}

.status.success {
  background: #dcfce7;
  color: #166534;
}

.status.error {
  background: #ffe4e6;
  color: #be123c;
}

p {
  margin: 0;
  font-size: 13px;
}

time {
  margin-top: 6px;
  display: block;
  font-size: 11px;
  color: var(--text-muted);
}
</style>

