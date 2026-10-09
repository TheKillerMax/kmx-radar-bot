# Plan visual — Huracán Isaías, octubre de 2026

**Formato:** seis imágenes de 1080 × 1350 px (4:5). Logo aprobado `assets/logo.png` en las seis. Material meteorológico real y trazable del NHC/NOAA; gráficos propios de texto y datos cuando resulten más legibles. Sin fotografías sintéticas. Incluir hora de corte visible donde aparezcan datos meteorológicos.

## 1 — Situación confirmada
- **Kicker:** «GOLFO DE MÉXICO · 9 DE OCTUBRE»
- **Title:** «Isaías ya es huracán de categoría 3»
- **Body:** «Sigue sobre el mar y se acerca a la costa de Estados Unidos».
- **Callout:** «Vientos de hasta 193 km/h» (medición de las 7:20 a. m. CDT).
- **Footer:** «Fuente: Centro Nacional de Huracanes · Datos de la mañana».
- **Visual:** mapa real del NHC del fenómeno, con su crédito y fecha. No confundir con mapas de Isaías de 2020.

## 2 — Llegada prevista
- **Kicker:** «¿DÓNDE SE ESPERA?»
- **Title:** «Entre Alabama y el noroeste de Florida»
- **Body:** «Se prevé que llegue a tierra la noche del viernes 9. Aún no había ocurrido en la actualización consultada».
- **Callout:** «Pronóstico: puede cambiar».
- **Footer:** «Fuente: NHC / AP · 9 de octubre de 2026».
- **Visual:** segundo gráfico oficial del NHC con avisos o trayectoria; no dibujar un punto de impacto exacto ni presentar una franja prevista como certeza. Estas **dos primeras imágenes** deben permitir comprender por sí solas quién es Isaías, qué está ocurriendo y qué falta por suceder.

## 3 — Fuerza observada
- **Kicker:** «¿QUÉ SIGNIFICA CATEGORÍA 3?»
- **Title:** «Es un huracán de gran intensidad»
- **Stat_label:** «120 mph · 193 km/h»
- **Body:** «Velocidad de sus vientos sostenidos, según el NHC en la mañana del 9 de octubre».
- **Footer:** «Medición del 9/10, 7:20 a. m., hora central de EE. UU.».
- **Visual:** gráfico tipográfico propio; **cifra grande arriba, explicación debajo**, sin superposición.

## 4 — Agua y lluvia
- **Kicker:** «LOS RIESGOS»
- **Title:** «El peligro también viene del agua»
- **Bullets:** «El mar puede avanzar sobre zonas costeras». «Las lluvias pueden causar inundaciones». «Los vientos pueden provocar daños».
- **Callout:** «El riesgo cambia según el lugar».
- **Footer:** «Fuente: NHC / AP».
- **Visual:** pictogramas planos y diagramas editoriales; no simular barrios inundados ni atribuir alturas específicas a localidades no confirmadas.

## 5 — Medidas locales
- **Kicker:** «PREPARATIVOS»
- **Title:** «Hay zonas costeras con órdenes de evacuación»
- **Body:** «Las medidas las definen las autoridades de cada localidad. No todas las zonas tienen la misma alerta».
- **Footer:** «Fuentes: AP y avisos locales referidos por NHC».
- **Visual:** mapa real de áreas bajo avisos del NHC. No reemplaza las órdenes de evacuación locales.

## 6 — Qué sigue
- **Kicker:** «LA SITUACIÓN PUEDE CAMBIAR»
- **Title:** «Antes de compartir, revisa el último aviso»
- **Body:** «El huracán seguía en el mar en el último dato usado para esta publicación. Su recorrido e intensidad pueden cambiar».
- **Callout:** «Alertas actualizadas: NHC y autoridades locales».
- **Footer:** «Datos y pronóstico: mañana del 9/10/2026».
- **Visual:** cronología editorial propia «observado → previsto → por confirmar», sin simular imágenes reales.
- **CTA:** «Guarda este post para consultar las fuentes».

**Preflight obligatorio FASE 2:** verificar de nuevo categoría, hora de corte, pronósticos y avisos **antes de renderizar o publicar**. Si el dato dejó de ser actual y cambia el sentido del titular, devolver a editorial. Comprobar todos los textos visibles de `visuals.json`: kicker, title, body, bullets, callout, footer, stat_label, créditos y CTA. Unicode NFC, tildes y signos de apertura, longitud de cajas, márgenes, contraste y legibilidad en móvil. No crear `visuals.json`, `.ready` o `.visualize` en FASE 1.