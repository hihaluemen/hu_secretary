<template>
  <main class="page">
    <header class="page-header">
      <h1>MiShu Demo Dashboard</h1>
      <p>面向客户演示：自然语言输入 -> 标准化 -> 意图拆分 -> 入库/查询/更新 SQL。</p>
    </header>

    <section v-if="store.errorMessage" class="error-banner">
      {{ store.errorMessage }}
    </section>

    <section class="layout">
      <div class="left-col">
        <InputPanel
          ref="inputPanelRef"
          v-model:input-text="store.inputText"
          v-model:dry-run="store.dryRun"
          :loading="store.loading"
          @submit="store.runProcess"
          @reset-demo="onResetDemo"
          @replay-last="store.replayLast"
          @export-json="store.exportCurrentResult"
          @use-sample="store.setSample"
          @audio-ready="store.setAudioPayload"
          @audio-cleared="onAudioCleared"
        />
        <PipelineResult :loading="store.loading" :result="store.processResult" :asr-text="store.asrText" />
        <RunLogPanel :logs="store.runLogs" />
      </div>

      <div class="right-col">
        <TomorrowReminderPanel :loading="store.remindersLoading" :items="store.tomorrowReminders" />
        <EventTable :loading="store.eventsLoading" :events="store.events" />
        <UpdateSqlPreview :loading="store.loading" :sql="store.updateSqlPreview" />
      </div>
    </section>

    <ConfirmActionModal
      :visible="store.confirmModalVisible"
      :loading="store.loading"
      :preview="store.pendingPreviewResult"
      @cancel="store.cancelPendingExecution"
      @confirm="store.confirmPendingExecution"
    />
  </main>
</template>

<script setup>
import { onMounted } from 'vue'
import { ref } from 'vue'

import ConfirmActionModal from '../components/ConfirmActionModal.vue'
import EventTable from '../components/EventTable.vue'
import InputPanel from '../components/InputPanel.vue'
import PipelineResult from '../components/PipelineResult.vue'
import RunLogPanel from '../components/RunLogPanel.vue'
import TomorrowReminderPanel from '../components/TomorrowReminderPanel.vue'
import UpdateSqlPreview from '../components/UpdateSqlPreview.vue'
import { useDemoStore } from '../stores/demo'

const store = useDemoStore()
const inputPanelRef = ref(null)

onMounted(async () => {
  await store.loadEvents()
  await store.loadTomorrowReminders()
})

const onAudioCleared = () => {
  store.clearAudioPayload()
}

const onResetDemo = async () => {
  await store.resetDemoData()
  inputPanelRef.value?.clearAudio?.()
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: var(--bg-color);
  color: var(--text-color);
  padding: 24px;
}

.page-header {
  margin-bottom: 16px;
}

.page-header h1 {
  font-family: var(--font-heading);
  margin: 0 0 8px;
}

.page-header p {
  margin: 0;
  color: var(--text-muted);
}

.error-banner {
  margin-bottom: 12px;
  background: #fff1f2;
  color: #9f1239;
  border: 1px solid #fecdd3;
  border-radius: 10px;
  padding: 10px 12px;
  font-size: 13px;
}

.layout {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 16px;
}

.left-col,
.right-col {
  display: grid;
  gap: 16px;
}

@media (max-width: 1024px) {
  .layout {
    grid-template-columns: 1fr;
  }
}
</style>
