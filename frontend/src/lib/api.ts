const API_URL = window.location.protocol + '//' + window.location.hostname + ':8000'

function readCookie(name: string): string | null {
  const match = document.cookie.match(new RegExp('(^|; )' + name + '=([^;]+)'))
  return match ? decodeURIComponent(match[2]) : null
}

let refreshing: Promise<boolean> | null = null

async function tryRefresh(): Promise<boolean> {
  try {
    const res = await fetch(`${API_URL}/api/auth/refresh`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
    })
    return res.ok
  } catch {
    return false
  }
}

export async function apiRequest(path: string, opts: RequestInit = {}): Promise<Response> {
  const method = (opts.method || 'GET').toUpperCase()
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(opts.headers as Record<string, string> | undefined),
  }
  // CSRF header on every state-changing request (cookie auth).
  if (method !== 'GET' && method !== 'HEAD' && method !== 'OPTIONS') {
    const csrf = readCookie('csrf_token')
    if (csrf) headers['X-CSRF-TOKEN'] = csrf
  }
  const res = await fetch(`${API_URL}${path}`, {
    ...opts,
    method,
    headers,
    credentials: 'include',
  })
  if (res.status === 401) {
    // Silent refresh once, then retry.
    if (!refreshing) refreshing = tryRefresh().finally(() => { refreshing = null })
    const ok = await refreshing
    if (ok) {
      const retry = await fetch(`${API_URL}${path}`, {
        ...opts,
        method,
        headers,
        credentials: 'include',
      })
      return retry
    }
  }
  return res
}

export { API_URL }