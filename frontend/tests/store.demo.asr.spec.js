import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const processAssistantMock = vi.fn()
const createEventsBatchMock = vi.fn()
const executeUpdateSqlMock = vi.fn()
const fetchEventsMock = vi.fn()
const resetDemoEventsMock = vi.fn()

const transcribeAudioMock = vi.fn(async () => ({
  user_id: 'user_001',
  text: '语音转写文本',
  provider: 'dashscope',
  model: 'qwen3-asr-flash',
  mime_type: 'audio/webm',
  file_size: 123,
  duration_ms: 88,
}))

vi.mock('../src/api/assistant', () => ({
  processAssistant: (...args) => processAssistantMock(...args),
}))

vi.mock('../src/api/asr', () => ({
  transcribeAudio: (...args) => transcribeAudioMock(...args),
}))

vi.mock('../src/api/events', () => ({
  fetchEvents: (...args) => fetchEventsMock(...args),
  resetDemoEvents: (...args) => resetDemoEventsMock(...args),
  createEventsBatch: (...args) => createEventsBatchMock(...args),
  executeUpdateSql: (...args) => executeUpdateSqlMock(...args),
}))

const fetchTomorrowRemindersMock = vi.fn()

vi.mock('../src/api/reminders', () => ({
  fetchTomorrowReminders: (...args) => fetchTomorrowRemindersMock(...args),
}))

import { useDemoStore } from '../src/stores/demo'


describe('demo store asr flow', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    processAssistantMock.mockReset()
    processAssistantMock.mockImplementation(async (payload) => ({
      user_id: payload.user_id,
      input: payload.text,
      normalized_input: payload.text,
      intent: { add_content: '', update_content: '', select_content: '' },
      add: { events: [], result: null },
      select: [],
      update_sql: '',
      dry_run: payload.dry_run,
    }))

    createEventsBatchMock.mockReset()
    createEventsBatchMock.mockImplementation(async () => ({
      status: 'success',
      msg: 'ok',
      detail: [],
      success_count: 0,
      fail_count: 0,
    }))

    executeUpdateSqlMock.mockReset()
    executeUpdateSqlMock.mockImplementation(async () => ({
      status: 'success',
      affected_rows: 1,
    }))

    fetchEventsMock.mockReset()
    fetchEventsMock.mockImplementation(async () => [])

    resetDemoEventsMock.mockReset()
    resetDemoEventsMock.mockImplementation(async () => ({ user_id: 'user_001', deleted_count: 0 }))

    fetchTomorrowRemindersMock.mockReset()
    fetchTomorrowRemindersMock.mockImplementation(async () => ({
      user_id: 'user_001',
      remind_date: '2026-02-09',
      target_date: '2026-02-10',
      total: 0,
      items: [],
    }))

    transcribeAudioMock.mockClear()
  })

  it('uses asr text when audio exists', async () => {
    const store = useDemoStore()
    store.inputText = '文本应被忽略'
    store.setAudioPayload({
      blob: new Blob(['abc'], { type: 'audio/webm' }),
      mimeType: 'audio/webm',
    })

    await store.runProcess()
    expect(transcribeAudioMock).toHaveBeenCalledTimes(1)
    expect(processAssistantMock).toHaveBeenCalledTimes(1)
    const calledPayload = processAssistantMock.mock.calls[0][0]
    expect(calledPayload.text).toBe('语音转写文本')
    expect(calledPayload.dry_run).toBe(true)
  })

  it('uses text directly when audio missing', async () => {
    const store = useDemoStore()
    store.inputText = '直接文本'
    await store.runProcess()

    expect(transcribeAudioMock).not.toHaveBeenCalled()
    expect(processAssistantMock).toHaveBeenCalledTimes(1)
    const calledPayload = processAssistantMock.mock.calls[0][0]
    expect(calledPayload.text).toBe('直接文本')
    expect(calledPayload.dry_run).toBe(true)
  })

  it('opens confirm modal for write actions and executes after confirm', async () => {
    const store = useDemoStore()
    store.inputText = '把明天会议改到下午三点'
    processAssistantMock.mockImplementationOnce(async (payload) => ({
      user_id: payload.user_id,
      input: payload.text,
      normalized_input: payload.text,
      intent: {
        add_content: '新增事项',
        update_content: '修改事项',
        select_content: '',
      },
      add: {
        events: [
          {
            event: '项目会议',
            event_time: '2026-02-15 15:00:00',
            location: '1号会议室',
            participants: '李总',
            remark: '',
          },
        ],
        result: null,
      },
      select: [],
      update_sql: "UPDATE events SET location = '1号会议室' WHERE id = 2",
      dry_run: true,
    }))

    await store.runProcess()

    expect(store.confirmModalVisible).toBe(true)
    expect(createEventsBatchMock).toHaveBeenCalledTimes(0)
    expect(executeUpdateSqlMock).toHaveBeenCalledTimes(0)

    await store.confirmPendingExecution()

    expect(store.confirmModalVisible).toBe(false)
    expect(createEventsBatchMock).toHaveBeenCalledTimes(1)
    expect(executeUpdateSqlMock).toHaveBeenCalledTimes(1)
    expect(fetchEventsMock).toHaveBeenCalled()
    expect(fetchTomorrowRemindersMock).toHaveBeenCalled()
  })

  it('keeps input and skips execution when confirm is cancelled', async () => {
    const store = useDemoStore()
    store.inputText = '新增一个事项'
    processAssistantMock.mockImplementationOnce(async (payload) => ({
      user_id: payload.user_id,
      input: payload.text,
      normalized_input: payload.text,
      intent: { add_content: '新增事项', update_content: '', select_content: '' },
      add: {
        events: [{ event: '项目启动会', event_time: '2026-02-16 10:00:00', location: 'A会议室', participants: '李总' }],
        result: null,
      },
      select: [],
      update_sql: '',
      dry_run: true,
    }))

    await store.runProcess()
    store.cancelPendingExecution()

    expect(store.inputText).toBe('新增一个事项')
    expect(store.confirmModalVisible).toBe(false)
    expect(createEventsBatchMock).toHaveBeenCalledTimes(0)
    expect(executeUpdateSqlMock).toHaveBeenCalledTimes(0)
  })
})
