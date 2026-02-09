<template>
  <section class="panel">
    <h2>链路结果</h2>

    <div v-if="loading" class="state loading">处理中，请稍候...</div>
    <div v-else-if="!result" class="state empty">暂无结果，点击“执行处理”开始。</div>
    <div v-else class="content">
      <article class="block">
        <h3>标准化输入</h3>
        <p>{{ result.normalized_input || '-' }}</p>
      </article>

      <article v-if="asrText" class="block">
        <h3>ASR 转写文本</h3>
        <p>{{ asrText }}</p>
      </article>

      <article class="block">
        <h3>意图拆分</h3>
        <ul>
          <li><strong>新增：</strong>{{ result.intent?.add_content || '-' }}</li>
          <li><strong>查询：</strong>{{ result.intent?.select_content || '-' }}</li>
          <li><strong>更新：</strong>{{ result.intent?.update_content || '-' }}</li>
        </ul>
      </article>

      <article class="block">
        <h3>新增写库结果</h3>
        <p>{{ result.add?.result?.msg || '无新增写库动作' }}</p>
      </article>
    </div>
  </section>
</template>

<script setup>
defineProps({
  loading: {
    type: Boolean,
    required: true,
  },
  result: {
    type: Object,
    default: null,
  },
  asrText: {
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

.content {
  display: grid;
  gap: 12px;
}

.block {
  border: 1px solid #e6f2f5;
  border-radius: 10px;
  padding: 12px;
}

.block h3 {
  margin: 0 0 8px;
  font-size: 14px;
}

.block p,
.block li {
  margin: 0;
  font-size: 13px;
  color: var(--text-color);
}

.block ul {
  margin: 0;
  padding-left: 16px;
  display: grid;
  gap: 6px;
}
</style>
