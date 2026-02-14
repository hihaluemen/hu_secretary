<template>
  <div v-if="visible" class="mask" role="dialog" aria-modal="true" aria-label="确认执行写库操作">
    <section class="modal">
      <header class="header">
        <h3>确认执行写库操作</h3>
        <p>请确认以下内容，确认后会写入数据库。</p>
      </header>

      <div v-if="hasAddEvents" class="block">
        <h4>新增事项（{{ addEvents.length }}）</h4>
        <ul>
          <li v-for="(item, idx) in addEvents" :key="idx">
            <span class="line">{{ item.event || item['事件内容'] || '未知事项' }}</span>
            <span class="meta">
              {{ item.event_time || item['开始时间'] || '-' }} ·
              {{ item.location || item['地点'] || '-' }} ·
              {{ item.participants || item['人物'] || '-' }}
            </span>
          </li>
        </ul>
      </div>

      <div v-if="hasUpdateSql" class="block">
        <h4>更新 SQL</h4>
        <pre>{{ preview?.update_sql }}</pre>
      </div>

      <footer class="actions">
        <button type="button" class="ghost" :disabled="loading" @click="$emit('cancel')">取消</button>
        <button type="button" class="primary" :disabled="loading" @click="$emit('confirm')">
          {{ loading ? '执行中...' : '确认执行' }}
        </button>
      </footer>
    </section>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false,
  },
  loading: {
    type: Boolean,
    default: false,
  },
  preview: {
    type: Object,
    default: null,
  },
})

defineEmits(['confirm', 'cancel'])

const addEvents = computed(() => props.preview?.add?.events || [])
const hasAddEvents = computed(() => addEvents.value.length > 0)
const hasUpdateSql = computed(() => !!props.preview?.update_sql)
</script>

<style scoped>
.mask {
  position: fixed;
  inset: 0;
  background: rgba(2, 6, 23, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
  padding: 16px;
}

.modal {
  width: min(760px, 100%);
  max-height: calc(100vh - 32px);
  overflow: auto;
  background: #fff;
  border-radius: 14px;
  border: 1px solid #dbeafe;
  box-shadow: 0 24px 48px rgba(15, 23, 42, 0.25);
  padding: 18px;
}

.header h3 {
  margin: 0;
  font-family: var(--font-heading);
}

.header p {
  margin: 6px 0 0;
  color: var(--text-muted);
  font-size: 13px;
}

.block {
  margin-top: 14px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 12px;
  background: #f8fafc;
}

.block h4 {
  margin: 0 0 8px;
  font-size: 14px;
}

ul {
  margin: 0;
  padding-left: 18px;
}

li + li {
  margin-top: 8px;
}

.line {
  display: block;
  color: #0f172a;
  font-size: 14px;
}

.meta {
  display: block;
  margin-top: 2px;
  color: #475569;
  font-size: 12px;
}

pre {
  margin: 0;
  background: #082f49;
  color: #e0f2fe;
  border-radius: 10px;
  padding: 12px;
  font-size: 12px;
  line-height: 1.5;
  overflow: auto;
}

.actions {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.ghost,
.primary {
  border: none;
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 13px;
  cursor: pointer;
}

.ghost {
  background: #e2e8f0;
  color: #0f172a;
}

.primary {
  background: var(--primary-color);
  color: #fff;
}

.ghost:disabled,
.primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}
</style>
