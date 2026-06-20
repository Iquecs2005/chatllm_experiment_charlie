const { useEffect, useMemo, useRef, useState, useCallback } = React;

function createMessageId() {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
}

function App() {
  const [sessions, setSessions] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const messagesRef = useRef(null);
  const abortControllerRef = useRef(null);
  const sessionsLoadedRef = useRef(false);
  const titledSessionsRef = useRef(new Set());

  // Load sessions on mount
  useEffect(() => {
    (async () => {
      try {
        const data = await listSessions();
        setSessions(data.sessions);
        // Mark sessions that already have a non-default title as titled
        for (const s of data.sessions) {
          if (s.title !== "Novo Chat") {
            titledSessionsRef.current.add(s.id);
          }
        }
        if (data.sessions.length > 0) {
          setCurrentSessionId(data.sessions[0].id);
        }
      } catch (err) {
        console.error("Failed to load sessions:", err);
      }
    })();
  }, []);

  // Load messages when session changes
  useEffect(() => {
    if (!currentSessionId) {
      setMessages([]);
      return;
    }
    (async () => {
      try {
        const msgs = await getSessionMessages(currentSessionId);
        setMessages(msgs.length > 0 ? msgs : []);
      } catch (err) {
        console.error("Failed to load messages:", err);
        setMessages([]);
      }
    })();
  }, [currentSessionId]);

  const chatHistory = useMemo(
    () => messages.filter((msg) => msg.role === "user" || msg.role === "assistant"),
    [messages]
  );

  useEffect(() => {
    const el = messagesRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages]);

  useEffect(() => {
    return () => {
      abortControllerRef.current?.abort();
    };
  }, []);

  const handleNewSession = useCallback(async () => {
    try {
      const newSession = await createSession();
      setSessions((prev) => [newSession, ...prev]);
      setCurrentSessionId(newSession.id);
    } catch (err) {
      setError("Erro ao criar sessao: " + err.message);
    }
  }, []);

  const handleDeleteSession = useCallback(async (sessionId, event) => {
    event.stopPropagation();
    try {
      await deleteSession(sessionId);
      titledSessionsRef.current.delete(sessionId);
      setSessions((prev) => prev.filter((s) => s.id !== sessionId));
      if (currentSessionId === sessionId) {
        setCurrentSessionId(null);
        setMessages([]);
      }
    } catch (err) {
      setError("Erro ao deletar sessao: " + err.message);
    }
  }, [currentSessionId]);

  const handleSelectSession = useCallback((sessionId) => {
    setCurrentSessionId(sessionId);
    setError("");
  }, []);

  const onStop = () => {
    abortControllerRef.current?.abort();
    abortControllerRef.current = null;
    setBusy(false);
  };

  const onSubmit = async (event, inputRef) => {
    event.preventDefault();
    const cleaned = text.trim();
    if (!cleaned || busy) return;

    // Auto-create session if none selected
    let sessionId = currentSessionId;
    if (!sessionId) {
      try {
        const newSession = await createSession();
        setSessions((prev) => [newSession, ...prev]);
        sessionId = newSession.id;
        setCurrentSessionId(sessionId);
      } catch (err) {
        setError("Erro ao criar sessao: " + err.message);
        return;
      }
    }

    setError("");
    const userMessage = { id: createMessageId(), role: "user", content: cleaned };
    const assistantMessageId = createMessageId();

    setMessages((prev) => [
      ...prev,
      userMessage,
      { id: assistantMessageId, role: "assistant", content: "" },
    ]);
    setText("");
    setBusy(true);
    const abortController = new AbortController();
    abortControllerRef.current = abortController;

    // Track reply content live — avoids stale closure on messages state
    let replyContent = "";

    try {
      await sendMessageStream({
        message: cleaned,
        session_id: sessionId,
        history: chatHistory,
        signal: abortController.signal,
        onDelta: (delta) => {
          replyContent += delta;
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantMessageId
                ? { ...msg, content: `${msg.content}${delta}` }
                : msg
            )
          );
        },
      });

      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === assistantMessageId && !msg.content.trim()
            ? { ...msg, content: "Nao foi possivel obter resposta do modelo agora." }
            : msg
        )
      );

      // Generate title only once per session — track via ref to avoid stale closure
      if (replyContent.trim() && !titledSessionsRef.current.has(sessionId)) {
        titledSessionsRef.current.add(sessionId);
        try {
          const result = await generateSessionTitle(sessionId, cleaned, replyContent);
          setSessions((prev) => prev.map((s) => s.id === sessionId ? { ...s, title: result.title } : s));
        } catch (e) {
          // Non-critical — remove from set so it can retry on next message
          titledSessionsRef.current.delete(sessionId);
        }
      }
    } catch (err) {
      const aborted = err?.name === "AbortError";
      if (!aborted) {
        setError(err.message || "Falha inesperada ao gerar resposta.");
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantMessageId
              ? { ...msg, content: msg.content.trim() ? msg.content : "Nao foi possivel obter resposta do modelo agora." }
              : msg
          )
        );
      } else {
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantMessageId && !msg.content.trim()
              ? { ...msg, content: "Resposta interrompida." }
              : msg
          )
        );
      }
    } finally {
      abortControllerRef.current = null;
      setBusy(false);
    }
  };

  return (
    <div className="app-layout">
      <aside className={`sidebar ${sidebarOpen ? "open" : "closed"}`}>
        <div className="sidebar-header">
          <button className="sidebar-new-chat" onClick={handleNewSession} title="Novo Chat">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true">
              <path d="M8 2a.75.75 0 0 1 .75.75v4.5h4.5a.75.75 0 0 1 0 1.5h-4.5v4.5a.75.75 0 0 1-1.5 0v-4.5h-4.5a.75.75 0 0 1 0-1.5h4.5v-4.5A.75.75 0 0 1 8 2z"/>
            </svg>
            Novo Chat
          </button>
        </div>
        <div className="sidebar-list">
          {sessions.length === 0 && (
            <div className="sidebar-empty">Nenhuma sessao ainda</div>
          )}
          {sessions.map((session) => (
            <div
              key={session.id}
              className={`sidebar-item ${currentSessionId === session.id ? "active" : ""}`}
              onClick={() => handleSelectSession(session.id)}
            >
              <span className="sidebar-item-title" title={session.title}>
                {session.title}
              </span>
              <button
                className="sidebar-item-delete"
                onClick={(e) => handleDeleteSession(session.id, e)}
                title="Deletar sessao"
              >
                <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true">
                  <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/>
                  <path fillRule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4L4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/>
                </svg>
              </button>
            </div>
          ))}
        </div>
      </aside>

      <main className="app-shell">
        <header className="app-header">
          <button className="sidebar-toggle" onClick={() => setSidebarOpen(!sidebarOpen)} title="Alternar sidebar">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
              <path fillRule="evenodd" d="M3 5a1 1 0 0 1 1-1h12a1 1 0 1 1 0 2H4a1 1 0 0 1-1-1zm0 5a1 1 0 0 1 1-1h12a1 1 0 1 1 0 2H4a1 1 0 0 1-1-1zm0 5a1 1 0 0 1 1-1h12a1 1 0 1 1 0 2H4a1 1 0 0 1-1-1z" clipRule="evenodd"/>
            </svg>
          </button>
          <div className="brand">ChatLLM Lab</div>
        </header>

        <section className="messages" aria-live="polite" ref={messagesRef}>
          <div className="messages-inner">
            {messages.length === 0 && (
              <article className="bubble assistant">
                <MessageContent content="Bem-vindo ao ChatLLM Lab. Como posso ajudar voce hoje?" />
              </article>
            )}
            {messages.map((msg) => (
              <article key={msg.id || msg.created_at} className={`bubble ${msg.role}`}>
                <MessageContent content={msg.content} />
              </article>
            ))}
          </div>
        </section>

        <Composer
          text={text}
          busy={busy}
          error={error}
          onChangeText={setText}
          onSubmit={onSubmit}
          onStop={onStop}
        />

        <div className="warning-banner">Lembre-se, voce precisa focar no experimento!!!</div>
      </main>
    </div>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);

