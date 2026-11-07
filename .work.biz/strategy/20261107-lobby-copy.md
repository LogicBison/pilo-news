# Lobby copy deck — `heraldfox.com`

**What it is:** every string the lobby needs, in English and Spanish, as `lobby.*` catalog keys ready for `apps/web/src/messages/{en,es}.json`. Companion to `.work.biz/plans/20261107-plan-heraldfox-lobby.md`.
**Status:** Draft copy 2026-11-07. Not implemented. Two keys are gated: `lobby.offer.brief.*` (needs D-002 delivery) and `lobby.services.content.signature` (needs D-005 reviewer).
**Needs:** D-018 (brand string), D-002 (delivery), D-005 (reviewer). Claims ledger at the end — read it before editing a number.

---

## How to use

- Keys go under a top-level `lobby` namespace. No string is hardcoded in a component; `pnpm check` enforces EN/ES key parity.
- `lobby.brand.name` is the single brand token. Today the catalog says "System News" and the domain says `heraldfox.com` — D-018 picks one. Changing this one key must change the whole lobby.
- Numbers (`{desks}`, `{sources}`) are interpolated from the API, never typed into copy. Interpolation uses the existing `{name}` syntax in `lib/i18n.ts`.
- Register: desk editor, not marketing. No exclamation marks, no "unlock", no "seamless". Spanish uses `usted`, matching the channel catalog.
- es-ES conventions for dates and numbers, as the rest of the catalog does.

---

## English

