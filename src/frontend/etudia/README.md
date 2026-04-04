# Frontend StudIA – interface de chat

Ce projet est une application Next.js (App Router) qui fournit une interface de chat pour StudIA, l’assistant d’orientation destiné aux lycéens avant Parcoursup.

## Démarrer le frontend en local

Depuis le dossier `frontend/etudIA` :

```bash
npm run dev
# ou
yarn dev
# ou
pnpm dev
# ou
bun dev
```

L’application est accessible sur [http://localhost:3000](http://localhost:3000).

La page principale `app/page.js` affiche une interface de chat basée sur le hook `useChat` de `@ai-sdk/react` :
- les messages de l’utilisateur sont envoyés à l’endpoint Next.js `/api/chat`,
- la page se met à jour automatiquement quand le code est modifié.

## Endpoint `/api/chat`

Le backend Next.js expose une route API :

- **URL** : `POST /api/chat`
- **Entrée** : historique des messages du chat (utilisateur + assistant), fourni automatiquement par `useChat`.
- **Comportement** :
  - récupère le dernier message de l’utilisateur,
  - appelle le modèle OpenAI `gpt-4o` via le SDK `ai`,
  - envoie un message système qui cadre le rôle du modèle :
    - assistant d’orientation pour lycéens,
    - réponses limitées au cadre orientation / formations (type Parcoursup),
    - refus des questions hors sujet (actualités sportives, people, etc.),
    - prise en compte des biais : ignorer prénom, style ou fautes de l’utilisateur pour ne pas inférer son origine, son genre ou son niveau.
- **Sortie** : une réponse générée par le modèle, renvoyée en streaming au hook `useChat`.

Cette couche API sera ensuite enrichie pour intégrer les résultats du moteur de recommandation RAG (backend Python + pgvector) dans le prompt envoyé au modèle.

## Chat d’orientation

Le front Next.js utilise `useChat` (`@ai-sdk/react`) pour appeler l’endpoint `POST /api/chat`.

L’API `/api/chat` :
- lit l’historique des messages et le dernier message utilisateur,
- applique un message système qui cadre le LLM sur l’orientation Parcoursup et limite les sujets hors périmètre,
- appelle le modèle OpenAI `gpt-4o-mini` via l’AI SDK,
- limite la réponse à 300 tokens pour contrôler les coûts,
- renvoie un message JSON `{ role, content }` consommé par le front.

Les prompts ne contiennent aucune information identifiante (pas de nom, mail, etc.) afin de limiter les risques en termes de confidentialité.

## À venir

Les prochaines évolutions prévues côté frontend sont :
- consommer les recommandations renvoyées par le backend Python,
- préparer l’intégration avec un déploiement sur Vercel.