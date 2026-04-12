// app/api/chat/route.js
import { NextResponse } from "next/server";

export const maxDuration = 30;

export async function POST(req) {
  const body = await req.json();

  // useChat envoie soit un tableau, soit un objet { messages }
  const messages = Array.isArray(body) ? body : body.messages ?? [];
  console.log("Messages bruts côté API :", JSON.stringify(messages, null, 2));

  // On garde au plus les 4 derniers échanges
  const MAX_HISTORY = 4;
  const recentMessages =
    messages.length > MAX_HISTORY ? messages.slice(-MAX_HISTORY) : messages;

  // Dernier message utilisateur
  const lastUserMessage = [...recentMessages].reverse().find(
    (m) => m.role === "user",
  );

  // Selon ta version de useChat, soit m.content, soit m.parts[*].text
  const userText =
    lastUserMessage?.content ??
    (lastUserMessage?.parts
      ?.filter((p) => p.type === "text")
      .map((p) => p.text)
      .join(" ") ?? "");

  console.log("Dernier message utilisateur (texte) :", userText);

  if (!userText) {
    return NextResponse.json(
      { error: "Aucun message utilisateur reçu." },
      { status: 400 },
    );
  }

  // Appel à ton backend FastAPI : message -> answer
  const ragResponse = await fetch("http://127.0.0.1:8000/chat-orientation", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: userText }),
  });

  if (!ragResponse.ok) {
    console.error(
      "Erreur backend /chat-orientation :",
      ragResponse.status,
      await ragResponse.text(),
    );
    return NextResponse.json(
      { error: "Erreur backend d'orientation." },
      { status: 500 },
    );
  }

  const data = await ragResponse.json();
  console.log("Réponse backend /chat-orientation :", data);

  // Répondre dans un format simple (un message assistant)
  const message = {
    id: Date.now().toString(),
    role: "assistant",
    content: data.answer,
  };

  // 👉 au lieu de { messages: [message] }
  return NextResponse.json(message);
}