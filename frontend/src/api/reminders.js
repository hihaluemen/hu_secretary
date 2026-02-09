import apiClient from './client'

export const fetchTomorrowReminders = async (params) => {
  const { data } = await apiClient.get('/reminders/tomorrow', { params })
  return data
}
