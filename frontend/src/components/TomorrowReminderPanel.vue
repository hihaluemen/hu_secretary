<template>
  <section class="panel">
    <h2>明日提醒</h2>
    <div v-if="loading" class="state loading">加载明日提醒中...</div>
    <div v-else-if="!items.length" class="state empty">明日暂无提醒事项</div>
    <ul v-else class="reminder-list">
      <li v-for="item in items" :key="item.event_id">
        <p class="title">{{ item.event }}</p>
        <p class="meta">{{ item.event_time }} · {{ item.location }}</p>
        <p class="meta">参与人：{{ item.participants }}</p>
      </li>
    </ul>
  </section>
</template>

<script setup>
defineProps({
  loading: {
    type: Boolean,
    required: true,
  },
  items: {
    type: Array,
    default: () => [],
  },
})
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

.loading {
  background: #e0f2fe;
  color: #0c4a6e;
}

.empty {
  background: #ecfeff;
  color: #155e75;
}

.reminder-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 8px;
}

.reminder-list li {
  border: 1px solid #e6f2f5;
  border-radius: 10px;
  padding: 10px;
}

.title {
  margin: 0;
  font-weight: 600;
  font-size: 14px;
}

.meta {
  margin: 4px 0 0;
  color: var(--text-muted);
  font-size: 12px;
}
</style>