```json
"lobby": {
  "brand": {
    "name": "Herald Fox",
    "tagline": "Industry desks",
    "deskCount": "{desks} desks"
  },
  "nav": {
    "desks": "Desks",
    "services": "Services",
    "references": "Reference issues",
    "contact": "Contact",
    "cta": "Commission a desk"
  },
  "hero": {
    "eyebrow": "{desks} desks · English and Spanish",
    "title": "Know what changed in your field before it costs you.",
    "lead": "Every desk reads the primary record — regulators, filings, standards bodies, recall notices, trial registries — and publishes only what a professional has to act on. Free to read. No account.",
    "doorReader": "Follow a desk",
    "doorBuyer": "Commission a desk",
    "note": "No account. No paywall. RSS and JSON on every desk."
  },
  "board": {
    "caption": "All {desks} desks, and how each one runs",
    "summary": "Desk, update cadence, languages, and the date of the newest story.",
    "headDesk": "Desk",
    "headUpdates": "Updates",
    "headLanguages": "Languages",
    "headFiled": "Last filed",
    "liveLabel": "updated on a schedule",
    "everyHours": "every {hours} h",
    "empty": "The board is not loading right now. The desks below still work."
  },
  "dir": {
    "eyebrow": "01 — The directory",
    "title": "{desks} desks. Pick yours.",
    "intro": "Every desk is written the same way: primary sources only, a daily or weekly pass, two languages where we have them. Each one carries the same free offers — a brief, a reference issue where we publish one, and a way to reach a specialist.",
    "enter": "Enter the desk",
    "offerBrief": "Brief",
    "offerAsset": "Reference",
    "offerQuestion": "Questions",
    "offerConsultation": "Consultation",
    "emptyTitle": "The directory is unavailable",
    "emptyBody": "The news service is not answering. Try again in a moment.",
    "retry": "Try again"
  },
  "offer": {
    "eyebrow": "02 — What is free",
    "title": "Three ways to use a desk. None of them cost money.",
    "asset": {
      "title": "Reference issues",
      "body": "Dated documents built from the record — the KEV digest, the regulatory calendar. Each one lists its sources and the date it was filed.",
      "cta": "Read the archive",
      "ctaWaitlist": "Join the waitlist"
    },
    "question": {
      "title": "Ask one question",
      "body": "One question per desk, answered in writing. No call, no funnel.",
      "cta": "Ask a desk"
    },
    "specialist": {
      "title": "Talk to a specialist",
      "body": "When the answer needs a person, we route your case to an independent, vetted specialist. No cost, no obligation, and nothing we publish is advice.",
      "cta": "Talk to a specialist"
    }
  },
  "how": {
    "eyebrow": "03 — How a desk is built",
    "title": "Three steps, and a person at the end of the second.",
    "step1Title": "Sourced",
    "step1Body": "Feeds from the bodies that matter in each field — regulators, filings, standards bodies — each one checked by a quality gate before it is allowed in.",
    "step2Title": "Summarized",
    "step2Body": "A model drafts the summary from the source text. A person signs the reference issues before they publish.",
    "step3Title": "Routed",
    "step3Body": "A reader who needs a person reaches an independent specialist. We do not charge the reader and we do not give advice."
  },
  "services": {
    "eyebrow": "04 — For organizations",
    "title": "When the desk has to carry your name.",
    "intro": "The same pipeline that runs the {desks} desks can run one for you, or produce the document your team keeps rebuilding.",
    "introFallback": "The same pipeline that runs the desks can run one for you, or produce the document your team keeps rebuilding.",
    "news": {
      "title": "News service",
      "body": "We run one or more desks for your association, firm, or portfolio.",
      "point1": "Sourced from primary records, on a daily or weekly cadence.",
      "point2": "Published under your brand, in English and Spanish.",
      "point3": "Delivered as a page, an RSS feed, an email, or JSON.",
      "point4": "Every item links to its source, so a reader can check it in one click.",
      "for": "For associations, professional firms, funds, and agencies with an audience and no newsroom."
    },
    "content": {
      "title": "Content generation",
      "body": "We build and maintain the reference document your team keeps rebuilding by hand.",
      "point1": "Regulatory calendars, rule-change logs, recall trackers, queue and trial digests.",
      "point2": "Every row dated, cited, and traceable to a primary record.",
      "signature": "Signed by the reviewer accountable for it.",
      "point4": "Refreshed on the schedule the document needs.",
      "for": "For teams that hand a client a document and get asked to prove it."
    },
    "cta": "Request a scope call"
  },
  "engage": {
    "eyebrow": "05 — How an engagement runs",
    "title": "Scope call, fixed pilot, then the cadence.",
    "step1Title": "Scope call",
    "step1Body": "Thirty minutes. Which desk, which audience, what has to be true for this to work. If we are the wrong fit, we say so on the call.",
    "step2Title": "Fixed pilot",
    "step2Body": "Four weeks, one desk, an agreed cadence, a fixed fee. You see the output before any retainer exists.",
    "step3Title": "Review gate",
    "step3Body": "Nothing publishes under your name until your reviewer or ours signs it.",
    "step4Title": "Publish",
    "step4Body": "Your domain or ours. Page, RSS, email, JSON — whatever your audience already reads."
  },
  "faq": {
    "eyebrow": "06 — Questions",
    "title": "The ones we get on the first call.",
    "q1": "Who writes the desks?",
    "a1": "A pipeline reads the primary sources and drafts. A person signs the reference issues. Every item links to the record it came from.",
    "q2": "Is this AI-generated?",
    "a2": "Summaries are drafted by a model from the source text and published with the source cited. Reference issues are reviewed and signed. We name the model and the reviewer on request.",
    "q3": "Can I read only one industry?",
    "a3": "Yes. Each desk has its own site and feed, and publishes a brief where we have one. None of them require an account.",
    "q4": "Do you publish in Spanish?",
    "a4": "Yes, where the desk has Spanish coverage. Depth varies by desk, and the Spanish side of a new desk is thinner for the first weeks.",
    "q5": "Do you give advice?",
    "a5": "No. We publish news and route you to independent specialists. Nothing on this site is legal, financial, or medical advice.",
    "q6": "Can you run a desk under our brand?",
    "a6": "That is the news service. It starts with a scope call and a four-week pilot.",
    "q7": "What does it cost to read?",
    "a7": "Nothing. No account, no paywall. A feed may carry a small, labelled promotion, usually for one of our own desks or services.",
    "q8": "Can we take the data?",
    "a8": "Every desk publishes RSS 2.0 and a documented JSON API. For commercial use, talk to us."
  },
  "final": {
    "title": "Two ways in.",
    "readerTitle": "I read the news",
    "readerBody": "{desks} fields, free to read, in two languages.",
    "readerCta": "Follow a desk",
    "buyerTitle": "I need the news made",
    "buyerBody": "A news service or a commissioned document. One call to scope it.",
    "buyerCta": "Request a scope call"
  },
  "footer": {
    "blurb": "{brand} runs {desks} industry desks from primary sources, in English and Spanish.",
    "blurbFallback": "Herald Fox runs industry desks from primary sources, in English and Spanish.",
    "desksTitle": "Desks",
    "companyTitle": "Company",
    "followTitle": "Follow",
    "legal": "News, not professional advice. Headlines link to the original publisher."
  },
  "form": {
    "title": "Request a scope call",
    "intro": "Tell us the audience and what has to be true. We reply to the ones we can help with.",
    "name": "Name",
    "email": "Work email",
    "phone": "Phone (optional)",
    "message": "What do you need?",
    "messageHint": "Which service, which industry, how often.",
    "consent": "I agree to be contacted about this request and have read the privacy policy.",
    "consentLink": "Privacy policy",
    "submit": "Send request",
    "sending": "Sending…",
    "success": "Received. We read every message and reply to the ones we can help with.",
    "error": "That did not send. Check the email address and try again.",
    "limited": "Too many messages from this connection. Try again in an hour."
  },
  "spine": {
    "directory": "Directory",
    "offers": "Offers",
    "method": "Method",
    "services": "Services",
    "process": "Process",
    "questions": "Questions"
  },
  "contact": {
    "eyebrow": "07 — Contact",
    "title": "Write to us.",
    "intro": "One message, read by a person. Say which desk, a service, or something else entirely. For a service inquiry the form on the services page asks the better questions.",
    "submit": "Send message"
  },
  "legal": {
    "updated": "Last updated 7 November 2026",
    "privacyTitle": "Privacy",
    "privacyBody": "Herald Fox stores only what it needs to run the desks and answer a service inquiry: feed metadata, headlines and links, aggregated usage counts, and the messages you choose to send. We do not sell personal data. We store a hashed network identifier, a hashed device identifier, campaign parameters, and a coarse country code when the network edge provides one, to prevent abuse and measure aggregate interest; we do not store raw IP addresses. An inquiry is read by us, and is not sold or shared with a partner unless you ask for an introduction.",
    "termsTitle": "Terms",
    "termsBody": "Herald Fox publishes headlines, excerpts, and original summaries with attribution and links to the publisher. Content remains the property of its publisher. Nothing on this site is legal, financial, medical, or professional advice. A service engagement is governed by the scope you sign, not by this page. Automated access must respect the published rate limits."
  },
  "a11y": {
    "skipLink": "Skip to the desks",
    "languageSwitch": "Switch language",
    "plate": "{name} — {tagline} Enter the desk.",
    "boardCaption": "All {desks} desks with update cadence, languages, and the date of the newest story."
  }
}
```

