# Plan visual — FASE 1

Publicación: `kmx-20261023-terremoto-tibet-nagqu-m70` · Evento: `12-4d0e5e05c4acdb01` · Manifest: `2026-10-23T08:27:27Z` · Creación: `2026-10-23T09:26:24Z`. Seis imágenes verticales **1080 × 1350**; diseño de información propio, cartografía real de Natural Earth y datos oficiales de USGS. En **todas** las imágenes usar `assets/logo.png` intacto, con márgenes seguros. No crear imágenes ni `visuals.json` durante FASE 1.

## 01 · 01-terremoto-tibet.png
- kicker: **TÍBET · 22 DE OCTUBRE**
- title: **Un terremoto de magnitud 7,0 sacude el norte del Tíbet**
- body: **Ocurrió en Nagqu, China. Autoridades confirman al menos 16 muertos; el balance sigue actualizándose.**
- stat: **7,0**
- stat_label: **Magnitud registrada**
- callout: **BALANCE PROVISIONAL**
- footer / fuentes: **USGS · Reuters · 23/10/2026**
- recurso: mapa de situación original sobre cartografía pública Natural Earth, punto USGS verificado; no foto del desastre.
- alt_text: Mapa informativo original con la ubicación aproximada del sismo de magnitud 7,0 del 22 de octubre de 2026 en Nagqu, Tíbet, China; balance provisional de al menos 16 fallecidos.

## 02 · 02-donde-ocurrio.png
- kicker: **¿DÓNDE OCURRIÓ?**
- title: **Cerca de Baqen, en la región china de Nagqu**
- body: **22 de octubre · 22:33 hora local. El epicentro se registró en la meseta tibetana.**
- stat: **18 km / 10 km**
- stat_label: **Profundidad estimada: USGS / CENC**
- footer / fuentes: **USGS · Centro de Redes Sísmicas de China**
- recurso: mapa original a escala indicativa con coordenadas y sin imágenes satelitales de terceros.
- alt_text: Mapa de Natural Earth con un punto en el norte del Tíbet, cerca de Baqen, y la hora local del terremoto, 22:33 del 22 de octubre de 2026.

## 03 · 03-balance-provisional.png
- kicker: **¿QUÉ SABEMOS DE LAS VÍCTIMAS?**
- title: **Al menos 16 personas fallecidas**
- body: **Las autoridades también informaron de 76 personas heridas en una actualización del 23 de octubre. Son cifras preliminares.**
- stat: **16**
- stat_label: **Fallecidos confirmados, según autoridades**
- callout: **DATOS EN ACTUALIZACIÓN**
- footer / fuentes: **Reuters · 23/10/2026**
- recurso: tarjetas de datos tipográficas. Apilar cifra y rótulo; nunca colocar leyenda al lado sin medir.
- alt_text: Tarjeta informativa: al menos 16 personas fallecidas y 76 heridas según actualización de autoridades locales publicada por Reuters el 23 de octubre de 2026.

## 04 · 04-danos-en-viviendas.png
- kicker: **¿QUÉ DAÑOS SE HAN REPORTADO?**
- title: **Más de 300 viviendas derrumbadas**
- body: **El informe inicial de Nagqu consignó 339 hogares con viviendas colapsadas. Las inspecciones siguen en curso.**
- stat: **339**
- stat_label: **Hogares afectados por derrumbes, balance inicial**
- footer / fuentes: **Xinhua · AP · 23/10/2026**
- recurso: visualización tipográfica, sin fotografías no autorizadas ni ilustraciones ficticias.
- alt_text: Tarjeta documental con la cifra provisional de al menos 339 viviendas derrumbadas, atribuida a la autoridad de Nagqu según Xinhua y Associated Press.

## 05 · 05-evacuaciones-y-rescate.png
- kicker: **¿QUÉ PASA CON LA POBLACIÓN?**
- title: **Más de 12.000 personas reubicadas**
- body: **Los equipos de emergencia evalúan daños y ayudan a los afectados. La electricidad y las comunicaciones se restablecen gradualmente.**
- callout: **EL RESCATE CONTINÚA**
- footer / fuentes: **Xinhua, citada por Reuters · 23/10/2026**
- recurso: diagrama propio, datos atribuidos, sin imagen simulada.
- alt_text: Gráfico tipográfico que indica más de 12.000 personas reubicadas según Xinhua, junto a una nota sobre rescate y recuperación de servicios.

## 06 · 06-que-falta-saber.png
- kicker: **¿QUÉ SIGUE?**
- title: **El balance puede cambiar**
- body: **Continúan las réplicas y las inspecciones. Las autoridades actualizarán los datos de víctimas y daños.**
- callout: **Guarda este post para consultar las actualizaciones.**
- footer / fuentes: **USGS · autoridades locales · Reuters · 23/10/2026**
- recurso: tarjeta propia, sin predicciones sísmicas.
- alt_text: Tarjeta final que informa de réplicas y de la revisión continua de víctimas y daños, sin ofrecer predicciones de nuevos terremotos.

## Control bloqueante de FASE 2

Revisar cifras y cortes temporales antes de dibujar; mantener los textos públicos y `visuals.json` en UTF-8 Unicode NFC, con á, é, í, ó, ú, ü, ñ, ¿ y ¡ según corresponda. Campos: kicker, title, body, bullets, callout, footer, stat, stat_label, fuentes. No transliterar. Medir cada caja, verificar márgenes, solapamientos, contraste móvil, atribución y presencia del logo auténtico. No generar fotografías sintéticas. Registrar cualquier material externo en `visual-sources.json` con licencia comprobada. Nunca interpretar el mapa como medición de daños. **No crear .visualize, .ready ni publicar aquí.**