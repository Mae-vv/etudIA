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
  const lastUserMessage = [...messages].reverse().find(
    (m) => m.role === "user",
  );

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

  const backendBaseUrl = process.env.ORIENTATION_API_URL;

  // Appel à ton backend FastAPI : message -> answer
  const ragResponse = await fetch(`${backendBaseUrl}/chat-orientation`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message: userText,
      history: recentMessages,
    }),
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


  const fullText = data.answer ?? "";

  // Streaming artificiel de fullText
  const encoder = new TextEncoder();

  const stream = new ReadableStream({
    start(controller) {
      const chunkSize = 20; // nb de caractères par "tick"
      let index = 0;

      function push() {
        if (index >= fullText.length) {
          controller.close();
          return;
        }
        const slice = fullText.slice(index, index + chunkSize);
        index += chunkSize;
        controller.enqueue(encoder.encode(slice));
        // petit délai pour l'effet "chat"
        setTimeout(push, 20);
      }

      push();
    },
  });

  return new Response(stream, {
    status: 200,
    headers: {
      "Content-Type": "text/plain; charset=utf-8",
    },
  });
}
  // Répondre dans un format simple (un message assistant)
//   const message = {
//     id: Date.now().toString(),
//     role: "assistant",
//     content: data.answer,
//   };

//   return NextResponse.json(message);
// }