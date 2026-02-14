import { defineStore } from 'pinia'

import { processAssistant } from '../api/assistant'
import { transcribeAudio } from '../api/asr'
import { createEventsBatch, executeUpdateSql, fetchEvents, resetDemoEvents } from '../api/events'
import { fetchTomorrowReminders } from '../api/reminders'

const hasObjectUrlApi = typeof URL !== 'undefined' && typeof URL.createObjectURL === 'function'
const hasRevokeObjectUrlApi = typeof URL !== 'undefined' && typeof URL.revokeObjectURL === 'function'

const SAMPLE_INPUTS = {
  add: '明天上午9点在政务办和李总开项目启动会，提醒我带上项目计划书。',
  select: '帮我查一下明天上午和李总相关的事项。',
  update: '把明天和李总的会议改到下午3点，地点改成1号会议室。',
}

export const useDemoStore = defineStore('demo', {
  state: () => ({
    userId: 'user_001',
    inputText: '',
    dryRun: false,
    loading: false,
    eventsLoading: false,
    errorMessage: '',
    processResult: null,
    events: [],
    requestHistory: [],
    runLogs: [],
    audioBlob: null,
    audioMimeType: '',
    audioObjectUrl: '',
    asrText: '',
    remindersLoading: false,
    tomorrowReminders: [],
    confirmModalVisible: false,
    pendingPreviewResult: null,
    pendingExecutionPlan: null,
  }),
  getters: {
    hasProcessResult: (state) => !!state.processResult,
    hasEvents: (state) => state.events.length > 0,
    updateSqlPreview: (state) => state.processResult?.update_sql || '',
  },
  actions: {
    setSample(type) {
      this.inputText = SAMPLE_INPUTS[type] || ''
    },
    async runProcess() {
      if (!this.inputText.trim() && !this.audioBlob) {
        this.errorMessage = '请输入待处理内容'
        return
      }
      this.loading = true
      this.errorMessage = ''
      const startedAt = performance.now()
      try {
        let finalInputText = this.inputText
        this.asrText = ''

        if (this.audioBlob) {
          const audioName = this.audioMimeType.includes('wav') ? 'recording.wav' : 'recording.webm'
          const file = new File([this.audioBlob], audioName, {
            type: this.audioMimeType || 'audio/webm',
          })
          const asrResult = await transcribeAudio({
            file,
            userId: this.userId,
          })
          this.asrText = asrResult?.text || ''
          finalInputText = this.asrText
          this.runLogs.unshift({
            at: new Date().toISOString(),
            stage: 'asr.transcribe',
            status: 'success',
            message: `语音识别完成，获得 ${this.asrText.length} 字`,
          })
          if (!finalInputText.trim()) {
            throw new Error('语音识别结果为空，请重试')
          }
        }

        const payload = {
          user_id: this.userId,
          text: finalInputText,
          dry_run: true,
        }
        const result = await processAssistant(payload)
        this.processResult = result
        this.pendingPreviewResult = result
        const elapsed = Math.round(performance.now() - startedAt)
        this.requestHistory.unshift({
          input: finalInputText,
          at: new Date().toISOString(),
          normalized: result.normalized_input,
          elapsed,
        })
        this.runLogs.unshift({
          at: new Date().toISOString(),
          stage: 'assistant.process',
          status: 'success',
          message: `处理完成，耗时 ${elapsed}ms`,
        })

        const addEvents = result?.add?.events || []
        const updateSql = (result?.update_sql || '').trim()
        const needsConfirm = !this.dryRun && (addEvents.length > 0 || !!updateSql)

        if (needsConfirm) {
          this.pendingExecutionPlan = {
            addEvents,
            updateSql,
          }
          this.confirmModalVisible = true
          this.runLogs.unshift({
            at: new Date().toISOString(),
            stage: 'assistant.confirm',
            status: 'pending',
            message: '检测到新增或更新操作，请确认后执行',
          })
          return
        }

        this.confirmModalVisible = false
        this.pendingExecutionPlan = null
        this.pendingPreviewResult = null
        await this.loadEvents()
        await this.loadTomorrowReminders()
      } catch (error) {
        this.errorMessage = error.message
        this.confirmModalVisible = false
        this.pendingExecutionPlan = null
        this.pendingPreviewResult = null
        if (this.audioBlob && !this.asrText) {
          this.runLogs.unshift({
            at: new Date().toISOString(),
            stage: 'asr.transcribe',
            status: 'error',
            message: error.message,
          })
        }
        this.runLogs.unshift({
          at: new Date().toISOString(),
          stage: 'assistant.process',
          status: 'error',
          message: error.message,
        })
      } finally {
        this.loading = false
      }
    },
    cancelPendingExecution() {
      this.confirmModalVisible = false
      this.pendingExecutionPlan = null
      this.pendingPreviewResult = null
      this.runLogs.unshift({
        at: new Date().toISOString(),
        stage: 'assistant.confirm',
        status: 'cancel',
        message: '已取消写库执行',
      })
    },
    async confirmPendingExecution() {
      if (!this.pendingExecutionPlan) {
        this.confirmModalVisible = false
        return
      }

      this.loading = true
      this.errorMessage = ''
      try {
        const { addEvents, updateSql } = this.pendingExecutionPlan
        let addResult = this.pendingPreviewResult?.add?.result || null
        let updateExecuteResult = null

        if (addEvents.length > 0) {
          addResult = await createEventsBatch({
            user_id: this.userId,
            events: addEvents,
          })
          this.runLogs.unshift({
            at: new Date().toISOString(),
            stage: 'events.batch-create',
            status: 'success',
            message: `新增执行完成：成功 ${addResult.success_count || 0} 条`,
          })
        }

        if (updateSql) {
          updateExecuteResult = await executeUpdateSql({
            user_id: this.userId,
            sql: updateSql,
          })
          this.runLogs.unshift({
            at: new Date().toISOString(),
            stage: 'events.execute-update-sql',
            status: 'success',
            message: `更新执行完成：影响 ${updateExecuteResult.affected_rows || 0} 条`,
          })
        }

        if (this.pendingPreviewResult) {
          this.processResult = {
            ...this.pendingPreviewResult,
            dry_run: false,
            add: {
              ...(this.pendingPreviewResult.add || {}),
              result: addResult,
            },
            update_execute: updateExecuteResult,
          }
        }

        this.confirmModalVisible = false
        this.pendingExecutionPlan = null
        this.pendingPreviewResult = null
        this.runLogs.unshift({
          at: new Date().toISOString(),
          stage: 'assistant.confirm',
          status: 'success',
          message: '写库执行成功',
        })
        await this.loadEvents()
        await this.loadTomorrowReminders()
      } catch (error) {
        this.errorMessage = error.message
        this.runLogs.unshift({
          at: new Date().toISOString(),
          stage: 'assistant.confirm',
          status: 'error',
          message: error.message,
        })
      } finally {
        this.loading = false
      }
    },
    async loadEvents() {
      this.eventsLoading = true
      try {
        const data = await fetchEvents({ user_id: this.userId })
        this.events = data
        this.runLogs.unshift({
          at: new Date().toISOString(),
          stage: 'events.list',
          status: 'success',
          message: `已加载 ${data.length} 条事项`,
        })
      } catch (error) {
        this.errorMessage = error.message
        this.runLogs.unshift({
          at: new Date().toISOString(),
          stage: 'events.list',
          status: 'error',
          message: error.message,
        })
      } finally {
        this.eventsLoading = false
      }
    },
    async loadTomorrowReminders() {
      this.remindersLoading = true
      try {
        const data = await fetchTomorrowReminders({ user_id: this.userId })
        this.tomorrowReminders = data?.items || []
        this.runLogs.unshift({
          at: new Date().toISOString(),
          stage: 'reminders.tomorrow',
          status: 'success',
          message: `已加载 ${this.tomorrowReminders.length} 条明日提醒`,
        })
      } catch (error) {
        this.errorMessage = error.message
        this.runLogs.unshift({
          at: new Date().toISOString(),
          stage: 'reminders.tomorrow',
          status: 'error',
          message: error.message,
        })
      } finally {
        this.remindersLoading = false
      }
    },
    async resetDemoData() {
      this.loading = true
      this.errorMessage = ''
      try {
        await resetDemoEvents({ user_id: this.userId })
        this.processResult = null
        this.confirmModalVisible = false
        this.pendingExecutionPlan = null
        this.pendingPreviewResult = null
        this.clearAudioPayload()
        this.requestHistory = []
        this.runLogs.unshift({
          at: new Date().toISOString(),
          stage: 'events.reset-demo',
          status: 'success',
          message: '演示数据已重置',
        })
        await this.loadEvents()
        await this.loadTomorrowReminders()
      } catch (error) {
        this.errorMessage = error.message
        this.runLogs.unshift({
          at: new Date().toISOString(),
          stage: 'events.reset-demo',
          status: 'error',
          message: error.message,
        })
      } finally {
        this.loading = false
      }
    },
    replayLast() {
      const latest = this.requestHistory[0]
      if (!latest) {
        this.errorMessage = '暂无可重放请求'
        return
      }
      this.inputText = latest.input
      this.runLogs.unshift({
        at: new Date().toISOString(),
        stage: 'assistant.replay',
        status: 'success',
        message: '已填充最近一次请求内容',
      })
    },
    exportCurrentResult() {
      if (!this.processResult) {
        this.errorMessage = '暂无可导出结果'
        return
      }
      const payload = {
        exported_at: new Date().toISOString(),
        user_id: this.userId,
        result: this.processResult,
        events: this.events,
      }
      const blob = new Blob([JSON.stringify(payload, null, 2)], {
        type: 'application/json;charset=utf-8',
      })
      const url = URL.createObjectURL(blob)
      const anchor = document.createElement('a')
      anchor.href = url
      anchor.download = `mishu-demo-${Date.now()}.json`
      document.body.appendChild(anchor)
      anchor.click()
      anchor.remove()
      URL.revokeObjectURL(url)
      this.runLogs.unshift({
        at: new Date().toISOString(),
        stage: 'assistant.export',
        status: 'success',
        message: '当前结果已导出 JSON',
      })
    },
    setAudioPayload({ blob, mimeType }) {
      this.audioBlob = blob
      this.audioMimeType = mimeType || ''
      this.asrText = ''
      if (this.audioObjectUrl && hasRevokeObjectUrlApi) {
        URL.revokeObjectURL(this.audioObjectUrl)
      }
      this.audioObjectUrl = blob && hasObjectUrlApi ? URL.createObjectURL(blob) : ''
      this.runLogs.unshift({
        at: new Date().toISOString(),
        stage: 'audio.record',
        status: 'success',
        message: blob ? '录音已就绪，可执行处理' : '录音已清除',
      })
    },
    clearAudioPayload() {
      this.audioBlob = null
      this.audioMimeType = ''
      this.asrText = ''
      if (this.audioObjectUrl && hasRevokeObjectUrlApi) {
        URL.revokeObjectURL(this.audioObjectUrl)
      }
      this.audioObjectUrl = ''
      this.runLogs.unshift({
        at: new Date().toISOString(),
        stage: 'audio.record',
        status: 'success',
        message: '录音已清除',
      })
    },
  },
})
