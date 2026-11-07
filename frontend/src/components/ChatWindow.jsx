import { useEffect, useRef, useState } from 'react'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { api } from '../api'
import PulseLoader from './PulseLoader'

function renderAssistantContent(content) {
  const rawHtml = marked.parse(content, { breaks: true })
  return { __html: DOMPurify.sanitize(rawHtml) }
}

function truncate(text, max = 60) {
  return text.length > max ? text.slice(0, max) + '…' : text
}

export default function ChatWindow({ chat }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [error, setError] = useState('')
  const [replyingTo, setReplyingTo] = useState(null) // { id, content }
  const [copiedId, setCopiedId] = useState(null)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    if (!chat) return
    setError('')
    setReplyingTo(null)
    api.listMessages(chat.id).then(setMessages).catch((err) => setError(err.message))
  }, [chat])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, sending])

  function findMessageById(id) {
    return messages.find((m) => m.id === id)
  }

  async function handleSend(e) {
    e.preventDefault()
    const content = input.trim()
    if (!content || sending) return

    const replyToId = replyingTo?.id || null
    setInput('')
    setReplyingTo(null)
    setError('')
    setMessages((prev) => [
      ...prev,
      { id: `temp-${Date.now()}`, role: 'user', content, reply_to_id: replyToId },
    ])
    setSending(true)

    try {
      const assistantMessage = await api.sendMessage(chat.id, content, replyToId)
      setMessages((prev) => [...prev, assistantMessage])
    } catch (err) {
      setError(err.message)
    } finally {
      setSending(false)
    }
  }

  async function handleFeedback(message, feedback) {
    const newFeedback = message.feedback === feedback ? null : feedback 
    setMessages((prev) =>
      prev.map((m) => (m.id === message.id ? { ...m, feedback: newFeedback } : m))
    )
    try {
      await api.setMessageFeedback(chat.id, message.id, newFeedback)
    } catch (err) {
      setError(err.message)
    }
  }

  async function handleCopy(message) {
    try {
      await navigator.clipboard.writeText(message.content)
      setCopiedId(message.id)
      setTimeout(() => setCopiedId(null), 1500)
    } catch {
      setError('کپی کردن پاسخ ممکن نشد.')
    }
  }

  function handleDownloadChat() {
    const lines = messages.map((m) => {
      const speaker = m.role === 'user' ? 'کاربر' : 'دستیار'
      return `${speaker}: ${m.content}`
    })
    const text = lines.join('\n\n')
    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${chat.title.replace(/\s+/g, '_')}.txt`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  if (!chat) {
    return (
      <main className="chat-main">
        <div className="empty-state">
          <div className="empty-state-title">یک گفتگو رو انتخاب کن یا یکی جدید بساز</div>
          <div>دستیار آموزشی سلامت آماده پاسخ به سوالات آموزشی توئه</div>
        </div>
      </main>
    )
  }

  return (
    <main className="chat-main">
      <div className="chat-topbar">
        <span>{chat.title}</span>
        <div className="chat-topbar-actions">
          <button
            className="btn-topbar-action"
            onClick={handleDownloadChat}
            disabled={messages.length === 0}
            title="دانلود گفتگو به‌صورت فایل متنی"
          >
            ⬇ دانلود گفتگو
          </button>
        </div>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && !sending && (
          <div className="empty-state">
            <div className="empty-state-title">سوالت رو درباره سلامت، دارو یا آزمایش‌ها بپرس</div>
          </div>
        )}

        {messages.map((msg) => {
          const repliedMessage = msg.reply_to_id ? findMessageById(msg.reply_to_id) : null
          return (
            <div key={msg.id} className={`message-block ${msg.role}`}>
              {repliedMessage && (
                <div className="reply-preview">↩ {truncate(repliedMessage.content, 70)}</div>
              )}

              <div className={`message-row ${msg.role}`}>
                {msg.role === 'assistant' ? (
                  <div
                    className="message-bubble markdown-body"
                    dangerouslySetInnerHTML={renderAssistantContent(msg.content)}
                  />
                ) : (
                  <div className="message-bubble">{msg.content}</div>
                )}
              </div>

              <div className="message-actions">
                <button className="icon-btn" title="ریپلای" onClick={() => setReplyingTo(msg)}>
                  ↩
                </button>

                {msg.role === 'assistant' && !msg.id.toString().startsWith('temp-') && (
                  <>
                    <button className="icon-btn" title="کپی پاسخ" onClick={() => handleCopy(msg)}>
                      ⧉
                    </button>
                    {copiedId === msg.id && <span className="copy-toast">کپی شد!</span>}
                    <button
                      className={`icon-btn ${msg.feedback === 'like' ? 'active-feedback' : ''}`}
                      title="پاسخ مفید بود"
                      onClick={() => handleFeedback(msg, 'like')}
                    >
                      👍
                    </button>
                    <button
                      className={`icon-btn ${msg.feedback === 'dislike' ? 'active-feedback' : ''}`}
                      title="پاسخ مفید نبود"
                      onClick={() => handleFeedback(msg, 'dislike')}
                    >
                      👎
                    </button>
                  </>
                )}
              </div>
            </div>
          )
        })}

        {sending && <PulseLoader />}
        <div ref={messagesEndRef} />
      </div>

      {error && <div className="auth-error" style={{ margin: '0 24px' }}>{error}</div>}

      {replyingTo && (
        <div className="reply-banner">
          <span className="reply-banner-text">در پاسخ به: {truncate(replyingTo.content, 80)}</span>
          <button className="reply-banner-cancel" onClick={() => setReplyingTo(null)}>
            ✕
          </button>
        </div>
      )}

      <form className="chat-input-bar" onSubmit={handleSend}>
        <textarea
          className="chat-input"
          rows={1}
          placeholder="پیامت رو بنویس..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              handleSend(e)
            }
          }}
        />
        <button className="btn-send" type="submit" disabled={sending || !input.trim()}>
          ➤
        </button>
      </form>
      <div className="disclaimer-strip">پاسخ‌ها صرفاً آموزشی هستند، نه تشخیص یا تجویز پزشکی</div>
    </main>
  )
}