---

## Español

```json
"lobby": {
  "brand": {
    "name": "Herald Fox",
    "tagline": "Mesas sectoriales",
    "deskCount": "{desks} mesas"
  },
  "nav": {
    "desks": "Mesas",
    "services": "Servicios",
    "references": "Ediciones de referencia",
    "contact": "Contacto",
    "cta": "Encargar una mesa"
  },
  "hero": {
    "eyebrow": "{desks} mesas · Inglés y español",
    "title": "Sepa qué cambió en su sector antes de que le cueste.",
    "lead": "Cada mesa lee la fuente primaria —reguladores, expedientes, organismos de normalización, avisos de retiro, registros de ensayos— y publica solo lo que un profesional tiene que atender. Gratis. Sin cuenta.",
    "doorReader": "Seguir una mesa",
    "doorBuyer": "Encargar una mesa",
    "note": "Sin cuenta. Sin muro de pago. RSS y JSON en cada mesa."
  },
  "board": {
    "caption": "Las {desks} mesas y cómo funciona cada una",
    "summary": "Mesa, frecuencia de actualización, idiomas y la fecha de la historia más reciente.",
    "headDesk": "Mesa",
    "headUpdates": "Actualiza",
    "headLanguages": "Idiomas",
    "headFiled": "Último archivo",
    "liveLabel": "actualización programada",
    "everyHours": "cada {hours} h",
    "empty": "El tablero no está cargando. Las mesas de abajo siguen disponibles."
  },
  "dir": {
    "eyebrow": "01 — El directorio",
    "title": "{desks} mesas. Elija la suya.",
    "intro": "Todas las mesas se escriben igual: solo fuentes primarias, una pasada diaria o semanal y dos idiomas donde los tenemos. Cada una ofrece lo mismo, gratis: un resumen semanal, una edición de referencia cuando la publicamos y una vía para llegar a un especialista.",
    "enter": "Entrar a la mesa",
    "offerBrief": "Resumen",
    "offerAsset": "Referencia",
    "offerQuestion": "Preguntas",
    "offerConsultation": "Consulta",
    "emptyTitle": "El directorio no está disponible",
    "emptyBody": "El servicio de noticias no responde. Inténtelo de nuevo en un momento.",
    "retry": "Reintentar"
  },
  "offer": {
    "eyebrow": "02 — Lo que es gratis",
    "title": "Tres formas de usar una mesa. Ninguna cuesta dinero.",
    "asset": {
      "title": "Ediciones de referencia",
      "body": "Documentos fechados y construidos sobre el registro: el digest KEV, el calendario regulatorio. Cada uno enumera sus fuentes y la fecha en que se cerró.",
      "cta": "Ver el archivo",
      "ctaWaitlist": "Unirse a la lista"
    },
    "question": {
      "title": "Una pregunta",
      "body": "Una pregunta por mesa, respondida por escrito. Sin llamada y sin embudo.",
      "cta": "Preguntar a una mesa"
    },
    "specialist": {
      "title": "Hablar con un especialista",
      "body": "Cuando la respuesta necesita a una persona, canalizamos su caso a un especialista independiente y verificado. Sin costo, sin compromiso, y nada de lo que publicamos es asesoría.",
      "cta": "Hablar con un especialista"
    }
  },
  "how": {
    "eyebrow": "03 — Cómo se hace una mesa",
    "title": "Tres pasos, y una persona al final del segundo.",
    "step1Title": "Buscado",
    "step1Body": "Fuentes de los organismos que importan en cada sector —reguladores, expedientes, organismos de normalización—, cada una revisada por un filtro de calidad antes de entrar.",
    "step2Title": "Resumido",
    "step2Body": "Un modelo redacta el resumen a partir del texto de la fuente. Una persona firma las ediciones de referencia antes de publicarlas.",
    "step3Title": "Canalizado",
    "step3Body": "Quien necesita a una persona llega a un especialista independiente. No cobramos al lector y no damos asesoría."
  },
  "services": {
    "eyebrow": "04 — Para organizaciones",
    "title": "Cuando la mesa tiene que llevar su nombre.",
    "intro": "El mismo sistema que sostiene las {desks} mesas puede sostener una para usted, o producir el documento que su equipo rehace una y otra vez.",
    "introFallback": "El mismo sistema que sostiene las mesas puede sostener una para usted, o producir el documento que su equipo rehace una y otra vez.",
    "news": {
      "title": "Servicio de noticias",
      "body": "Operamos una o más mesas para su asociación, despacho o portafolio.",
      "point1": "Con fuentes primarias y una cadencia diaria o semanal.",
      "point2": "Publicado con su marca, en inglés y en español.",
      "point3": "Entregado como página, feed RSS, correo o JSON.",
      "point4": "Cada elemento enlaza a su fuente, para que el lector pueda verificarlo en un clic.",
      "for": "Para asociaciones, despachos profesionales, fondos y agencias con audiencia y sin sala de redacción."
    },
    "content": {
      "title": "Generación de contenidos",
      "body": "Construimos y mantenemos el documento de referencia que su equipo rehace a mano.",
      "point1": "Calendarios regulatorios, registros de cambios de norma, rastreadores de retiros, digests de colas y de ensayos.",
      "point2": "Cada fila fechada, citada y trazable a un registro primario.",
      "signature": "Firmado por el revisor responsable.",
      "point4": "Actualizado con la frecuencia que el documento necesita.",
      "for": "Para equipos que entregan un documento a un cliente y tienen que demostrarlo."
    },
    "cta": "Solicitar una llamada de alcance"
  },
  "engage": {
    "eyebrow": "05 — Cómo corre un encargo",
    "title": "Llamada de alcance, piloto fijo y después la cadencia.",
    "step1Title": "Llamada de alcance",
    "step1Body": "Treinta minutos. Qué mesa, qué audiencia y qué tiene que ser cierto para que esto funcione. Si no somos la opción, se lo decimos en la llamada.",
    "step2Title": "Piloto fijo",
    "step2Body": "Cuatro semanas, una mesa, una cadencia acordada y un precio fijo. Ve el resultado antes de que exista cualquier contrato mensual.",
    "step3Title": "Puerta de revisión",
    "step3Body": "Nada se publica con su nombre hasta que lo firme su revisor o el nuestro.",
    "step4Title": "Publicar",
    "step4Body": "Su dominio o el nuestro. Página, RSS, correo, JSON: lo que su audiencia ya lee."
  },
  "faq": {
    "eyebrow": "06 — Preguntas",
    "title": "Las que salen en la primera llamada.",
    "q1": "¿Quién escribe las mesas?",
    "a1": "Un sistema lee las fuentes primarias y redacta. Una persona firma las ediciones de referencia. Cada elemento enlaza al registro del que salió.",
    "q2": "¿Esto lo genera una IA?",
    "a2": "Los resúmenes los redacta un modelo a partir del texto de la fuente y se publican citando esa fuente. Las ediciones de referencia se revisan y se firman. Damos el nombre del modelo y del revisor cuando se pide.",
    "q3": "¿Puedo leer solo un sector?",
    "a3": "Sí. Cada mesa tiene su propio sitio y su propio feed, y publica un resumen donde lo tenemos. Ninguna pide cuenta.",
    "q4": "¿Publican en español?",
    "a4": "Sí, donde la mesa tiene cobertura en español. La profundidad varía por mesa, y el lado español de una mesa nueva es más delgado las primeras semanas.",
    "q5": "¿Dan asesoría?",
    "a5": "No. Publicamos noticias y canalizamos hacia especialistas independientes. Nada de este sitio es asesoría legal, financiera ni médica.",
    "q6": "¿Pueden operar una mesa con nuestra marca?",
    "a6": "Ese es el servicio de noticias. Empieza con una llamada de alcance y un piloto de cuatro semanas.",
    "q7": "¿Cuánto cuesta leer?",
    "a7": "Nada. Sin cuenta y sin muro de pago. Un feed puede llevar una promoción pequeña e identificada, casi siempre de una de nuestras mesas o servicios.",
    "q8": "¿Podemos tomar los datos?",
    "a8": "Cada mesa publica RSS 2.0 y una API JSON documentada. Para uso comercial, hable con nosotros."
  },
  "final": {
    "title": "Dos puertas.",
    "readerTitle": "Leo las noticias",
    "readerBody": "{desks} sectores, gratis y en dos idiomas.",
    "readerCta": "Seguir una mesa",
    "buyerTitle": "Necesito las noticias hechas",
    "buyerBody": "Un servicio de noticias o un documento por encargo. Una llamada para definir el alcance.",
    "buyerCta": "Solicitar una llamada de alcance"
  },
  "footer": {
    "blurb": "{brand} opera {desks} mesas sectoriales desde fuentes primarias, en inglés y en español.",
    "blurbFallback": "Herald Fox opera mesas sectoriales desde fuentes primarias, en inglés y en español.",
    "desksTitle": "Mesas",
    "companyTitle": "Compañía",
    "followTitle": "Seguir",
    "legal": "Noticias, no asesoría profesional. Los titulares enlazan al medio original."
  },
  "form": {
    "title": "Solicitar una llamada de alcance",
    "intro": "Cuéntenos la audiencia y qué tiene que ser cierto. Respondemos a los mensajes que podemos atender.",
    "name": "Nombre",
    "email": "Correo de trabajo",
    "phone": "Teléfono (opcional)",
    "message": "¿Qué necesita?",
    "messageHint": "Qué servicio, qué sector y con qué frecuencia.",
    "consent": "Acepto que me contacten sobre esta solicitud y he leído la política de privacidad.",
    "consentLink": "Política de privacidad",
    "submit": "Enviar solicitud",
    "sending": "Enviando…",
    "success": "Recibido. Leemos todos los mensajes y respondemos a los que podemos ayudar.",
    "error": "No se pudo enviar. Revise el correo e inténtelo de nuevo.",
    "limited": "Demasiados mensajes desde esta conexión. Inténtelo de nuevo en una hora."
  },
  "spine": {
    "directory": "Directorio",
    "offers": "Ofertas",
    "method": "Método",
    "services": "Servicios",
    "process": "Proceso",
    "questions": "Preguntas"
  },
  "contact": {
    "eyebrow": "07 — Contacto",
    "title": "Escríbanos.",
    "intro": "Un mensaje, leído por una persona. Diga qué mesa, un servicio o cualquier otra cosa. Para una solicitud de servicio, el formulario de la página de servicios hace las preguntas más útiles.",
    "submit": "Enviar mensaje"
  },
  "legal": {
    "updated": "Última actualización: 7 de noviembre de 2026",
    "privacyTitle": "Privacidad",
    "privacyBody": "Herald Fox guarda solo lo necesario para operar las mesas y responder una solicitud de servicio: metadatos de fuentes, titulares y enlaces, conteos de uso agregados y los mensajes que usted decide enviar. No vendemos datos personales. Guardamos un identificador de red con hash, un identificador de dispositivo con hash, parámetros de campaña y un código de país aproximado cuando el borde de la red lo proporciona, para evitar abusos y medir interés agregado; no guardamos direcciones IP sin procesar. Una solicitud la leemos nosotros; no se vende ni se comparte con un socio salvo que usted pida una presentación.",
    "termsTitle": "Términos",
    "termsBody": "Herald Fox publica titulares, extractos y resúmenes originales con atribución y enlaces al medio. El contenido sigue siendo propiedad de su editor. Nada de este sitio es asesoría legal, financiera, médica ni profesional. Un encargo de servicio se rige por el alcance que usted firma, no por esta página. El acceso automatizado debe respetar los límites de uso publicados."
  },
  "a11y": {
    "skipLink": "Saltar a las mesas",
    "languageSwitch": "Cambiar idioma",
    "plate": "{name} — {tagline} Entrar a la mesa.",
    "boardCaption": "Las {desks} mesas con su frecuencia de actualización, idiomas y la fecha de la historia más reciente."
  }
}
```

