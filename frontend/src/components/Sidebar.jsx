import { useState } from 'react'

export default function Sidebar({
  chats,
  activeChatId,
  onSelectChat,
  onNewChat,
  onRenameChat,
  onDeleteChat,
  onLogout,
  theme,
  onToggleTheme,
}) {
  const [renamingId, setRenamingId] = useState(null)
  const [renameValue, setRenameValue] = useState('')

  function startRename(chat) {
    setRenamingId(chat.id)
    setRenameValue(chat.title)
  }

  function submitRename(chatId) {
    const trimmed = renameValue.trim()
    if (trimmed) onRenameChat(chatId, trimmed)
    setRenamingId(null)
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <span className="sidebar-title">گفتگوهای من</span>
        <button
          className="theme-toggle-btn"
          onClick={onToggleTheme}
          title={theme === 'dark' ? 'حالت روشن' : 'حالت تاریک'}
        >
          {theme === 'dark' ? '☀️' : '🌙'}
        </button>
      </div>

      <button className="btn-new-chat" onClick={onNewChat}>
        + گفتگوی جدید
      </button>

      <div className="chat-list">
        {chats.map((chat) => (
          <div
            key={chat.id}
            className={`chat-list-item ${chat.id === activeChatId ? 'active' : ''}`}
            onClick={() => renamingId !== chat.id && onSelectChat(chat.id)}
          >
            {renamingId === chat.id ? (
              <input
                className="rename-input"
                value={renameValue}
                autoFocus
                onChange={(e) => setRenameValue(e.target.value)}
                onClick={(e) => e.stopPropagation()}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') submitRename(chat.id)
                  if (e.key === 'Escape') setRenamingId(null)
                }}
                onBlur={() => submitRename(chat.id)}
              />
            ) : (
              <>
                <span className="chat-list-item-title">{chat.title}</span>
                <div className="chat-list-item-actions">
                  <button
                    className="icon-btn"
                    title="تغییر نام"
                    onClick={(e) => {
                      e.stopPropagation()
                      startRename(chat)
                    }}
                  >
                    ✎
                  </button>
                  <button
                    className="icon-btn danger"
                    title="حذف گفتگو"
                    onClick={(e) => {
                      e.stopPropagation()
                      if (confirm('این گفتگو برای همیشه حذف می‌شود. مطمئنی؟')) {
                        onDeleteChat(chat.id)
                      }
                    }}
                  >
                    ✕
                  </button>
                </div>
              </>
            )}
          </div>
        ))}
      </div>

      <button className="icon-btn sidebar-logout-btn" onClick={onLogout}>
        خروج از حساب
      </button>
    </aside>
  )
}
