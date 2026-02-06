<template>
  <section class="panel">
    <div class="panel-title-row">
      <h2>自然语言输入</h2>
      <div class="actions">
        <button type="button" class="ghost" @click="$emit('export-json')">导出 JSON</button>
        <button type="button" class="ghost" @click="onReplay">重放上次</button>
        <button type="button" class="ghost warning" @click="onReset">重置演示数据</button>
      </div>
    </div>

    <label for="demo-input">请输入待办指令</label>
    <textarea
      id="demo-input"
      :value="inputText"
      rows="5"
      placeholder="例如：明天下午两点在A会议室和张总讨论项目进度。"
      @input="$emit('update:inputText', $event.target.value)"
    />

    <div class="sample-row">
      <span>示例：</span>
      <button type="button" class="sample" @click="$emit('use-sample', 'add')">新增</button>
      <button type="button" class="sample" @click="$emit('use-sample', 'select')">查询</button>
      <button type="button" class="sample" @click="$emit('use-sample', 'update')">更新</button>
    </div>

    <div class="submit-row">
      <label class="checkbox">
        <input
          type="checkbox"
          :checked="dryRun"
          @change="$emit('update:dryRun', $event.target.checked)"
        />
        dry-run（只演示链路不写库）
      </label>
      <button type="button" class="primary" :disabled="loading" @click="$emit('submit')">
        {{ loading ? '处理中...' : '执行处理' }}
      </button>
    </div>
  </section>
</template>

<script setup>
defineProps({
  inputText: {
    type: String,
    required: true,
  },
  dryRun: {
    type: Boolean,
    required: true,
  },
  loading: {
    type: Boolean,
    required: true,
  },
})

const emit = defineEmits([
  'submit',
  'reset-demo',
  'replay-last',
  'export-json',
  'use-sample',
  'update:inputText',
  'update:dryRun',
])

const onReset = () => emit('reset-demo')
const onReplay = () => emit('replay-last')
</script>

<style scoped>
.panel {
  background: #fff;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 16px;
  box-shadow: var(--card-shadow);
}

.panel-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.panel-title-row h2 {
  margin: 0;
  font-family: var(--font-heading);
}

.actions {
  display: flex;
  gap: 8px;
}

label {
  display: block;
  margin-top: 12px;
  margin-bottom: 6px;
  font-size: 14px;
  color: var(--text-muted);
}

textarea {
  width: 100%;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  padding: 10px 12px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s ease;
}

textarea:focus {
  border-color: var(--primary-color);
}

.sample-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 10px;
}

.sample-row span {
  font-size: 13px;
  color: var(--text-muted);
}

.sample,
.ghost,
.primary {
  border: none;
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.sample,
.ghost {
  background: #e8f7fa;
  color: var(--text-color);
}

.sample:hover,
.ghost:hover {
  background: #d3f0f5;
}

.ghost.warning {
  background: #fff7ed;
  color: #c2410c;
}

.ghost.warning:hover {
  background: #ffedd5;
}

.submit-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
  gap: 12px;
}

.checkbox {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  font-size: 13px;
}

.primary {
  background: var(--cta-color);
  color: #fff;
  font-weight: 600;
}

.primary:hover {
  filter: brightness(0.95);
}

.primary:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}
</style>