---

## Held until D-002 lands

The weekly brief card is written and dropped from the grid, not forgotten. D-017
(approved 2026-11-07) keeps reader capture off the lobby, and D-002 is still open,
so a lobby card promising a Monday send would be the only promise on the page we
cannot keep.

Re-enable it when delivery works, and change `offer.title` back to "Four ways…" /
"Cuatro formas…".

```json
"offer": {
  "brief": {
    "title": "The weekly brief",
    "body": "One email a week per desk: what moved, why it matters, what to watch. Subscribe on the desk you care about.",
    "cta": "Choose a desk"
  }
}
```

```json
"offer": {
  "brief": {
    "title": "El resumen semanal",
    "body": "Un correo a la semana por mesa: qué se movió, por qué importa y qué viene. Se suscribe en la mesa que le interesa.",
    "cta": "Elegir una mesa"
  }
}
```

Until then the desk plates still show a "Brief" chip wherever `offers.brief` is
true — the offer is visible at the desk that serves it, which is where it already
lives on every channel page.

---

## Page metadata

| Key | EN | ES |
|---|---|---|
| `lobby.meta.title` | Herald Fox — eleven industry desks for professionals | Herald Fox — once mesas sectoriales para profesionales |
| `lobby.meta.description` | Eleven industry desks read the primary record and publish what professionals actually have to act on. English and Spanish, free to read. | Once mesas sectoriales leen la fuente primaria y publican lo que un profesional tiene que atender. Inglés y español, gratis. |
| `services.meta.title` | News services and content generation | Servicios de noticias y generación de contenidos |
| `services.meta.description` | We run industry desks under your brand and build the reference documents your team keeps rebuilding. Scope call, four-week pilot, published when reviewed. | Operamos mesas sectoriales con su marca y construimos los documentos de referencia que su equipo rehace. Llamada de alcance, piloto de cuatro semanas, se publica cuando se revisa. |

