import { openai } from '@ai-sdk/openai';
import { streamText, convertToModelMessages } from 'ai';

export const maxDuration = 30;

export async function POST(req) {
  const body = await req.json();
  const messages = Array.isArray(body) ? body : body.messages ?? [];
  console.log("Messages bruts côté API :", JSON.stringify(messages, null, 2));

  // Limit context window to recent turns before model conversion.
  const MAX_HISTORY = 4;
  const recentMessages =
    messages.length > MAX_HISTORY ? messages.slice(-MAX_HISTORY) : messages;
  
    // Dernier message utilisateur pour le RAG
  const lastUserMessage = [...recentMessages].reverse().find(
    (m) => m.role === 'user'
  );

  const lastUserText =
    lastUserMessage?.parts
      ?.filter((p) => p.type === 'text')
      .map((p) => p.text)
      .join(' ') ?? ''; // useChat v2: content contient déjà le texte

  console.log('Dernier message utilisateur (texte) :', lastUserText);

  // Appel au backend Python RAG
  let recommendations = [];

  if (lastUserText) {
    try {
      const ragResponse = await fetch('http://127.0.0.1:8000/recommendations', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: lastUserText,
          profile: {
            typeformation: 'BUT',
            isapprentissage: true,
            maxfraisscolarite: 2500,
            region: null,
          },
          limit: 5,
        }),
      });

      if (!ragResponse.ok) {
        console.error(
          'Erreur backend RAG:',
          ragResponse.status,
          await ragResponse.text()
        );
      } else {
        const ragData = await ragResponse.json();
        recommendations = ragData.recommendations ?? [];
        console.log('Reco RAG côté API /chat :', recommendations);
      }
    } catch (error) {
      console.error('Erreur de fetch vers le backend RAG:', error);
    }
  }

  // Construire un contexte texte à partir des recos (max 3)
  const ragContext = (recommendations ?? [])
    .slice(0, 3)
    .map((rec, idx) => {
      const ville = rec.commune || '';
      const type = rec.type_formation || '';
      return `${idx + 1}. ${type} – ${ville}\n${rec.chunk_text}`;
    })
    .join('\n\n');

  // 1) Convertir recentMessages (avec parts) en messages { role, content }
  const baseMessages = recentMessages.map((m) => {
    const text =
      m.parts
        ?.filter((p) => p.type === 'text')
        .map((p) => p.text)
        .join(' ') ?? '';

    return {
      role: m.role,
      content: text,
    };
  });

  // 2) Ajouter un message system avec le contexte RAG si dispo
  const messagesWithRag = [...baseMessages];

  if (ragContext) {
    messagesWithRag.push({
      role: 'system',
      content:
        "Voici des formations issues d'un moteur de recommandation RAG basé sur Parcoursup. " +
        "Tu dois t'appuyer uniquement sur ces formations pour ta réponse, sans en inventer d'autres :\n\n" +
        ragContext,
    });
  }

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
      messages: messagesWithRag,
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