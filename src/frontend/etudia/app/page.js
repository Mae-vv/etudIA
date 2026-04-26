"use client";

import { useEffect, useRef, useState } from "react";

export default function Chat() {
  const [input, setInput] = useState("");
  const [isRequesting, setIsRequesting] = useState(false);
  const [messages, setMessages] = useState([]);
  const bottomRef = useRef(null);

  // Auto-scroll dès que messages change
  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = {
      id: Date.now().toString() + "-user",
      role: "user",
      content: input,
    };

    const assistantId = Date.now().toString() + "-assistant";

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
              m.id === assistantId
                ? { ...m, content: m.content + chunk }
                : m,
            ),
          );
        }
      }
    } catch (err) {
      console.error("Erreur réseau /api/chat :", err);
      setIsRequesting(false);
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantId
            ? {
                ...m,
                content:
                  "Je n'ai pas pu générer la réponse (erreur réseau).",
              }
            : m,
        ),
      );
    }
  }

  console.log("Messages côté front :", messages);

  return (
    <div className="flex flex-col w-full max-w-md py-24 mx-auto stretch">
      {/* Liste des messages */}
      {messages.map((message) => (
        <div key={message.id} className="whitespace-pre-wrap mb-2">
          {message.role === "user" ? "User: " : "AI: "}
          <div>{message.content}</div>
        </div>
      ))}
      <div ref={bottomRef} />

      {/* Zone “footer” avec barre + input */}
      <div className="fixed bottom-0 left-1/2 -translate-x-1/2 w-full max-w-md px-2 pb-2 bg-transparent">
        {isRequesting && (
          <div className="w-full h-2 bg-zinc-200 rounded mb-2 overflow-hidden">
            <div className="h-2 bg-blue-500 animate-pulse w-2/5 rounded" />
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <input
            className="w-full dark:bg-zinc-900 p-2 border border-zinc-300 dark:border-zinc-800 rounded shadow-xl"
            value={input}
            placeholder="Parle-moi de ta situation d’orientation…"
            onChange={(e) => setInput(e.currentTarget.value)}
          />
        </form>
      </div>
    </div>
  );
}