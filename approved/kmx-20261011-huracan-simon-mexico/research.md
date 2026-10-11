# Investigación editorial — huracán Simón frente a México

**Publicación:** `kmx-20261011-huracan-simon-mexico`  
**Evento de entrada:** `02-f26f2391dd17e5ec`  
**Manifest:** `2026-10-11T09:54:35Z`  
**Corte de evidencia meteorológica:** 11 de octubre de 2026, **15:00 UTC**, aviso 17 del Centro Nacional de Huracanes de EE. UU. (NHC). Los avisos posteriores pueden modificar posición, fuerza y advertencias.

## Confirmación principal y límites

El boletín 17 del NHC (15:00 UTC del 11 de octubre) registra al huracán **Simon**, denominado **Simón** en redacción española, como categoría 4, con **vientos máximos sostenidos de 230 km/h**. Su centro estaba cerca de **19,2° N, 105,3° O**, unos **105 km al noroeste de Manzanillo** y 140 km al sur-sureste de Cabo Corrientes. Se desplazaba hacia el nor-noroeste a unos 11 km/h. No se confirma que el centro haya tocado tierra. El aviso de huracán cubre desde **Punta San Telmo hasta El Roblito**, así como **las Islas Marías**. Un aviso es una advertencia de condiciones peligrosas previstas en algún punto del sector, no una afirmación de que todos los municipios ya están recibiendo los mismos impactos.

El NHC prevé lluvias adicionales intensas, con riesgo de **inundaciones y deslizamientos** en terreno montañoso, y **marejada ciclónica y olas destructivas** en la costa cercana a donde se aproxime el centro. Estas son previsiones sujetas a cambios, no mediciones de inundación registradas en cada localidad. Una evolución lenta, paralela a costa o más cerca de tierra puede modificar la exposición local. El NHC prevé que el núcleo permanezca muy cerca de la costa el domingo y lunes, pero **no se establece una localidad definitiva de impacto**.

El Gobierno de México informó el 10 de octubre de suspensión de actividades no esenciales en zonas de Jalisco, Colima, Michoacán y Nayarit por la amenaza. Su comunicación prueba el anuncio de la medida y su fecha; para conocer vigencia y alcance por municipio se debe recurrir a las autoridades locales. Associated Press publicó el 11 de octubre reportería independiente sobre medidas de seguridad, suspensión de clases y preparativos de habitantes y comercios; se evita trasladar fotografías de AP sin licencia. La cobertura independiente no sustituye las advertencias meteorológicas oficiales.

## Fuentes originales y contraste

1. **NHC, aviso público 17**, 11/10/2026, 15:00 UTC: https://prod-east-nhc.woc.noaa.gov/mobile/text/refresh/MIATCPEP5%2Bhtml/111452.shtml
2. **NHC, pronóstico oficial 17**, 11/10/2026, 15:00 UTC: https://prod-east-nhc.woc.noaa.gov/mobile/text/refresh/MIATCMEP5%2Bhtml/111450.shtml
3. **Gobierno de México, Presidencia, 10/10/2026**, medidas preventivas: https://www.gob.mx/presidencia/prensa/presidenta-informa-suspension-de-actividades-no-esenciales-en-jalisco-colima-michoacan-y-nayarit-por-huracan-simon-categoria-4?idiom=es
4. **Associated Press, 11/10/2026**, preparativos y efectos costeros: https://apnews.com/article/0e3336ba92518117ca8008c5746d230e
5. **El País México, 11/10/2026**, alerta y refugios locales: https://elpais.com/mexico/2026-10-11/jalisco-y-colima-se-preparan-para-la-embestida-del-huracan-simon-de-categoria-cuatro.html
6. **NOAA — condiciones generales de imágenes y gráficos**: https://oceanservice.noaa.gov/about/faq.html

No confundir coberturas derivadas de un mismo boletín con mediciones independientes. NHC mide y pronostica, las autoridades mexicanas deciden medidas y AP contrasta impactos y preparativos. Las cifras **250 km/h** del aviso de las 09:00 UTC ya habían cambiado a **230 km/h** a las 15:00 UTC: se usa exclusivamente la segunda observación y se indica su hora. Las condiciones reales posteriores pueden ser distintas.

## Descarte del resto de eventos y duplicados

Se leyeron `EDITORIAL_SYSTEM.md`, instrucciones, manifest, las **12 parejas** `event.json`/`evidence.md` y los **19 registros** de `previous_posts.json`. Se revisaron los directorios de `approved/` y todos los `handoff.json` disponibles: **ninguno** registra el manifest `2026-10-11T09:54:35Z`. El estado anterior marca `last_processed_generated_at=2026-10-11T00:11:58Z`, distinto del manifest presente. No hay cobertura previa de **Simón** entre las publicaciones enumeradas; la noticia de **Isaías** corresponde a otro huracán.

- **01 y 03:** resultados WWE de Penta y Tiffany Stratton; clasificación económica incorrecta, menor prioridad de servicio público.
- **02, seleccionado:** huracán categoría 4, confirmación meteorológica primaria, medidas mexicanas y reportería independiente; alto valor público y urgencia.
- **04:** pleno de Les Corts sobre vivienda; agenda futura y relevancia geográfica limitada.
- **05:** propuesta de la Agencia Espacial Europea sobre autonomía espacial y financiación; su aprobación o alcance no están demostrados por dos notas derivadas.
- **06:** polémica arbitral sobre Vinícius y Tchouaméni, erróneamente etiquetada como ciencia.
- **07:** desarrollo de robots lunares de la ESA; fuente primaria disponible, impacto inmediato menor y sin contraste adicional localizado.
- **08:** réplicas en Panamá; sólo una fuente agregadora y continuidad de un terremoto ya tratado en `kmx-20261010-terremoto-panama-m77`.
- **09:** pronósticos diarios de ciudades alicantinas, erróneamente clasificados como tecnología.
- **10:** ataque al aeropuerto de Riad; ya hay paquete editorial `kmx-20261010-ataque-aeropuerto-riad`; actualización de víctimas necesita investigación distinta y no justifica duplicarlo.
- **11:** detenciones en protestas de Nueva Delhi; alto riesgo de errores de cifras y requiere contrastes primarios más amplios.
- **12:** posible investigación antimonopolio estadounidense a cadenas por el veto a CNN; polémica política que necesita documentación regulatoria y respuestas completas.

## Decisiones y cautelas editoriales

- Tratamiento informativo, sin espectacularizar un desastre ni especular sobre fallecimientos o destrucción.
- El titular, las primeras dos imágenes y el primer párrafo pueden comprenderse sin conocimientos previos.
- No afirmar lugar ni hora de entrada a tierra; no atribuir fotografías de tormentas antiguas a 2026.
- Antes de FASE 2, recuperar el **aviso NHC más reciente**, comprobar alcance exacto de alertas, actualizar textos y material gráfico si los datos cambiaron.
- El contenido no sustituye avisos de evacuación ni alertas locales.

## Descubrimiento y etiquetas

La búsqueda del 11 de octubre encontró `#Simon` en avisos difundidos por Protección Civil y `#Huracán` en comunicación meteorológica. `#KMXRadar` identifica la marca; `#Jalisco` contextualiza geográficamente; `#ProtecciónCivil` alcanza a lectores atentos a alertas y seguridad. No se encontraron datos públicos confiables para atribuirles un volumen exacto de búsquedas o alcance; se prioriza relevancia semántica. Se evitan etiquetas genéricas y potencialmente engañosas.
