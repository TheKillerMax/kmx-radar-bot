# Fuentes visuales y licencias — FASE 1

Publicación: `kmx-20261023-terremoto-tibet-nagqu-m70`. Evento: `12-4d0e5e05c4acdb01`. Manifest: `2026-10-23T08:27:27Z`. Preparado: `2026-10-23T09:26:24Z`. Ningún recurso externo se ha descargado todavía; rutas locales son previstas.

## 1 · Natural Earth: mapa real de contexto (imágenes 01 y 02)
- source_url: https://www.naturalearthdata.com/downloads/
- original_creator: Natural Earth (Tom Patterson, Nathaniel Vaughn Kelso y colaboradores).
- license_or_permission: Dominio público para datos vectoriales y raster de Natural Earth; permite modificación y uso comercial.
- license_url: https://www.naturalearthdata.com/about/terms-of-use/
- attribution_required: false; crédito informativo recomendado.
- attribution_text: Cartografía: Natural Earth (dominio público).
- local_path: approved/kmx-20261023-terremoto-tibet-nagqu-m70/sources/natural-earth-context.zip (ruta prevista, aún inexistente).
- retrieved_at: 2026-10-23T09:26:24Z (consulta de condiciones; sin descarga).
- notes: construir mapa original con límites políticos marcados como aproximados según dataset; ninguna foto, imagen satelital protegida ni capa de terceros. Punto geográfico documentado por USGS. Evitar presentar el mapa como ShakeMap de intensidad real si no se ha importado tal modelo.

## 2 · USGS: datos originales para marcador geográfico y sismo (imágenes 01 y 02)
- source_url: https://earthquake.usgs.gov/earthquakes/eventpage/us6000u43g
- original_creator: U.S. Geological Survey (USGS), evento us6000u43g.
- license_or_permission: Datos producidos por USGS: dominio público federal de EE. UU.; comprobar cualquier componente externo antes de reutilizarlo.
- license_url: https://www.usgs.gov/information-policies-and-instructions/copyrights-and-credits
- attribution_required: crédito solicitado por USGS.
- attribution_text: Datos sísmicos: Servicio Geológico de Estados Unidos (USGS).
- local_path: approved/kmx-20261023-terremoto-tibet-nagqu-m70/sources/us6000u43g-data.json (ruta prevista, aún inexistente).
- retrieved_at: 2026-10-23T09:26:24Z (consulta de datos y metadatos; sin descargar material gráfico).
- notes: 32,381° N; 93,780° E; magnitud 7,0; profundidad 18 km según USGS. No reutilizar mosaicos de OpenStreetMap, Google Maps ni logotipo USGS bajo esta autorización. Mapas finales son composiciones propias.

## 3 · Fuentes informativas para tarjetas 03–06 (sin fotografías externas)
- Balance inicial de Nagqu, citado por Xinhua: https://www.news.cn/politics/20261023/1504202b7b854ca581a7d3c85c2d9251/c.html
- Ministerio chino y red sísmica nacional, citados por Xinhua: https://www.news.cn/politics/20261023/d8bb1ab3f2fe47eaba1734407d9acf66/c.html
- Último balance de heridos y traslados, Reuters: https://www.reuters.com/world/china/injuries-chinas-tibet-rise-65-after-earthquake-death-toll-remains-16-2026-10-23/
- Confirmación independiente y daños, Associated Press: https://apnews.com/article/china-earthquake-tibet-be27a2db79ada1c6309914d173b983a8
- Tipo de recurso: cifras y explicaciones incorporadas en diagramas originales; estas páginas NO conceden por sí solas derechos sobre fotografías y vídeos.
- attribution_text: «Fuentes: autoridades locales de Nagqu, Xinhua, Reuters y AP · 23/10/2026».
- local_path: no aplica; piezas originales sin foto externa.
- retrieved_at: 2026-10-23T09:26:24Z (revisión de fuentes, no descarga de imágenes).
- notes: NO usar fotografías ni vídeos de Reuters, AP, Xinhua ni redes sociales salvo autorización expresa adicional. Si en FASE 2 se agrega un archivo, verificar y documentar licencia individualmente en visual-sources.json antes del uso.

## 4 · Logo oficial
- source_url / local_path: `assets/logo.png` (archivo interno autorizado del proyecto).
- license_or_permission: uso aprobado para la identidad de KMX RADAR dentro del repositorio; no recrearlo.
- attribution_required: no, es la marca propia.
- notes: usar en las seis piezas, preservar proporciones, color, márgenes y legibilidad.

**En FASE 2:** registrar `visual-sources.json` con source_url, original_creator, license_or_permission, attribution_required, attribution_text, local_path, retrieved_at y notes. No fabricar fotografías documentales ni usar contenido comercial no licenciado.