`hreflang`: `en`, `es`, `x-default` → the apex path, same pattern as `lib/seo.ts`.

## Structured data

- `Organization`: `name` "Herald Fox", `url` the apex, `email` `news@heraldfox.com`, `description` = meta description. No `foundingDate`, no `sameAs` — unknown.
- `ItemList`: one `ListItem` per desk, `url` = the desk's canonical origin (channel subdomain), `name` = desk name. No position ranking claims.
- `Service` × 2 on `/services`: `serviceType` "Industry news service" and "Reference document production", `provider` = the Organization, no `offers`/`price` block (no public prices, D-016).
- No `FAQPage` until the answers freeze (D-002/D-005 move three of them).

## Claims ledger

Every factual assertion in the copy, with its source. Editing copy means editing this table.

| Claim | Where | Status | Evidence |
|---|---|---|---|
| "eleven desks" | hero, directory, footer, board | **measured** 2026-11-07 | `GET /v1/industries` → 11 |
| feed count | not in copy | **not servable** | the DB held 52 source rows on 2026-11-07, but `/v1/sources` filters by channel and recency (legal returns 2), so no total is exposed. The copy states the quality gate instead of a number; add `sources_total` to `/v1/desks` before interpolating one |
| "English and Spanish" | hero, services, footer | **measured** | `locales: ["en","es"]` on every desk |
| "two languages where we have them" | directory intro | **measured** | Spanish depth varies by desk (honest hedge, one only) |
| "a person signs the reference issues" | how, FAQ, services | **measured for reference issues** | reviewer gate + `offer_issues` publish flow; 0 published so far, so the claim is about the mechanism, not a track record |
| "summaries drafted by a model" | FAQ q2 | **measured** | `ai_client.py`, DeepSeek `deepseek-flash` |
| "every item links to its source" | services.news.point4 | **measured** | each card and detail page links out to the publisher; there is no per-item human review, so the copy must never say "reviewed" about news items |
| "a person signs the reference issues" | how, FAQ, services | **mechanism only** | 0 issues published on 2026-11-07 — the gate exists, the track record does not. Do not phrase it as "signed by" until one exists |
| "quality gate before a feed is allowed in" | how.step1Body | **measured** | `sources/application/quality.py` + `verify-sources` CLI |
| "no account, no paywall" | hero note, FAQ q7 | **measured** | public reads need no key |
| "a feed may carry a small, labelled promotion, usually our own" | FAQ q7 | **policy, D-021** | replaces the old absolute "no advertising": the owner intends minimal house promotion, so the copy states the ceiling and the label instead of a ban. The same claim was removed from `proof.independentValue`, `brief.value2` and `asset.note` |
| "signed by the reviewer accountable" | `services.content.signature` | **gated on D-005** | no reviewer named yet — ship the variant without the sentence until one is |
| "weekly brief" | `offer.brief.*` | **gated on D-002** | capture only, delivery not wired |
| "we reply to the ones we can help with" | form success | **assumption** | no reply SLA exists; deliberately does not promise a time |
| "four-week pilot, fixed fee" | engage | **proposal** | D-016; no pilot has run |
| pricing | not on the page | **assumption** | anchors in plan §11 |
| "reference issues listed with sources and a filed date" | `offer.asset.body` | **format claim, no instances yet** | 0 published issues; the card must fall back to the waitlist variant below until one exists |

