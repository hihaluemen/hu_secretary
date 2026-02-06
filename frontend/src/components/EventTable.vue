<template>
  <section class="panel">
    <h2>事项列表</h2>
    <div v-if="loading" class="state loading">加载事项中...</div>
    <div v-else-if="!events.length" class="state empty">暂无事项数据</div>
    <div v-else class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>事项</th>
            <th>时间</th>
            <th>地点</th>
            <th>参与人</th>
            <th>备注</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in events" :key="item.id">
            <td>{{ item.id }}</td>
            <td>{{ item.event }}</td>
            <td>{{ item.event_time }}</td>
            <td>{{ item.location }}</td>
            <td>{{ item.participants }}</td>
            <td>{{ item.remark || '-' }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<script setup>
defineProps({
  loading: {
    type: Boolean,
    required: true,
  },
  events: {
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

.table-wrap {
  overflow: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  min-width: 720px;
}

th,
td {
  border-bottom: 1px solid #e5eff2;
  padding: 10px;
  text-align: left;
  font-size: 13px;
  vertical-align: top;
}

th {
  background: #f0fbfd;
  color: var(--text-muted);
  font-weight: 600;
}

tbody tr:hover {
  background: #f2fdff;
}
</style>

