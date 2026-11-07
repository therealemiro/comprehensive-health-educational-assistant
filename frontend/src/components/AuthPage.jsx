import { useState } from 'react'
import { api } from '../api'

export default function AuthPage({ onAuthenticated }) {
  const [mode, setMode] = useState('login') // 'login' | 'register'
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      if (mode === 'register') {
        await api.register(email, password)
      }
      await api.login(email, password)
      onAuthenticated()
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-brand">
          <PulseMark />
          <span className="auth-brand-title">دستیار آموزشی سلامت</span>
        </div>
        <p className="auth-subtitle">
          {mode === 'login' ? 'وارد حساب خودت شو تا گفتگو رو ادامه بدی' : 'یک حساب جدید بساز'}
        </p>

        {error && <div className="auth-error">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="field-group">
            <label className="field-label" htmlFor="email">ایمیل</label>
            <input
              id="email"
              type="email"
              className="field-input"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
            />
          </div>
          <div className="field-group">
            <label className="field-label" htmlFor="password">رمز عبور</label>
            <input
              id="password"
              type="password"
              className="field-input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={8}
              autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
            />
          </div>
          <button className="btn-primary" type="submit" disabled={loading}>
            {loading ? 'در حال انجام...' : mode === 'login' ? 'ورود' : 'ثبت‌نام'}
          </button>
        </form>

        <div className="auth-switch">
          {mode === 'login' ? (
            <>
              حساب نداری؟ <button onClick={() => setMode('register')}>ثبت‌نام کن</button>
            </>
          ) : (
            <>
              قبلاً ثبت‌نام کردی؟ <button onClick={() => setMode('login')}>وارد شو</button>
            </>
          )}
        </div>

        <div className="auth-disclaimer">
          این دستیار صرفاً اطلاعات آموزشی درباره سلامت، دارو و آزمایش‌ها ارائه می‌دهد و جایگزین
          تشخیص یا مشاوره پزشک نیست.
        </div>
      </div>
    </div>
  )
}

function PulseMark() {
  return (
    <svg width="26" height="20" viewBox="0 0 84 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path
        d="M2 12H24L30 2L38 22L46 12H58L64 4L70 12H82"
        stroke="#1F6F72"
        strokeWidth="3"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}
