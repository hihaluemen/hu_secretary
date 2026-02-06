<template>
  <section class="panel">
    <h2>更新 SQL 预览</h2>
    <div v-if="loading" class="state loading">等待处理结果...</div>
    <div v-else-if="!sql" class="state empty">当前无更新 SQL</div>
    <pre v-else class="sql">{{ sql }}</pre>
  </section>
</template>

<script setup>
defineProps({
  loading: {
    type: Boolean,
    required: true,
  },
  sql: {
    type: String,
    default: '',
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

.sql {
  margin: 0;
  background: #082f49;
  color: #e0f2fe;
  border-radius: 10px;
  padding: 12px;
  font-size: 13px;
  line-height: 1.5;
  overflow: auto;
}
</style>