Two phrases deliberately absent: "within one business day" (existing `cta.promise3` claims it with no partner SLA behind it — do not copy it onto the lobby) and any reader-count, customer-count, or "trusted by" line (nothing to measure yet).

## Variants to keep on hand

- **No published reference issue yet (0 issues, today's state):** keep the `offer.asset` card and use `lobby.offer.asset.ctaWaitlist` ("Join the waitlist" / "Unirse a la lista"), linking to the desk that owns the asset (`legal`, `cybersecurity`). Switch to `lobby.offer.asset.cta` ("Read the archive") only once one issue is published — the archive page has an honest empty state, but the lobby should not send traffic to it.
- **No reviewer named (G2 open):** drop `services.content.signature`, and change `services.news.point4` to "Reviewed before publication, every item linked to its source." — the reviewer clause moves to the news service only where a partner reviewer exists.
- **No delivery yet (G1, resolved by deferral 2026-11-07):** the brief card is not on the page — see "Held until D-002 lands". The desk plates keep their `Brief` chip from the API, because the offer is real at the desk; only the lobby's own card is withheld.
- **Single-language launch:** if a desk has no Spanish, the board shows `EN` only. No copy change needed — the board reads `locales` from the API.

## Next action

Take D-018 (brand string) first: it changes `lobby.brand.name` and the masthead across both locales. Then hand the two catalog blocks to `@ui-director` with the plan's H4–H6.
