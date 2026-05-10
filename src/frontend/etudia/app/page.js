// This file was partially generated with the help of an AI assistant.
"use client";

import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";

export default function Chat() {
  const [input, setInput] = useState("");
  const [isRequesting, setIsRequesting] = useState(false);
  const [messages, setMessages] = useState([]);
  const [pendingSeconds, setPendingSeconds] = useState(0);
  const [lastDuration, setLastDuration] = useState(null);
  const bottomRef = useRef(null);
  const timerRef = useRef(null);
  const startRef = useRef(null);
  const textareaRef = useRef(null);

  // Auto-scroll dès que messages change
  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: "smooth" });
    }
  });

  useEffect(() => {
    if (!isRequesting) return;
    setPendingSeconds(0);
    startRef.current = Date.now();
    timerRef.current = window.setInterval(() => {
      setPendingSeconds(Math.max(0, Math.floor((Date.now() - startRef.current) / 1000)));
    }, 1000);
    return () => window.clearInterval(timerRef.current);
  }, [isRequesting]);

  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 180)}px`;
  }, [input]);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!input.trim()) return;

    const t0 = Date.now();
    const messageId = t0.toString();
    const userMessage = {
      id: `${messageId}-user`,
      role: "user",
      content: input,
    };

    const assistantId = `${messageId}-assistant`;

    // Ajout immédiat du message user + placeholder assistant
    setMessages((prev) => [
      ...prev,
      userMessage,
      { id: assistantId, role: "assistant", content: "" },
    ]);

    const historyToSend = [...messages, userMessage];
    setInput("");

    try {
      setIsRequesting(true);

      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: historyToSend,
        }),
      });

      if (!res.ok || !res.body) {
        console.error("Erreur /api/chat :", await res.text());
        setIsRequesting(false);
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId
              ? {
                  ...m,
                  content:
                    "Je n'ai pas pu générer la réponse (erreur côté serveur).",
                }
              : m,
          ),
        );
        return;
      }

      // Lecture du flux texte en streaming
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let done = false;

      // Dès qu'on commence à recevoir du texte, on considère que
      // la requête backend est “répondue”
      setIsRequesting(false);

      while (!done) {
        const { value, done: doneReading } = await reader.read();
        done = doneReading;
        if (value) {
          const chunk = decoder.decode(value);

          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId ? { ...m, content: m.content + chunk } : m,
            ),
          );
        }
      }
      const elapsed = (Date.now() - t0) / 1000;
      setLastDuration(elapsed);
    } catch (err) {
      console.error("Erreur réseau /api/chat :", err);
      setIsRequesting(false);
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantId
            ? {
                ...m,
                content: "Je n'ai pas pu générer la réponse (erreur réseau).",
              }
            : m,
        ),
      );
    }
  }

  function handleReset() {
    setMessages([]);
    setInput("");
    setIsRequesting(false);
    setPendingSeconds(0);
    setLastDuration(null);
    window.clearInterval(timerRef.current);
    timerRef.current = null;
  }

  console.log("Messages côté front :", messages);

  return (
    <div className="min-h-screen bg-[#f6f6f6] text-[#161616]">
      <header className="fixed inset-x-0 top-0 z-20 border-b border-[#dddddd] bg-white">
        <div className="mx-auto flex min-h-16 w-full max-w-5xl flex-col justify-center px-4 py-3 sm:px-6">
          <p className="text-lg font-bold leading-6 text-[#000091]">etudIA</p>
          <p className="mt-1 text-xs leading-5 text-[#666666] sm:text-sm">
            Assistant d'orientation basé sur Parcoursup
            pour explorer des formations qui pourraient te correspondre.<br></br>
            Ne remplace ni Parcoursup ni les sources officielles.
          </p>
        </div>
      </header>

      <main className="mx-auto flex min-h-screen w-full max-w-5xl flex-col px-4 pt-24 pb-36 sm:px-6 sm:pb-32">
        <section
          aria-label="Conversation avec etudIA"
          aria-live="polite"
          className="flex flex-1 flex-col gap-4 overflow-y-auto"
        >
          {messages.length === 0 && (
            <div className="mx-auto flex flex-1 items-center justify-center py-12 text-center">
              <p className="max-w-md text-sm leading-6 text-[#666666] sm:text-base">
                Dis-moi ce que tu aimes, tes matières préférées, si tu préfères travailler
                le matin ou l’après-midi, le travail seul·e ou en équipe, tes passions,
                devant un ordinateur ou dehors...
                Je t’aiderai à explorer des pistes d’orientation.
              </p>
            </div>
          )}

          {messages.map((message) => {
            const isUser = message.role === "user";

            return (
              <article
                className={`flex w-full ${isUser ? "justify-end" : "justify-start"}`}
                key={message.id}
              >
                <div
                  className={`max-w-[88%] rounded-sm border px-4 py-3 text-sm leading-6 shadow-sm sm:max-w-[72%] sm:px-5 sm:py-4 sm:text-base ${
                    isUser
                      ? "border-[#000091] bg-[#000091] text-white"
                      : "border-[#dddddd] bg-white text-[#161616]"
                  }`}
                >
                  <p
                    className={`mb-1 text-xs font-semibold uppercase tracking-[0.04em] ${
                      isUser ? "text-[#f5f5ff]" : "text-[#000091]"
                    }`}
                  >
                    {isUser ? "Toi" : "etudIA"}
                  </p>
                  {isUser ? (
                    <div className="whitespace-pre-wrap">
                      {message.content}
                    </div>
                  ) : (
                    <div className="whitespace-pre-wrap">
                      <ReactMarkdown>
                        {message.content ||
                          (isRequesting ? "etudIA prépare une réponse..." : "")}
                      </ReactMarkdown>
                      {lastDuration !== null && !isRequesting && message.content && (
                        <p className="mt-3 text-xs text-[#666666] tabular-nums">Réponse obtenue en {lastDuration.toFixed(1)}s</p>
                      )}
                    </div>
                  )}
                </div>
              </article>
            );
          })}

          <div ref={bottomRef} />
        </section>
      </main>

      <footer className="fixed inset-x-0 bottom-0 z-20 border-t border-[#d9d9d9] bg-white px-4 py-3 shadow-[0_-8px_24px_rgba(0,0,0,0.06)] sm:px-6">
        <div className="mx-auto w-full max-w-5xl">
          {isRequesting && (
            <div className="mb-2 flex items-center gap-2 text-sm text-[#3a3a3a]">
              <span
                aria-hidden="true"
                className="h-4 w-4 animate-spin rounded-full border-2 border-[#000091] border-t-transparent"
              />
              <span>En réflexion...</span>
              <span className="tabular-nums text-[#666666]">{pendingSeconds}s</span>
            </div>
          )}

          <form
            className="grid gap-2 sm:grid-cols-[auto_1fr_auto] sm:items-start"
            onSubmit={handleSubmit}
          >
            <button
              className="min-h-11 rounded-sm border border-[#c9c9d8] bg-white px-4 py-2 text-sm font-semibold text-[#000091] transition hover:bg-[#f6f6ff] focus:outline-none focus:ring-2 focus:ring-[#000091] focus:ring-offset-2 disabled:cursor-not-allowed disabled:text-[#929292]"
              disabled={isRequesting || messages.length === 0}
              onClick={handleReset}
              type="button"
            >
              Nouvelle conversation
            </button>
            <label className="sr-only" htmlFor="orientation-message">
              Message à envoyer à etudIA
            </label>
            <textarea
              ref={textareaRef}
              className="min-h-11 w-full rounded-sm border border-[#bcbcbc] bg-white px-3 py-2 text-base text-[#161616] outline-none placeholder:text-[#777777] focus:border-[#000091] focus:ring-2 focus:ring-[#000091]/20"
              id="orientation-message"
              onChange={(e) => setInput(e.currentTarget.value)}
              onInput={(e) => {
                const el = e.currentTarget;
                el.style.height = "auto";
                el.style.height = `${Math.min(el.scrollHeight, 180)}px`;
              }}
              placeholder="Pose ta question d'orientation..."
              rows={1}
              value={input}
            />
            <button
              className="min-h-11 rounded-sm bg-[#000091] px-5 py-2 text-base font-semibold text-white transition hover:bg-[#1212ff] focus:outline-none focus:ring-2 focus:ring-[#000091] focus:ring-offset-2 disabled:cursor-not-allowed disabled:bg-[#eeeeee] disabled:text-[#929292]"
              disabled={isRequesting || !input.trim()}
              type="submit"
            >
              Envoyer
            </button>
          </form>
        </div>
      </footer>
    </div>
  );
}
