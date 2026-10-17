# KMX RADAR — estado operativo

**Fecha de esta nota:** 16 de octubre de 2026 (instantánea, no estado dinámico).

| Subsistema | Diagnóstico |
| --- | --- |
| Recolección RSS e intake | Operativa; collector programado cada 6 h en `America/Santiago`. |
| Automatizaciones de ChatGPT | Siete tareas canónicas habilitadas, con reglas de no retroceso y recuperación. |
| Producción visual | Operativa; render y QC automatizados con fotografías reales y créditos. |
| GitHub Actions, push a main | Grupo de escritura serializado y recuperación acotada de errores `non-fast-forward` sin force push. |
| Tests CI | Pruebas automatizadas satisfactoriamente ejecutadas tras el refuerzo de resiliencia; revisar Actions para el último resultado. |
| Instagram / Meta | **Bloqueo externo:** `OAuthException 190`; se exige iniciar sesión y completar las instrucciones de Instagram. |
| Publicación automática | Configurada, pero condicionada a que Instagram acepte la credencial, permisos, frescura, derechos, cuotas y QC. |
| Control de duplicados | `publication_id`, recibos persistentes y comprobación de caption exacto ante errores ambiguos. |

El estado dinámico reside en `data/chatgpt_state.json`; el historial confirmado está en `data/published.json`. `PUBLISH_ENABLED` ya no es la configuración operativa (ver `config/autopublish.yml`).

**Acción externa aún necesaria:** el titular de @kmxradar debe acceder a instagram.com para atender la verificación de seguridad. No exponer el token ni la contraseña en el chat. Tras recuperar el acceso, `Check Instagram connection` puede validar la credencial actual o un secreto alternativo autenticado para la misma cuenta.

Más información: [README.md](README.md), [auditoría](docs/AUDIT_KMX_2026-10-16.md), [EDITORIAL_SYSTEM.md](EDITORIAL_SYSTEM.md).
