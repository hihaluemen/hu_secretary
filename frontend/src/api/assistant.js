import apiClient from './client'

export const processAssistant = async (payload) => {
  const { data } = await apiClient.post('/assistant/process', payload)
  return data
}

