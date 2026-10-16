# Plan visual — FASE 1

**Publicación:** kmx-20261016-terremoto-kamchatka-m69. Seis imágenes de 1080 × 1350 píxeles. Sin fotografías ni escenas sintéticas. Las piezas 01 y 03 incluyen cartografía real de **Natural Earth** (dominio público) con el epicentro indicado según **USGS**; las demás son diagramas y composición tipográfica editorial. En todas debe usarse solo **assets/logo.png**, sin modificaciones de proporción ni color.

## 01-terremoto-kamchatka.png
- kicker: «RUSIA · 16 DE OCTUBRE»
- title: «Un terremoto de magnitud 6,9 sacude Kamchatka»
- body: «Ocurrió en el extremo oriental de Rusia. El USGS confirmó el sismo.»
- callout: «CONFIRMADO»
- footer y fuente visible: «USGS · 16/10/2026 · Mapa: Natural Earth»
- alt_text: «Mapa informativo realizado con datos reales que ubica en Kamchatka, Rusia, el terremoto de magnitud 6,9 del 16 de octubre de 2026.»
- recurso: mapa verdadero de Kamchatka con indicador del epicentro a 51,985° N y 157,270° E. Dibujar el mapa con datos Natural Earth, sin imagen sintética.

## 02-sin-alerta-tsunami.png
- kicker: «¿HAY ALERTA DE TSUNAMI?»
- title: «No hay alerta de tsunami por este terremoto»
- body: «La agencia estadounidense de vigilancia de tsunamis no registró una amenaza asociada al sismo.»
- callout: «Sin aviso de tsunami»
- footer y fuente visible: «NOAA · boletín del 16/10/2026»
- alt_text: «Tarjeta informativa que explica que la agencia estadounidense NOAA no mantenía alerta ni amenaza de tsunami por el terremoto de Kamchatka.»
- recurso: infografía tipográfica con símbolo de información, no escena oceánica inventada.

## 03-donde-ocurrio.png
- kicker: «¿DÓNDE OCURRIÓ?»
- title: «Cerca de Ozernovskiy, en el este de Rusia»
- body: «El epicentro estuvo aproximadamente 76 kilómetros al noreste de esta localidad de Kamchatka.»
- stat: «76 km»
- stat_label: «al noreste de Ozernovskiy»
- footer y fuente visible: «USGS · Natural Earth»
- alt_text: «Mapa de Kamchatka con el punto del sismo marcado unos 76 kilómetros al noreste de Ozernovskiy.»
- recurso: mapa geográfico de dominio público, con escala y etiqueta del epicentro; no mostrar límites geográficos ficticios.

## 04-profundidad.png
- kicker: «¿A QUÉ PROFUNDIDAD?»
- title: «El temblor comenzó a 135 kilómetros bajo tierra»
- body: «Es la profundidad calculada por el USGS. Sus mediciones pueden actualizarse.»
- stat: «135 km»
- stat_label: «profundidad del terremoto»
- footer y fuente visible: «USGS · 16/10/2026»
- alt_text: «Gráfico que indica que el Servicio Geológico de Estados Unidos calculó una profundidad de 135 kilómetros para el terremoto.»
- recurso: esquema geométrico no fotográfico; aclarar que es ilustración explicativa, no imagen del subsuelo.

## 05-primeros-reportes.png
- kicker: «¿HUBO DAÑOS?»
- title: «Sin víctimas ni daños confirmados en los primeros reportes»
- body: «Algunos vecinos salieron de sus viviendas. Las autoridades aún evaluaban la situación.»
- callout: «Balance preliminar»
- footer y fuente visible: «EFE · 16/10/2026»
- alt_text: «Tarjeta con el primer balance de Kamchatka: vecinos evacuaron edificios y todavía no se habían confirmado víctimas ni daños.»
- recurso: tarjeta tipográfica de balance provisional, sin fotografías de personas ni edificios ficticios.

## 06-comprobar-actualizaciones.png
- kicker: «¿QUÉ SIGUE?»
- title: «Los registros y los balances pueden cambiar»
- body: «Consulta al USGS y a la agencia de alertas de tsunami para conocer las actualizaciones oficiales.»
- callout: «Guarda este post para revisar las fuentes.»
- footer y fuentes visibles: «USGS · NOAA»
- alt_text: «Tarjeta que remite al Servicio Geológico de Estados Unidos y a la vigilancia oficial de tsunamis para consultar actualizaciones.»
- recurso: diseño informativo original con referencias legibles.

## Control para FASE 2

Las imágenes 01 y 02 deben explicar el hecho a alguien sin información previa: qué pasó, dónde y qué se sabe del riesgo de tsunami. No generar `visuals.json` en esta fase. Antes del render, verificar cadena por cadena las tildes, eñes y signos de apertura de todos los campos visibles (kicker, title, body, bullets, callout, footer, stat, stat_label, fuentes) y de cada alt_text. Normalizar UTF-8 NFC y comprobar que no aparezcan variantes degradadas. Ajustar las cajas reales de texto y márgenes para móvil. Mantener créditos y procedencia de datos cartográficos. No crear .ready ni .visualize.
