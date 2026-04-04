import { openai } from '@ai-sdk/openai';
import { generateText, convertToModelMessages } from 'ai';

export const maxDuration = 30;

export async function POST(req) {
  const body = await req.json();
  const messages = Array.isArray(body) ? body : body.messages ?? [];

  // Limit context window to recent turns before model conversion.
  const MAX_HISTORY = 4;
  const recentMessages =
    messages.length > MAX_HISTORY ? messages.slice(-MAX_HISTORY) : messages;

  try {
    const result = streamText({
      model: openai('gpt-4o-mini'),
      system:
        "Tu es un assistant d'orientation pour lycéens. " +
        "Tu t'appuies sur une base de données de formations (type Parcoursup). " +
        "Tu ne réponds pas aux questions qui sortent de ce cadre (par exemple actualité sportive, people, etc.). " +
        "Tu ignores le prénom et toute information identifiante de l'utilisateur : " +
        "tu ne tires aucune conclusion sur son niveau, son origine, son genre ou sa personnalité à partir de son prénom, de ses fautes ou de son style. " +
        "Tu dois rester neutre, explicite sur tes limites et éviter tout biais. " +
        "Si une question sort du cadre orientation/formation, tu expliques calmement que ce n'est pas ton rôle.",
      messages: convertToModelMessages(recentMessages),
      maxOutputTokens: 300,
    });

    return result.toUIMessageStreamResponse();
  } catch (err) {
    console.error('Erreur OpenAI :', err);

    return new Response(
      JSON.stringify({
        error:
          "Je ne peux pas appeler le modèle de langage pour le moment (quota ou erreur). Tu peux réessayer plus tard.",
      }),
      {
        status: 500,
        headers: { 'Content-Type': 'application/json' },
      }
    );
  }
}