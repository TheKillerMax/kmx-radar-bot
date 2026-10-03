# KMX RADAR Bot

Infraestructura gratuita para **KMX RADAR** (`@kmxradar`).

Este repositorio **no usa ningún LLM local**. GitHub actúa como radar y publicador; **ChatGPT es el editor/investigador**.

## Arquitectura

```text
GDELT + RSS + fuentes públicas
        ↓
GitHub Actions
        ↓
normalización + clustering
        ↓
señales de corroboración
        ↓
extracción limitada de evidencia
        ↓
ZIP de entrada
        ↓
TÚ SUBES EL ZIP A CHATGPT
        ↓
ChatGPT investiga de nuevo en la web
        ↓
redacción + verificación + imágenes
        ↓
approved/<publication_id>/
        ↓
.ready
        ↓
Instagram API
```

## Qué hace GitHub

El workflow **Build KMX RADAR intake ZIP** se ejecuta cada 2 horas y también manualmente.

Genera un artifact con un archivo parecido a:

```text
kmx-radar-intake-20261002T235900Z.zip
```

Dentro encontrarás:

```text
manifest.json
instructions.md
EDITORIAL_SYSTEM.md
publication-package-schema.json
previous_posts.json
brand/
  logo.svg
events/
  01-.../
    event.json
    evidence.md
  02-.../
    ...
```

El ZIP contiene hasta 10 acontecimientos candidatos, sus URLs, dominios, señales de corroboración y extractos breves.

La puntuación interna **no es una probabilidad de verdad**. Sirve únicamente para ordenar candidatos.

## Flujo con ChatGPT

1. Ve a **Actions → Build KMX RADAR intake ZIP**.
2. Abre la ejecución más reciente.
3. Descarga el artifact `kmx-radar-intake-...`.
4. Sube el ZIP a ChatGPT.
5. Pide a ChatGPT que siga `instructions.md` y `EDITORIAL_SYSTEM.md`.
6. `EDITORIAL_SYSTEM.md` contiene el estándar FORJA-Editorial: rigor, fact-checking, arquitectura narrativa, retención, diseño, ética y trazabilidad.
7. ChatGPT debe volver a investigar en Internet antes de redactar.
8. ChatGPT prepara el contenido final e imágenes.
9. Con el repositorio conectado, ChatGPT puede guardar el resultado en:

```text
approved/<publication_id>/
├── publication.json
├── 01-cover.jpg
├── 02-known.jpg
├── ...
└── .ready
```

**`.ready` debe añadirse al final**, cuando todos los archivos estén completos y la publicación esté realmente aprobada.

## Publicación automática

El workflow **Publish approved KMX RADAR package** se activa al añadirse:

```text
approved/**/.ready
```

Para permitir publicaciones reales, crea en:

**Settings → Secrets and variables → Actions → Variables**

```text
PUBLISH_ENABLED=true
```

Mientras sea `false`, no se publica nada.

El publicador admite:

- una imagen;
- carruseles de hasta 10 imágenes;
- caption;
- alt text;
- identificación `is_ai_generated` cuando corresponda;
- límite diario de publicaciones;
- separación mínima entre publicaciones;
- registro de lo ya publicado para evitar duplicados.

## Secretos

En:

**Settings → Secrets and variables → Actions → Secrets**

deben existir:

### `INSTAGRAM_ACCESS_TOKEN`

Token de la Instagram API generado en Meta Developers.

### `TOKEN_ENCRYPTION_PASSWORD`

Cadena aleatoria de al menos 24 caracteres.

Nunca publiques ninguno de esos valores.

## Estado de la conexión

La conexión con Instagram ya fue comprobada mediante:

**Actions → Check Instagram connection**

y el workflow terminó correctamente.

## Renovación del token

El workflow **Refresh Instagram token** intenta renovar semanalmente el token de larga duración y guarda la nueva versión cifrada en:

```text
data/instagram_token.enc
```

## Política editorial

KMX RADAR prioriza:

- fuentes primarias;
- varias fuentes independientes;
- separación entre hechos, declaraciones e inferencias;
- transparencia sobre incertidumbre;
- correcciones visibles;
- no copiar fotografías o artículos de terceros sin permiso.

En política y elecciones, ChatGPT debe presentar hechos y posiciones documentadas sin apoyar, oponerse, clasificar, puntuar ni predecir ganadores.

En salud, conflictos, fallecimientos, acusaciones criminales, seguridad pública y elecciones se exige verificación reforzada.

Un acontecimiento no tiene por qué convertirse en publicación. **Omitir es preferible a inventar.**

## Formato del paquete final

Consulta:

```text
publication-package-schema.example.json
```

Campos principales:

- `publication_id`
- `source_event_id`
- `status`
- `headline`
- `caption`
- `sources`
- `images`
- `ready_to_publish`

## Coste

El diseño evita:

- OpenAI API;
- APIs LLM de pago;
- servidores de pago;
- Canva/Metricool;
- dominio propio.

GitHub recopila y publica; ChatGPT se usa interactuando desde tu cuenta.

---

**KMX RADAR — Detectamos lo que importa.**
