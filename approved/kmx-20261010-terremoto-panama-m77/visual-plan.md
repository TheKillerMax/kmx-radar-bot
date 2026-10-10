# Plan visual — Terremotos en Panamá

**Formato:** seis imágenes 1080 × 1350. Logo aprobado `assets/logo.png` presente sin modificaciones en cada una. Imágenes reales del USGS y paneles informativos propios; ninguna fotografía sintética ni reutilización de fotos AP/Reuters/EFE sin licencia. `visuals.json` no se crea en FASE 1.

## Imagen 1 — Hecho y lugar
- **Kicker:** «PANAMÁ · 9 DE OCTUBRE»
- **Title:** «Un terremoto de magnitud 7,7 sacudió Panamá»
- **Body:** «El epicentro estuvo cerca de Pitaloza Arriba. Hubo daños y evacuaciones».
- **Callout:** «Terremoto confirmado».
- **Footer:** «Fuente: Servicio Geológico de Estados Unidos y Associated Press».
- **Visual:** mapa real del epicentro, producido por USGS, con marca y fecha; si el producto integra capas de terceros sin licencia, reconstruir mapa editorial desde las coordenadas y datos públicos, sin inventar daños.

## Imagen 2 — Los movimientos siguientes
- **Kicker:** «¿QUÉ PASÓ DESPUÉS?»
- **Title:** «Llegaron fuertes réplicas»
- **Body:** «Después del sismo de magnitud 7,7 se registró otro de magnitud 6,6 y numerosos temblores».
- **Footer:** «Fuentes: USGS y Associated Press · 9 y 10 de octubre».
- **Visual:** línea temporal propia desde datos instrumentales de USGS, sin ilustrar destrucción ficticia. Las primeras dos imágenes bastan para explicar qué ocurrió.

## Imagen 3 — Dónde ocurrió
- **Kicker:** «¿DÓNDE FUE?»
- **Title:** «El epicentro quedó en el centro-sur de Panamá»
- **Body:** «Fue cerca de Pitaloza Arriba, al oeste-suroeste de esa localidad».
- **Footer:** «Ubicación: USGS · 7,587° N, 80,769° O».
- **Visual:** mapa de localización auténtico USGS con su rótulo y atribución. No convertir la intensidad estimada en un registro de casas destruidas.

## Imagen 4 — Daños constatados
- **Kicker:** «¿QUÉ DAÑOS HUBO?»
- **Title:** «Se reportaron edificios y carreteras dañados»
- **Body:** «Se documentaron daños y evacuaciones. Las autoridades siguen revisando el alcance».
- **Callout:** «Balances provisionales».
- **Footer:** «Fuentes: Associated Press, Reuters y EFE · 9–10 de octubre».
- **Visual:** esquema informativo propio; sin fotos de prensa sin permiso ni cifras de víctimas no revalidadas.

## Imagen 5 — Aviso de tsunami
- **Kicker:** «AVISO DEL 9 DE OCTUBRE»
- **Title:** «El aviso por tsunami fue levantado»
- **Body:** «Tras el sismo hubo avisos preventivos, levantados después para ese evento. Consulta los nuevos avisos oficiales».
- **Footer:** «Fuente: Associated Press · 9 de octubre».
- **Visual:** cronología rotulada «emitido» y «levantado». No usar capturas viejas como alerta vigente.

## Imagen 6 — Qué sigue
- **Kicker:** «LAS RÉPLICAS PUEDEN CONTINUAR»
- **Title:** «Consulta la información oficial»
- **Body:** «Sigue a Protección Civil de Panamá para conocer daños, medidas y posibles avisos nuevos».
- **CTA:** «Guarda este post para consultar las fuentes».
- **Footer:** «USGS · Sistema Nacional de Protección Civil de Panamá».
- **Visual:** tarjeta tipográfica con fuentes, sin fotografías.

## Revisión obligatoria en FASE 2

Verificar `publication.json` y todas las cadenas visibles de cualquier `visuals.json` futuro, incluidas kicker, title, body, bullets, callout, footer, stat_label, CTA y fuentes, en UTF-8/Unicode NFC. No corregir acentos por transliteración ASCII. Revalidar datos sísmicos, avisos y balances; comprobar licencia por archivo, márgenes, contraste, jerarquía y tamaño móvil. No crear `.visualize` ni `.ready` en FASE 1.