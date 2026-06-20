const API_BASE = window.location.origin;

function getToken() {
  return localStorage.getItem("token");
}

function setToken(token) {
  if (token) {
    localStorage.setItem("token", token);
  } else {
    localStorage.removeItem("token");
  }
}

function authHeaders() {
  const token = getToken();
  const headers = { "Content-Type": "application/json" };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
}

async function sendMessageStream({ message, history, session_id, onDelta, signal }) {
  const response = await fetch(`${API_BASE}/api/chat/stream`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ message, history, session_id }),
    signal,
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    const detail = body?.detail || "Erro ao enviar mensagem para o servidor.";
    throw new Error(detail);
  }

  if (!response.body) {
    throw new Error("Streaming nao suportado no ambiente atual.");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder("utf-8");
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const events = buffer.split("\n\n");
    buffer = events.pop() || "";

    for (const rawEvent of events) {
      const line = rawEvent
        .split("\n")
        .find((part) => part.startsWith("data:"));
      if (!line) continue;

      const payloadText = line.slice(5).trim();
      if (!payloadText) continue;

      let payload;
      try {
        payload = JSON.parse(payloadText);
      } catch {
        continue;
      }

      if (payload.error) {
        throw new Error(payload.error);
      }

      if (payload.delta) {
        onDelta(payload.delta);
      }
    }
  }
}

async function apiFetch(path, options = {}) {
  const headers = { ...authHeaders(), ...options.headers };
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body?.detail || `Erro ${response.status}`);
  }
  return response;
}

async function listSessions() {
  const response = await apiFetch("/api/sessions");
  return response.json();
}

async function createSession() {
  const response = await apiFetch("/api/sessions", { method: "POST" });
  return response.json();
}

async function deleteSession(sessionId) {
  await apiFetch(`/api/sessions/${sessionId}`, { method: "DELETE" });
}

async function getSessionMessages(sessionId) {
  const response = await apiFetch(`/api/sessions/${sessionId}/messages`);
  return response.json();
}

async function generateSessionTitle(sessionId, message, reply) {
  const response = await apiFetch("/api/sessions/generate-title", {
    method: "POST",
    body: JSON.stringify({ session_id: sessionId, message, reply }),
  });
  return response.json();
}

// --- Auth ---

async function registerUser(email, password) {
  const response = await apiFetch("/api/auth/register", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  const data = await response.json();
  setToken(data.access_token);
  return data;
}

async function loginUser(email, password) {
  const response = await apiFetch("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  const data = await response.json();
  setToken(data.access_token);
  return data;
}

async function logoutUser() {
  try {
    await apiFetch("/api/auth/logout", { method: "POST" });
  } catch {
    // Ignore errors
  }
  setToken(null);
}

async function getMe() {
  const token = getToken();
  if (!token) return null;
  try {
    const response = await apiFetch("/api/auth/me");
    return response.json();
  } catch {
    setToken(null);
    return null;
  }
}
