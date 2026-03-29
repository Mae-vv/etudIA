import { openai } from '@ai-sdk/openai';
import { streamText, UIMessage, convertToModelMessages } from 'ai';

// Allow streaming responses up to 30 seconds
export const maxDuration = 30;

export async function POST(req) {
  const { messages } = await req.json();

  // 1. Dernier message utilisateur (pour le RAG)
  const lastUserMessage = [...messages].reverse().find(
    (m) => m.role === 'user'
  );

  const lastUserText =
    lastUserMessage?.parts
      ?.filter((p) => p.type === 'text')
      .map((p) => p.text)
      .join(' ') ?? '';

  console.log('Dernier message utilisateur (texte) :', lastUserText);

  if (!lastUserMessage) {
    console.log("Pas de message utilisateur pour l'instant.");
  }

  const result = streamText({
    model: openai('gpt-4o'),
    system:
      "Tu es un assistant d'orientation pour lycéens. " +
      "Tu t'appuies sur une base de données de formations (type Parcoursup). " +
      "Tu ne réponds pas aux questions qui sortent de ce cadre (par exemple actualité sportive, people, etc.). " +
      "Tu ignores le prénom et toute information identifiante de l'utilisateur : " +
      "tu ne tires aucune conclusion sur son niveau, son origine, son genre ou sa personnalité à partir de son prénom, de ses fautes ou de son style. " +
      "Tu dois rester neutre, explicite sur tes limites et éviter tout biais. " +
      "Si une question sort du cadre orientation/formation, tu expliques calmement que ce n'est pas ton rôle.",
    messages: convertToModelMessages(messages),
  });

  return result.toUIMessageStreamResponse();
}