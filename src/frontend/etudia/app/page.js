"use client";

import { useState } from "react";

export default function Chat() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = {
      id: Date.now().toString() + "-user",
      role: "user",
      content: input,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: [...messages, userMessage],
        }),
      });

      if (!res.ok) {
        console.error("Erreur /api/chat :", await res.text());
        return;
      }

      const data = await res.json(); // { id, role, content }
      setMessages((prev) => [...prev, data]);
    } catch (err) {
      console.error("Erreur réseau /api/chat :", err);
    }
  }

  console.log("Messages côté front :", messages);
  return (
    <div className="flex flex-col w-full max-w-md py-24 mx-auto stretch">
      {messages.map((message) => (
        <div key={message.id} className="whitespace-pre-wrap">
          {message.role === "user" ? "User: " : "AI: "}
          <div>{message.content}</div>
        </div>
      ))}

      <form onSubmit={handleSubmit}>
        <input
          className="fixed dark:bg-zinc-900 bottom-0 w-full max-w-md p-2 mb-8 border border-zinc-300 dark:border-zinc-800 rounded shadow-xl"
          value={input}
          placeholder="Say something..."
          onChange={(e) => setInput(e.currentTarget.value)}
        />
      </form>
    </div>
  );
}
