# Plan visual — Aluvión en Las Condes

**Formato:** seis imágenes verticales 1080 × 1350 px. `assets/logo.png` en todas, sin alteraciones. Solo cartografía real con derechos comprobados y gráficos editoriales propios. Nada de fotografías o escenas sintéticas. En FASE 1 no se crea `visuals.json` ni ninguna imagen.

## Imagen 1 — Hecho confirmado y lugar
- **Kicker:** «SANTIAGO DE CHILE · 8 DE OCTUBRE»
- **Title:** «Un aluvión golpeó Las Condes»
- **Body:** «El agua y el barro bajaron por San Carlos de Apoquindo. Hubo personas heridas y viviendas dañadas».
- **Callout:** «Emergencia confirmada».
- **Footer:** «Fuentes: Ministerio del Interior y Associated Press».
- **Visual:** cartografía real de OpenStreetMap en la que se identifica el sector, con atribución y rótulo editorial; nunca una escena inventada.

## Imagen 2 — Respuesta confirmada
- **Kicker:** «MEDIDA DEL 9 DE OCTUBRE»
- **Title:** «Las Condes fue declarada zona de catástrofe»
- **Body:** «La medida ayuda a movilizar recursos y acelerar la recuperación tras el aluvión».
- **Footer:** «Fuente: Ministerio del Interior de Chile · 9/10/2026».
- **Visual:** panel tipográfico de noticia confirmada y esquema propio de asistencia. Con las **dos primeras imágenes** se debe comprender sin contexto qué ocurrió, dónde y qué decisión se tomó.

## Imagen 3 — Localización
- **Kicker:** «¿DÓNDE OCURRIÓ?»
- **Title:** «San Carlos de Apoquindo, al oriente de Santiago»
- **Body:** «El sector pertenece a la comuna de Las Condes».
- **Footer:** «Cartografía: © OpenStreetMap contributors · ODbL».
- **Visual:** mapa OSM real; no representar una huella de inundación sin datos geográficos oficiales.

## Imagen 4 — Balance fechado
- **Kicker:** «BALANCE DEL 9 DE OCTUBRE»
- **Title:** «Seis personas resultaron heridas»
- **Stat_label:** «6 personas heridas».
- **Body:** «Es el balance informado por autoridades el 9 de octubre. Puede actualizarse».
- **Footer:** «Fuentes: autoridades citadas por Emol y Associated Press».
- **Visual:** cifra **arriba**, explicación **debajo**, con separación medida y fecha visible.

## Imagen 5 — Lo que falta por confirmar
- **Kicker:** «INVESTIGACIÓN ABIERTA»
- **Title:** «La Fiscalía busca establecer las causas»
- **Body:** «Se revisarán el origen de la crecida y las eventuales responsabilidades».
- **Callout:** «No hay una causa única demostrada».
- **Footer:** «Fuente: Fiscalía Oriente, declaración recogida por Emol · 9/10/2026».
- **Visual:** diagrama de dos columnas: «Confirmado» y «En investigación», sin insinuar culpabilidad.

## Imagen 6 — Información para el público
- **Kicker:** «LAS ALERTAS PUEDEN CAMBIAR»
- **Title:** «Consulta los avisos antes de desplazarte»
- **Body:** «Sigue las indicaciones de Senapred y de la Municipalidad de Las Condes. Los balances y cortes de calles pueden cambiar».
- **Callout:** «No compartas mapas antiguos como avisos vigentes».
- **Footer:** «Información actualizada: fuentes oficiales».
- **CTA:** «Guarda este post para consultar las fuentes».
- **Visual:** tarjeta de texto, trazos e iconos geométricos no fotográficos.

**Preflight FASE 2 obligatorio:** releer textos de `publication.json` y **todos los textos visibles de `visuals.json`** (kicker, title, body, bullets, callout, footer, stat_label, fuentes y CTA), en UTF-8/NFC y con ortografía completa. Comprobar fecha del balance, exactitud del mapa, derechos de cada recurso, atribución, legibilidad, contraste, márgenes y desbordamientos. Antes de producción, verificar si hay balance oficial nuevo o aviso actualizado y ajustar la pieza si afecta su veracidad. No crear `.ready` ni `.visualize` en FASE 1.
