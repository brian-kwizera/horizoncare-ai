import { useEffect, useRef, useState, type FormEvent } from "react";

type Source = {
  title: string;
  publisher: string;
  url: string | null;
  similarity: number;
};

type Evidence = {
  chunk_id: string;
  filename: string;
  content: string;
  similarity: number;
};

type AskResponse = {
  question: string;
  answer: string;
  sources: Source[];
  evidence: Evidence[];
};

type ChatTurn = {
  id: number;
  question: string;
  response?: AskResponse;
  error?: string;
  isLoading: boolean;
};

const suggestedQuestions = [
  "What are the common symptoms of malaria?",
  "What are the warning signs of severe dengue?",
  "How is malaria diagnosed?",
];

function HeartEkgLogo() {
  return (
    <svg
      className="heart-ekg-logo"
      viewBox="0 0 48 48"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
      focusable="false"
    >
      <path
        d="M24 41.2 9.2 27.3C2.8 21.3 4.1 11.6 11.3 8.4c4.6-2.1 9.4-.2 12.7 4.1 3.3-4.3 8.1-6.2 12.7-4.1 7.2 3.2 8.5 12.9 2.1 18.9L24 41.2Z"
        fill="#ffffff"
      />
      <path
        d="M9.5 23.8h7.2l3.5-6.2 5.1 13 5.1-10 2.6 3.2h5.5"
        fill="none"
        stroke="#237873"
        strokeWidth="2.7"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function App() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<ChatTurn[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [theme, setTheme] = useState<"light" | "dark">(() => {
    try {
      return localStorage.getItem("horizoncare-theme") === "dark"
        ? "dark"
        : "light";
    } catch {
      return "light";
    }
  });

  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "end",
    });
  }, [messages]);

  useEffect(() => {
  try {
    localStorage.setItem("horizoncare-theme", theme);
  } catch {
    // The selected theme still works if storage is unavailable.
  }
}, [theme]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const trimmedQuestion = question.trim();

    if (!trimmedQuestion || isLoading) return;

    const turnId = Date.now();

    setQuestion("");
    setIsLoading(true);

    setMessages((previous) => [
      ...previous,
      {
        id: turnId,
        question: trimmedQuestion,
        isLoading: true,
      },
    ]);

    try {
      const result = await fetch("/api/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: trimmedQuestion,
        }),
      });

      const data = await result.json();

      if (!result.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : "The request failed. Please try again.",
        );
      }

      setMessages((previous) =>
        previous.map((message) =>
          message.id === turnId
            ? {
                ...message,
                response: data as AskResponse,
                isLoading: false,
              }
            : message,
        ),
      );
    } catch (err) {
      const message =
        err instanceof Error
          ? err.message
          : "Unable to contact HorizonCare. Check that the backend is running.";

      setMessages((previous) =>
        previous.map((turn) =>
          turn.id === turnId
            ? {
                ...turn,
                error: message,
                isLoading: false,
              }
            : turn,
        ),
      );
    } finally {
      setIsLoading(false);
    }
  }

  function startNewQuestion() {
    setMessages([]);
    setQuestion("");
  }

  return (
    <div className={`app-shell ${theme === "dark" ? "dark-mode" : ""}`}>
      <aside className="sidebar">
        <button className="brand" onClick={startNewQuestion}>
          <span className="brand-mark">
            <HeartEkgLogo />
          </span>
          <span>
            <strong className="brand-name">HorizonCare</strong>
            <small className="brand-subtitle">AI HEALTH ASSISTANT</small>
          </span>
        </button>

        <button
          className="new-question"
          onClick={startNewQuestion}
        >
          <span aria-hidden="true">＋</span>
          New question
        </button>

        <p className="sidebar-label">YOUR WORKSPACE</p>

        <div className="sidebar-item">
          <span aria-hidden="true">◉</span>
          Ask HorizonCare
        </div>

        <div className="sidebar-bottom">
          <span className="status-dot" />
          <div>
            <strong>Prototype mode</strong>
            <p>
              Evidence retrieval is connected. AI-generated summaries
              are not yet enabled.
            </p>
          </div>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div className="breadcrumbs">
            <span>Workspace</span>
            <span aria-hidden="true">/</span>
            <strong>Ask HorizonCare</strong>
          </div>

          <div className="topbar-actions">
  <button
    type="button"
    className="theme-toggle"
    onClick={() =>
      setTheme((current) => (current === "light" ? "dark" : "light"))
    }
    aria-label={
      theme === "light"
        ? "Switch to dark mode"
        : "Switch to light mode"
    }
    aria-pressed={theme === "dark"}
  >
    <span aria-hidden="true">
      {theme === "light" ? "☾" : "☀"}
    </span>
    {theme === "light" ? "Dark mode" : "Light mode"}
  </button>

  <span className="environment-badge">
    <span className="status-dot" />
    Connected prototype
  </span>
</div>
        </header>

        <section
          className={`content-area ${
            messages.length > 0 ? "chat-active" : ""
          }`}
        >
          {messages.length === 0 && (
            <div className="welcome">
              <div className="welcome-icon" aria-hidden="true">
                ✳
              </div>

              <p className="eyebrow">
                HEALTH INFORMATION, MADE CLEARER
              </p>

              <h1>
                Understand health.
                <br />
                <span>Explore the evidence.</span>
              </h1>

              <p className="welcome-description">
                Ask a healthcare question and explore information
                supported by traceable medical sources.
              </p>
            </div>
          )}

          {messages.length > 0 && (
            <div className="chat-transcript" role="log" aria-live="polite">
              {messages.map((turn) => {
                const response = turn.response;
                const isMockMode =
                  response?.answer.startsWith("Mock mode is enabled");

                return (
                  <article className="chat-turn" key={turn.id}>
                    <div className="user-message-row">
                      <div className="user-message-bubble">
                        {turn.question}
                      </div>
                    </div>

                    <div className="assistant-message-row">
                      <div className="assistant-avatar" aria-hidden="true">
                        <HeartEkgLogo />
                      </div>

                      <div className="assistant-message-content">
                        <div className="assistant-message-heading">
                          <strong>HorizonCare</strong>
                          <span>Healthcare knowledge assistant</span>
                        </div>

                        {turn.isLoading && (
                          <div className="loading-card">
                            <span className="loading-indicator" />
                            Searching the knowledge base…
                          </div>
                        )}

                        {turn.error && (
                          <div className="error-notice" role="alert">
                            <h2>We couldn't complete your request</h2>
                            <p>{turn.error}</p>
                            <p>
                              Check that the backend is running, then
                              submit your question again.
                            </p>
                          </div>
                        )}

                        {response && (
                          <>
                            {isMockMode && (
                              <div className="mode-notice">
                                <span className="status-dot" />
                                <span>
                                  <strong>Mock mode</strong> — retrieved
                                  evidence is real, but no AI-generated
                                  summary was produced.
                                </span>
                              </div>
                            )}

                            <div className="answer-card">
                              <p className="response-label">
                                HORIZONCARE RESPONSE
                              </p>
                              <h2>Answer</h2>
                              <p className="answer-text">
                                {response.answer}
                              </p>
                            </div>

                            <section className="sources-section">
                              <div className="response-section-heading">
                                <h2>Sources</h2>
                                <span>
                                  {response.sources.length} found
                                </span>
                              </div>

                              {response.sources.length === 0 ? (
                                <p className="empty-state">
                                  No sufficiently relevant sources were
                                  found.
                                </p>
                              ) : (
                                <div className="source-list">
                                  {response.sources.map((source, index) => (
                                    <article
                                      className="source-card"
                                      key={`${source.url ?? source.title}-${index}`}
                                    >
                                      <div
                                        className="source-icon"
                                        aria-hidden="true"
                                      >
                                        ↗
                                      </div>

                                      <div className="source-details">
                                        <h3>{source.title}</h3>
                                        <p>{source.publisher}</p>

                                        <span className="similarity-label">
                                          Retrieval similarity:{" "}
                                          {source.similarity.toFixed(4)}
                                        </span>

                                        {source.url ? (
                                          <a
                                            href={source.url}
                                            target="_blank"
                                            rel="noreferrer"
                                          >
                                            Open original source
                                          </a>
                                        ) : (
                                          <span className="missing-url">
                                            Original source URL unavailable
                                          </span>
                                        )}
                                      </div>
                                    </article>
                                  ))}
                                </div>
                              )}
                            </section>

                            <section className="evidence-section">
                              <div className="response-section-heading">
                                <h2>Supporting evidence</h2>
                                <span>
                                  {response.evidence.length} passages
                                </span>
                              </div>

                              {response.evidence.length === 0 ? (
                                <p className="empty-state">
                                  No supporting passages were retrieved.
                                </p>
                              ) : (
                                <div className="evidence-list">
                                  {response.evidence.map((passage) => (
                                    <details
                                      className="evidence-card"
                                      key={passage.chunk_id}
                                    >
                                      <summary>
                                        <span className="evidence-title">
                                          {passage.chunk_id}
                                        </span>

                                        <span className="evidence-score">
                                          Similarity:{" "}
                                          {passage.similarity.toFixed(4)}
                                        </span>
                                      </summary>

                                      <p className="evidence-content">
                                        {passage.content}
                                      </p>
                                    </details>
                                  ))}
                                </div>
                              )}
                            </section>

                            <p className="medical-disclaimer">
                              Educational prototype only. Retrieved
                              information is not a substitute for
                              professional medical assessment.
                            </p>
                          </>
                        )}
                      </div>
                    </div>
                  </article>
                );
              })}

              <div ref={bottomRef} className="chat-bottom-anchor" />
            </div>
          )}

          {messages.length === 0 && (
            <section className="suggestions">
              <div className="section-heading">
                <h2>Try asking</h2>
                <span>EXAMPLE QUESTIONS</span>
              </div>

              <div className="suggestion-list">
                {suggestedQuestions.map((suggestion) => (
                  <button
                    key={suggestion}
                    type="button"
                    className="suggestion-button"
                    onClick={() => setQuestion(suggestion)}
                  >
                    <span>{suggestion}</span>
                    <span aria-hidden="true">↗</span>
                  </button>
                ))}
              </div>
            </section>
          )}

          <form
            className="question-form chat-composer"
              
            onSubmit={handleSubmit}
          >
            <label htmlFor="health-question">
              What would you like to understand?
            </label>

            <textarea
              id="health-question"
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              placeholder="Ask about a disease, symptoms, or health topic…"
              rows={1}
              disabled={isLoading}
            />

            <div className="form-footer">
              <span className="input-hint">
                {isLoading
                  ? "Searching the knowledge base…"
                  : "Check the supporting sources for context."}
              </span>

              <button
                type="submit"
                className="submit-button"
                disabled={!question.trim() || isLoading}
              >
                {isLoading ? "Searching…" : "Send question"}
                {!isLoading && <span aria-hidden="true">↑</span>}
              </button>
            </div>
          </form>

          <footer className="content-footer">
            <span>HorizonCare AI</span>
            <span>Educational prototype · Evidence-first design</span>
          </footer>
        </section>
      </main>
    </div>
  );
}

export default App;