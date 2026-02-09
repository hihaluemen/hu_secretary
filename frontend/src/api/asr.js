import apiClient from './client'

export const transcribeAudio = async ({ file, userId = 'user_001' }) => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('user_id', userId)

  const { data } = await apiClient.post('/asr/transcribe', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return data
}
