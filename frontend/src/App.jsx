import { useEffect, useState } from 'react'
import { api } from './api'
import AuthPage from './components/AuthPage'
import Sidebar from './components/Sidebar'
import ChatWindow from './components/ChatWindow'

function getInitialTheme() {
  const saved = localStorage.getItem('theme')
  if (saved === 'dark' || saved === 'light') return saved
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

export default function App() {
  const [loggedIn, setLoggedIn] = useState(api.isLoggedIn())
  const [chats, setChats] = useState([])
  const [activeChatId, setActiveChatId] = useState(null)
  const [theme, setTheme] = useState(getInitialTheme)

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('theme', theme)
  }, [theme])

  useEffect(() => {
    if (loggedIn) refreshChats()
  }, [loggedIn])

  async function refreshChats() {
    const data = await api.listChats()
    setChats(data)
  }

  async function handleNewChat() {
    const chat = await api.createChat('گفتگوی جدید')
    setChats((prev) => [chat, ...prev])
    setActiveChatId(chat.id)
  }

  async function handleRenameChat(chatId, title) {
    await api.renameChat(chatId, title)
    setChats((prev) => prev.map((c) => (c.id === chatId ? { ...c, title } : c)))
  }

  async function handleDeleteChat(chatId) {
    await api.deleteChat(chatId)
    setChats((prev) => prev.filter((c) => c.id !== chatId))
    if (activeChatId === chatId) setActiveChatId(null)
  }

  async function handleLogout() {
    await api.logout()
    setLoggedIn(false)
    setChats([])
    setActiveChatId(null)
  }

  function toggleTheme() {
    setTheme((t) => (t === 'dark' ? 'light' : 'dark'))
  }

  if (!loggedIn) {
    return <AuthPage onAuthenticated={() => setLoggedIn(true)} />
  }

  const activeChat = chats.find((c) => c.id === activeChatId) || null

  return (
    <div className="app-shell">
      <Sidebar
        chats={chats}
        activeChatId={activeChatId}
        onSelectChat={setActiveChatId}
        onNewChat={handleNewChat}
        onRenameChat={handleRenameChat}
        onDeleteChat={handleDeleteChat}
        onLogout={handleLogout}
        theme={theme}
        onToggleTheme={toggleTheme}
      />
      <ChatWindow chat={activeChat} />
    </div>
  )
}
