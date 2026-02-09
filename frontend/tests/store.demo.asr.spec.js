import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const processAssistantMock = vi.fn(async (payload) => ({
  user_id: payload.user_id,
  input: payload.text,
  normalized_input: payload.text,
  intent: { add_content: '', update_content: '', select_content: '' },
  add: { events: [], result: null },
  select: [],
  update_sql: '',
  dry_run: payload.dry_run,
}))

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
  fetchEvents: vi.fn(async () => []),
  resetDemoEvents: vi.fn(async () => ({ user_id: 'user_001', deleted_count: 0 })),
}))

vi.mock('../src/api/reminders', () => ({
  fetchTomorrowReminders: vi.fn(async () => ({
    user_id: 'user_001',
    remind_date: '2026-02-09',
    target_date: '2026-02-10',
    total: 0,
    items: [],
  })),
}))

import { useDemoStore } from '../src/stores/demo'


describe('demo store asr flow', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    processAssistantMock.mockClear()
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
  })

  it('uses text directly when audio missing', async () => {
    const store = useDemoStore()
    store.inputText = '直接文本'
    await store.runProcess()

    expect(transcribeAudioMock).not.toHaveBeenCalled()
    expect(processAssistantMock).toHaveBeenCalledTimes(1)
    const calledPayload = processAssistantMock.mock.calls[0][0]
    expect(calledPayload.text).toBe('直接文本')
  })
})
