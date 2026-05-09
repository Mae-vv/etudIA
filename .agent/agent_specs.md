# etudIA – Chat UI spec (DSFR-inspired conversational agent)

## 1. Project context

- Name: **etudIA**
- Goal: conversational assistant to help French high‑school students explore study options.
- Frontend:
  - Next.js **App Router**, located in `src/frontend/etudia/`.
  - Main chat page: `src/frontend/etudia/app/page.js`.
- Backend:
  - FastAPI on Render, exposed via a Next.js API route `/api/chat`.
  - Chat logic (state, `/api/chat` call, streaming, errors, auto‑scroll) is already implemented and must keep working.

This spec explains **how the chat UI should look and behave**.  
It is the single source of truth for any AI assistant editing the frontend.

---

## 2. Desired UI: real chat, no “report”

The page must look like a **conversational agent**, not like a report or long introduction.

- No big “Bonjour, je suis…” intro block.
- No long paragraphs at the top of the page.
- The main content is the **chat conversation** (message list), plus a fixed footer with the composer.

High-level layout:

- Top: simple header bar with product identity.
- Center: scrollable chat area with messages.
- Bottom: fixed composer bar with input and buttons.

---

## 3. Visual style (DSFR inspiration)

Use the **DSFR design system** as visual inspiration for colours, typography and components:

- DSFR docs:  
  - https://www.systeme-de-design.gouv.fr/version-courante/fr
- React DSFR:  
  - https://github.com/codegouvfr/react-dsfr

Rules:

- You MAY import and use `@codegouvfr/react-dsfr` components if it stays reasonable (headers, buttons, inputs).  
- If you do not import the library, mimic DSFR tokens:
  - primary blue around `#000091`,
  - neutral greys for borders/backgrounds,
  - clear focus rings and hover states,
  - readable typography (no huge hero titles).

---

## 4. Layout and behaviour

### 4.1 Header

- Simple, slim bar at the top of the page.
- Contains:
  - Left: “etudIA” as the product name.
  - Below or next to it: short tagline, e.g.  
    “Assistant d’orientation pour explorer des pistes, sans remplacer Parcoursup ni les sources officielles.”
- No big hero section, no long introduction, no secondary navigation.

### 4.2 Chat area (center)

This is the **main area** of the page.

- Fills the available space between the header and the fixed footer.
- Scrollable column of messages.
- Messages are shown as chat bubbles:
  - user messages aligned to the **right**,
  - assistant messages aligned to the **left**.
- Each bubble:
  - has spacing and borders inspired by DSFR,
  - can use subtle colour differences (e.g. user bubble in DSFR blue, assistant bubble in neutral white with border).

Empty state (no messages yet):

- Show a small, concise text (one or two short sentences) in the chat area:
  - e.g. “Pose ta question d’orientation pour commencer la conversation.”
- Do **not** show a big block of introduction text.

### 4.3 Fixed footer (composer)

The composer bar must be **fixed at the bottom** of the viewport.

- Position: `position: fixed; inset-x: 0; bottom: 0;`.
- Full width of the viewport.
- Contains, inside a centered container:

  - Left: **“Nouvelle conversation”** DSFR‑like button.  
    - Behaviour: clears the `messages` state and resets the input (starts a blank conversation).
  - Center: text input field for the user’s message.
  - Right: primary DSFR‑style button “Envoyer”.

Behaviour:

- When `isRequesting === true`:
  - show a small loading indicator (spinner or DSFR “loading” style) with text like  
    “etudIA prépare une réponse…” in or above the footer,
  - disable the “Envoyer” button.
- The footer must stay visible on mobile and desktop; only the chat area scrolls.

---

## 5. Logic that MUST stay the same

The AI must **not** change the existing chat logic, only the UI.

Preserve exactly:

- State:
  - `messages`, `input`, `isRequesting`, `bottomRef` (or equivalent).
- `handleSubmit` behaviour:
  - prevents default submit,
  - ignores empty input,
  - appends a user message and a placeholder assistant message,
  - calls `/api/chat` with a `messages` history,
  - updates the assistant message progressively as chunks arrive.
- Streaming:
  - uses `ReadableStream` + `TextDecoder` to append chunks to the assistant message.
- Auto‑scroll:
  - when new messages arrive, scroll to the bottom using `bottomRef`.
- Error handling:
  - on server error: message like “Je n'ai pas pu générer la réponse (erreur côté serveur).”
  - on network error: message like “Je n'ai pas pu générer la réponse (erreur réseau).”

No change to:

- `/api/chat` route path,
- request / response format,
- backend behaviour,
- environment variables.

---

## 6. Files and dependencies

- Default scope: only modify `src/frontend/etudia/app/page.js`.
- You MAY import DSFR components from `@codegouvfr/react-dsfr` **if**:
  - you also add the necessary imports and respect the existing project structure.
- Do not add unrelated libraries.

If additional files (styles, layout components) must be touched, this must be clearly explained and kept minimal.

---

## 7. Output requirements for the AI assistant

When generating code based on this spec, the AI must:

1. Only touch the files mentioned by the human developer (by default `app/page.js`).
2. Output the **full content** of each modified file in separate code blocks (no partial diffs).
3. Add this comment at the top of any modified file:

   ```js
   // This file was partially generated with the help of an AI assistant.
   ```

4. If any part of the spec is unclear (colours, component choice, DSFR usage), either:
   - make a conservative choice and mention it in a short comment, or
   - ask the human developer for clarification before making large structural changes.

---

## 8. AI assistance disclosure

- etudIA’s chat UI may be partially designed and implemented with the help of an AI assistant (ChatGPT or similar).
- The human developer remains responsible for reviewing and maintaining the code, and for ensuring that the UI is accessible, usable, and aligned with the project’s objectives.