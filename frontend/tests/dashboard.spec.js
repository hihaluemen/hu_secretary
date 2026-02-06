import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import { describe, expect, it, vi } from 'vitest'

vi.mock('../src/api/events', () => ({
  fetchEvents: vi.fn(async () => []),
  resetDemoEvents: vi.fn(async () => ({ user_id: 'user_001', deleted_count: 0 })),
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
