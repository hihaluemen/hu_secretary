import apiClient from './client'

export const fetchEvents = async (params) => {
  const { data } = await apiClient.get('/events', { params })
  return data
}

export const resetDemoEvents = async (params) => {
  const { data } = await apiClient.post('/events/reset-demo', null, { params })
  return data
}

export const createEventsBatch = async (payload) => {
  const { data } = await apiClient.post('/events/batch-create', payload)
  return data
}

export const executeUpdateSql = async (payload) => {
  const { data } = await apiClient.post('/events/execute-update-sql', payload)
  return data
}
