# KMX RADAR Bot

Sistema automatizado y gratuito para **KMX RADAR** (`@kmxradar`): descubre noticias, agrupa duplicados, exige corroboración entre fuentes independientes, redacta una pieza breve en español, genera una tarjeta gráfica con la marca y puede publicarla mediante la API oficial de Instagram.

> **Diseño editorial:** el bot no publica todo lo que encuentra. Si la evidencia no supera los umbrales configurados, la historia se descarta o queda en estado `EN DESARROLLO`. La puntuación interna es una puerta editorial, **no una probabilidad de verdad**.

## Arquitectura

```text
GDELT + RSS oficiales
        ↓
normalización y deduplicación
        ↓
clustering por acontecimiento
        ↓
corroboración / fuente primaria / riesgo
        ↓
extracción limitada de evidencia
        ↓
LLM local pequeño (Qwen2.5 0.5B) solo para redactar
        ↓
validador anti-cifras inventadas
        ↓
Pillow genera 1080×1350 con logo KMX RADAR
        ↓
archivo público en el repositorio
        ↓
Instagram Content Publishing API
```

## Coste

El proyecto está diseñado para **0 € de suscripciones**:

- repositorio público de GitHub;
- GitHub Actions con runner estándar;
- GDELT y RSS públicos;
- modelo open source ejecutado dentro del runner;
- Pillow para gráficos;
- Instagram API oficial.

No se requiere OpenAI API, Canva, Metricool, hosting de pago ni dominio.

## Requisitos previos

1. Cuenta profesional de Instagram `@kmxradar`.
2. App de Meta configurada con **Instagram API with Instagram Login**.
3. Permisos `instagram_business_basic` y `instagram_business_content_publish`.
4. Access Token generado desde el App Dashboard.
5. Repositorio **público** llamado `kmx-radar-bot`.

## Configurar secretos

Ve a:

**Settings → Secrets and variables → Actions → New repository secret**

Crea:

### `INSTAGRAM_ACCESS_TOKEN`
Pega el token de Instagram que generaste en Meta Developers.

### `TOKEN_ENCRYPTION_PASSWORD`
Usa una cadena aleatoria de al menos 24 caracteres.

El bot usa esta contraseña para cifrar el token renovado antes de guardarlo en el repositorio público.

**Nunca publiques ninguno de estos dos valores.**

## Probar la conexión de Instagram

En GitHub:

**Actions → Check Instagram connection → Run workflow**

El token no se imprime.

## Ejecutar primero en modo prueba

Por defecto no publica en Instagram.

En:

**Settings → Secrets and variables → Actions → Variables**

crea:

```text
PUBLISH_ENABLED = false
```

Después ejecuta manualmente:

**Actions → KMX RADAR → Run workflow**

El bot intentará:

1. descubrir noticias recientes;
2. agrupar historias repetidas;
3. puntuar corroboración;
4. seleccionar como máximo una candidata;
5. redactar;
6. generar la imagen en `docs/media/`;
7. guardar `data/last_candidate.json`.

Si no encuentra una noticia que pase los controles, no crea ninguna publicación.

## Activar publicación automática

Cuando hayas revisado varias ejecuciones de prueba y estés conforme:

```text
PUBLISH_ENABLED = true
```

El workflow se ejecuta automáticamente a los minutos `17` y `47` de cada hora.

## Seguridad del token

El primer run usa `INSTAGRAM_ACCESS_TOKEN` desde GitHub Secrets y crea:

```text
data/instagram_token.enc
```

Ese archivo contiene el token **cifrado**, nunca en texto plano.

El workflow `Refresh Instagram token` intenta renovar el token una vez por semana y guarda la versión nueva cifrada.

## Reglas editoriales incluidas

- mínimo de dominios independientes;
- bonificación por fuente oficial/primaria;
- mayor umbral para política, conflictos y salud;
- límite de publicaciones por día;
- separación mínima entre publicaciones;
- el LLM no decide si una noticia está verificada: redacta **después** de la corroboración;
- el LLM recibe solo fragmentos limitados de las fuentes;
- cualquier cifra generada que no aparezca en la evidencia hace que la salida se rechace;
- si falla el modelo, el sistema usa una plantilla determinista;
- sin fotografías copiadas de medios: la imagen se genera gráficamente con el logo, el titular y las fuentes.

## Qué significa cada estado

- `VERIFICADO`: pasó el umbral y se detectó una fuente primaria/oficial.
- `CORROBORADO`: pasó el umbral con varias fuentes independientes y de calidad, sin fuente primaria directa.
- `EN DESARROLLO`: hay convergencia parcial, pero no se publica automáticamente.
- `SIN CONFIRMAR`: evidencia insuficiente; no se publica.

Estos rótulos describen el **estado de verificación del bot**, no garantizan verdad absoluta.

## Limitaciones importantes

Un sistema gratuito y autónomo no equivale a una redacción humana internacional. Puede haber medios inaccesibles, errores de GDELT, coberturas repetidas que provengan de la misma agencia, información oficial incompleta y errores del modelo local.

Por eso los controles están diseñados para **omitir una noticia antes que inventar o forzar una publicación**.

Para temas delicados —acusaciones criminales, fallecimientos no confirmados, elecciones, conflictos, salud y seguridad pública— los umbrales son más altos.

## Pruebas locales

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -e .
pytest -q
```

## Política de correcciones

KMX RADAR debe conservar públicamente las correcciones materiales.

---

**KMX RADAR — Detectamos lo que importa.**
