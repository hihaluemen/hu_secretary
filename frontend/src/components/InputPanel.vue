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

    <div class="record-row">
      <span>语音输入：</span>
      <span v-if="!canRecord" class="record-hint">当前浏览器不支持录音</span>
      <button type="button" class="sample" :disabled="loading || !canRecord" @click="toggleRecord">
        {{ isRecording ? '停止录音' : '开始录音' }}
      </button>
      <button type="button" class="ghost" :disabled="loading || !audioUrl" @click="clearAudio">清除录音</button>
      <span class="record-hint">{{ recordHint }}</span>
    </div>

    <div v-if="audioUrl" class="audio-preview">
      <audio :src="audioUrl" controls preload="none" />
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
import { computed, onBeforeUnmount, ref } from 'vue'

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
  'audio-ready',
  'audio-cleared',
])

const onReset = () => emit('reset-demo')
const onReplay = () => emit('replay-last')

const isRecording = ref(false)
const mediaRecorder = ref(null)
const audioChunks = ref([])
const audioUrl = ref('')
const recordHint = computed(() => {
  if (isRecording.value) {
    return '录音中...'
  }
  if (audioUrl.value) {
    return '录音完成，可试听'
  }
  return '点击开始录音'
})
const canRecord =
  typeof navigator !== 'undefined' &&
  !!navigator.mediaDevices?.getUserMedia &&
  typeof MediaRecorder !== 'undefined'

const toggleRecord = async () => {
  if (!canRecord) {
    emit('audio-cleared')
    return
  }
  if (isRecording.value) {
    mediaRecorder.value?.stop()
    return
  }

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    const recorder = new MediaRecorder(stream)
    audioChunks.value = []
    recorder.ondataavailable = (event) => {
      if (event.data && event.data.size > 0) {
        audioChunks.value.push(event.data)
      }
    }
    recorder.onstop = () => {
      const mimeType = recorder.mimeType || 'audio/webm'
      const blob = new Blob(audioChunks.value, { type: mimeType })
      if (audioUrl.value) {
        URL.revokeObjectURL(audioUrl.value)
      }
      audioUrl.value = URL.createObjectURL(blob)
      emit('audio-ready', {
        blob,
        mimeType,
      })
      stream.getTracks().forEach((track) => track.stop())
      isRecording.value = false
    }
    mediaRecorder.value = recorder
    recorder.start()
    isRecording.value = true
  } catch {
    emit('audio-cleared')
  }
}

const clearAudio = () => {
  if (audioUrl.value) {
    URL.revokeObjectURL(audioUrl.value)
  }
  audioUrl.value = ''
  audioChunks.value = []
  emit('audio-cleared')
}

onBeforeUnmount(() => {
  if (audioUrl.value) {
    URL.revokeObjectURL(audioUrl.value)
  }
  if (isRecording.value) {
    mediaRecorder.value?.stop()
  }
})

defineExpose({
  clearAudio,
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

.record-row {
  margin-top: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.record-hint {
  color: var(--text-muted);
  font-size: 12px;
}

.audio-preview {
  margin-top: 10px;
}

.audio-preview audio {
  width: 100%;
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
