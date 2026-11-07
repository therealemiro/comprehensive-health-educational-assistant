const API_BASE = 'http://localhost:8000'

function getToken() {
  return localStorage.getItem('access_token')
}

function setToken(token) {
  localStorage.setItem('access_token', token)
}

function clearToken() {
  localStorage.removeItem('access_token')
}

async function request(path, { method = 'GET', body, auth = true } = {}) {
  const headers = { 'Content-Type': 'application/json' }
  if (auth) {
    const token = getToken()
    if (token) headers['Authorization'] = `Bearer ${token}`
  }

  const response = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  })

  if (!response.ok) {
    let detail = 'خطایی رخ داد. لطفاً دوباره تلاش کنید.'
    try {
      const data = await response.json()
      if (data.detail) detail = data.detail
    } catch {
      // JSON response doesn't exist!
    }
    throw new Error(detail)
  }

  if (response.status === 204) return null
  return response.json()
}

export const api = {
  register(email, password) {
    return request('/auth/register', { method: 'POST', body: { email, password }, auth: false })
  },

  async login(email, password) {
    const data = await request('/auth/login', { method: 'POST', body: { email, password }, auth: false })
    setToken(data.access_token)
    return data
  },

  async logout() {
    try {
      await request('/auth/logout', { method: 'POST' })
    } finally {
      clearToken()
    }
  },

  isLoggedIn() {
    return Boolean(getToken())
  },

  listChats() {
    return request('/chats/')
  },

  createChat(title) {
    return request('/chats/', { method: 'POST', body: { title } })
  },

  renameChat(chatId, title) {
    return request(`/chats/${chatId}`, { method: 'PATCH', body: { title } })
  },

  deleteChat(chatId) {
    return request(`/chats/${chatId}`, { method: 'DELETE' })
  },

  listMessages(chatId) {
    return request(`/chats/${chatId}/messages`)
  },

  sendMessage(chatId, content, replyToId = null) {
    return request(`/chats/${chatId}/messages`, {
      method: 'POST',
      body: { content, reply_to_id: replyToId },
    })
  },

  setMessageFeedback(chatId, messageId, feedback) {
    return request(`/chats/${chatId}/messages/${messageId}/feedback`, {
      method: 'PATCH',
      body: { feedback },
    })
  },
}
