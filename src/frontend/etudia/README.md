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

## Déploiement en production

Le frontend est déployé sur Vercel.

- Domaine de production : `https://etudia-pearl.vercel.app`
- Branche déployée : `main`
- Framework preset : Next.js (App Router)
- Root directory : `src/frontend/etudia`

La route `/api/chat` utilise la variable d’environnement **ORIENTATION_API_URL** pour appeler le backend FastAPI (Render).  
En production, ORIENTATION_API_URL pointe vers l’URL publique du backend, par exemple :

- `https://etudia-backend.onrender.com`

### Variables d’environnement (frontend)

| Nom                  | Utilisation                                   | Exemple local                        |
|----------------------|-----------------------------------------------|--------------------------------------|
| `ORIENTATION_API_URL` | URL du backend FastAPI `/chat-orientation`   | `http://127.0.0.1:8000`              |

En local, créer un fichier `.env.local` dans `src/frontend/etudia` :

```bash
ORIENTATION_API_URL=http://127.0.0.1:8000
```

Sur Vercel, la même variable est définie dans **Settings → Environment Variables** (environnement Production) avec l’URL Render.

## Interface de chat

La page principale `app/page.js` affiche une interface de chat simple (messages **User** / **AI**) qui :

- conserve l’historique des échanges côté frontend,
- envoie le dernier message de l’utilisateur à la route Next `/api/chat`,
- affiche la réponse de l’IA en streaming texte (le message AI se remplit progressivement),
- fait un auto‑scroll automatique vers le bas à chaque nouveau message,
- montre une barre de chargement au‑dessus du champ de saisie pendant que la requête est envoyée et traitée par le backend (profil structuré + RAG + LLM).

L’historique complet reste côté front, mais seul le dernier message utilisateur est utilisé pour interroger l’API d’orientation.

## Endpoint `/api/chat`

Le backend Next.js expose une route API :

- **URL** : `POST /api/chat`
- **Entrée** : historique des messages du chat (utilisateur + assistant), sous forme d’un tableau JSON.
- **Comportement** :
  - récupère le dernier message de l’utilisateur (texte libre),
  - appelle le backend FastAPI `POST /chat-orientation` avec ce message,
  - reçoit une réponse textuelle unique (`answer`) produite par la chaîne backend (profil structuré, moteur de recommandations RAG, LLM conseiller),
  - renvoie cette réponse sous forme de flux texte (streaming) au frontend.
- **Sortie** : un flux `text/plain` qui est assemblé côté front pour créer un message AI.

- La route Next `/api/chat` relaie les requêtes vers le backend FastAPI sur l’URL définie par ORIENTATION_API_URL (par exemple http://127.0.0.1:8000 en local, URL publique en prod).
- Cela permet de changer d’environnement (local / déploiement) sans modifier le code, uniquement via les variables d’environnement.

## Chat d’orientation (cadrage éthique)

Côté backend Python, l’API `/chat-orientation` :

- infère un profil structuré de lycéen (StudentProfile) à partir du message,
- interroge un moteur RAG basé sur pgvector pour récupérer des formations pertinentes avec une explication,
- appelle un LLM (`gpt-4o-mini`) avec un prompt système qui cadre le modèle :
  - rôle : assistant d’orientation pour lycéens,
  - réponses limitées au cadre orientation / formations (type Parcoursup),
  - refus des questions hors sujet (actualités sportives, people, etc.),
  - neutralité : ne pas inférer l’origine, le genre, la personnalité ou le niveau social à partir du prénom, du style ou des fautes.
- limite la longueur des réponses pour garder un coût maîtrisé.

Les prompts ne contiennent aucune information identifiante (pas de nom, mail, etc.) afin de limiter les risques de confidentialité.

## À venir

Les prochaines évolutions prévues côté frontend sont :

- mieux mettre en forme les justifications de recommandations (explications par formation),
- consommer de façon plus structurée les métadonnées renvoyées par le backend (type de formation, ville, budget, apprentissage),
- préparer l’intégration avec un déploiement sur Vercel.