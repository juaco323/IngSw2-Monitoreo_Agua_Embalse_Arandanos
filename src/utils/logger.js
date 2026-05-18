export function createCorrelationId() {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID()
  }
  return `corr-${Date.now()}-${Math.random().toString(16).slice(2)}`
}

function emit(level, message, context) {
  const prefix = `[${level}] [frontend]`
  const payload = context ? { message, ...context } : message
  if (level === 'FATAL') console.error(prefix, payload)
  else if (level === 'WARN') console.warn(prefix, payload)
  else console.info(prefix, payload)
}

export const appLogger = {
  info: (message, context) => emit('INFO', message, context),
  warn: (message, context) => emit('WARN', message, context),
  fatal: (message, context) => emit('FATAL', message, context),
}

export function fetchWithCorrelation(url, options = {}) {
  const headers = new Headers(options.headers || {})
  headers.set('X-Correlation-Id', createCorrelationId())
  return fetch(url, { ...options, headers }).catch((err) => {
    appLogger.warn('Error de red', { url, message: err.message })
    throw err
  })
}
