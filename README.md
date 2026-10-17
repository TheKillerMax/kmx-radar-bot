# KMX RADAR

Pipeline editorial y de publicación de [@kmxradar](https://www.instagram.com/kmxradar/) — «Detectamos lo que importa».

**Arquitectura:** GitHub Actions descubre noticias, conserva el estado, renderiza y publica. Las tareas programadas de ChatGPT investigan, verifican, redactan y preparan paquetes. No se ejecuta un LLM local ni se requiere OpenAI API para el flujo editorial.

## Flujo actual

```text
GitHub collector (intake/latest)
  → ChatGPT: Editorial / Editorial Recovery
  → approved/<publication_id>/{research.md,publication.json,visual-plan.md,visual-sourcing-plan.md,handoff.json}
  → ChatGPT: Visual Production / Visual Recovery
  → visual-sources.json + visuals.json
  → GitHub: prepare-visuals (imágenes 1080×1350 + visual-qc.json)
  → ChatGPT: Publish Check
  → .ready (solo después de pruebas editoriales, derechos y QC)
  → GitHub: publish-approved
  → .published.json + data/published.json + data/chatgpt_state.json
  → ChatGPT: Publish Reconcile / Sync Guard
```

GitHub genera `intake/latest/` automáticamente; **no es necesario descargar un ZIP ni volver a subirlo manualmente** en cada ciclo. El ZIP sigue disponible como artifact para inspección opcional. Cada intake contiene hasta 12 candidatos y sus señales automáticas **no representan probabilidades de verdad**.

### Horarios

El collector se programa aproximadamente a las **00:05, 06:05, 12:05 y 18:05, zona `America/Santiago`**, con cambios de horario de verano incorporados. GitHub puede retrasar una ejecución programada. Las siete tareas KMX RADAR se ejecutan cada seis horas, en esta secuencia local:

| Tarea | Hora base (repite cada 6 h) |
| --- | --- |
| Sync Guard | 00:15 |
| Editorial | 00:30 |
| Editorial Recovery | 00:55 |
| Visual Production | 01:30 |
| Visual Recovery | 02:10 |
| Publish Check | 02:30 |
| Publish Reconcile | 03:05 |

Estas tareas pertenecen al **chat original KMX RADAR**: no las dupliques en otras conversaciones. Los workflows de preparación visual y publicación también ejecutan reconciliación periódica para recuperar marcadores y recibos.

## Fuente de verdad y reglas

- **Estado activo:** `data/chatgpt_state.json`.
- **Intake:** `intake/latest/manifest.json` y `intake/latest/events/*`.
- **Historial de publicaciones:** `data/published.json` y `approved/<id>/.published.json`. Un workflow verde o un `.ready` **no** prueba que Instagram publicó.
- **Guía editorial:** `EDITORIAL_SYSTEM.md`, investigación en fuentes primarias e independientes y neutralidad política.
- **Imágenes:** únicamente fotografías/documentos reales con permisos de reutilización, registro en `visual-sources.json`, marca ARCHIVO o IMAGEN DE REFERENCIA cuando proceda, y logo oficial `assets/logo.png`. No se usan fotografías sintéticas como evidencia.
- **Calidad:** 6–10 imágenes estándar 1080×1350, `visual-qc.json` satisfactorio, alt text completo y español UTF-8/Unicode NFC (incluidos **ñ, tildes, ü, ¿, ¡** cuando corresponda).
- **Hashtags:** 3–5 específicos, sin repetidos e incluyendo habitualmente `#KMXRadar`.
- **Cuotas de publicación:** máximo **8 historias cada 24 horas** y separación mínima de **75 minutos**; las correcciones con el mismo `source_event_id` cuentan como una historia.
- **Idempotencia:** no publicar de nuevo `publication_id` ya registrado; comprobar coincidencia exacta de caption en Instagram antes de reintentos ante respuestas ambiguas.

No se publican automáticamente paquetes históricos aunque conserven `.ready` si no corresponden al publication_id activo; antes de reanudarlos hay que verificar la vigencia de hechos y permisos.

## Publicación y autenticación de Instagram

La publicación automática está controlada por **`config/autopublish.yml`** (actualmente `enabled: true`), no por la antigua variable `PUBLISH_ENABLED`. GitHub Actions usa los secretos:

- `INSTAGRAM_ACCESS_TOKEN`: credencial de la API de Instagram.
- `TOKEN_ENCRYPTION_PASSWORD`: contraseña de cifrado (24 caracteres o más).

El token cifrado se almacena en `data/instagram_token.enc`; no publiques ni pegues los valores en el repositorio o en el chat. El workflow `refresh-token.yml` intenta actualizarlo semanalmente; si existe un secreto distinto solo puede reemplazar el token cifrado **después** de comprobar que autentica la misma cuenta `@kmxradar`.

**Incidencia detectada el 16 de octubre de 2026:** Instagram devolvió `OAuthException code=190`, exigiendo iniciar sesión y seguir las instrucciones de seguridad en instagram.com. **Desactivar la seguridad del repositorio GitHub no soluciona un bloqueo de Meta.** Para resolverlo, el titular de `@kmxradar` debe iniciar sesión en Instagram y completar cualquier comprobación exigida. Si se requiere una autorización nueva, actualizar el secreto correspondiente desde GitHub Settings, nunca en un chat. Después, probar **Actions → Check Instagram connection** y comprobar el recibo real del publicador.

Ante este error, el sistema registra `external_error_code=instagram_auth_190`, conserva `.ready` y la publicación aprobada, y espacia los reintentos. No declara éxito ni duplica el contenido.

## Fiabilidad de GitHub

Los workflows que escriben usan el grupo de concurrencia `kmx-radar-main-writer`. El helper `.github/scripts/push-main-safely.sh` detecta carreras reales de push y realiza reintentos acotados de **fast-forward**, sin force push y sin sortear reglas de seguridad. Un conflicto de rebase no se ignora: se detiene para reconciliación segura. Los tests se ejecutan con `pytest -q`.

No es recomendable dejar las protecciones de GitHub desactivadas: mantén los permisos mínimos para Actions y gestiona autorizaciones explícitas para la identidad escritora. La seguridad editorial, derechos, QC y verificación de Meta nunca se desactivan para acelerar publicaciones.

## Diagnóstico

1. Leer `data/chatgpt_state.json` y compararlo con el `manifest.generated_at`.
2. Localizar el paquete activo y comprobar `publication.json`, `.ready`, `visual-qc.json` y `.published.json`.
3. Consultar **GitHub → Actions**: `Build KMX RADAR intake ZIP`, `Prepare KMX RADAR visuals`, `Publish approved KMX RADAR package`, `Refresh Instagram token` y `Check Instagram connection`.
4. Si el error es `OAuthException 190`, resolver el control de acceso de Instagram; no forzar publicaciones ni borrar recibos.
5. Reconciliar antes de reintentar; un error de publicación ambiguo puede corresponder a un post ya visible.

Consulta [el informe de auditoría](docs/AUDIT_KMX_2026-10-16.md), [el sistema editorial](EDITORIAL_SYSTEM.md) y [el esquema de publicación](publication-package-schema.example.json).

---

**KMX RADAR — Detectamos lo que importa.**
