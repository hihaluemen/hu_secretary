import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import { describe, expect, it, vi } from 'vitest'

vi.mock('../src/api/events', () => ({
  fetchEvents: vi.fn(async () => []),
  resetDemoEvents: vi.fn(async () => ({ user_id: 'user_001', deleted_count: 0 })),
  createEventsBatch: vi.fn(async () => ({ status: 'success', detail: [], success_count: 0, fail_count: 0 })),
  executeUpdateSql: vi.fn(async () => ({ status: 'success', affected_rows: 0 })),
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

vi.mock('../src/api/asr', () => ({
  transcribeAudio: vi.fn(async () => ({
    user_id: 'user_001',
    text: '明天上午开会',
    provider: 'dashscope',
    model: 'qwen3-asr-flash',
    mime_type: 'audio/webm',
    file_size: 123,
    duration_ms: 80,
  })),
}))

vi.mock('../src/api/assistant', () => ({
  processAssistant: vi.fn(async () => ({
    user_id: 'user_001',
    input: '',
    normalized_input: '',
    intent: { add_content: '', update_content: '', select_content: '' },
    add: { events: [], result: null },
    select: [],
    update_sql: '',
    dry_run: false,
  })),
}))

import DemoDashboard from '../src/views/DemoDashboard.vue'


describe('DemoDashboard', () => {
  it('renders page title', async () => {
    const router = createRouter({
      history: createWebHistory(),
      routes: [{ path: '/', component: DemoDashboard }],
    })

    router.push('/')
    await router.isReady()

    const wrapper = mount(DemoDashboard, {
      global: {
        plugins: [createPinia(), router],
      },
    })

    expect(wrapper.text()).toContain('MiShu Demo Dashboard')
  })
})
