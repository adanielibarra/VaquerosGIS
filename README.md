# VaquerosGIS

**Cartografía base de proyectos GIS en el estado de Tamaulipas.**

Plugin de QGIS con una base cartográfica de Tamaulipas (México) lista para
trabajar.

Desarrollado en la **Facultad de Ingeniería y Ciencias (FIC)** de la
**Universidad Autónoma de Tamaulipas (UAT)** por **Daniel Ibarra Marinas**
y **Ana Mónica de Jhesú García (Vienna)**.

## Para qué sirve

Para empezar un proyecto en Tamaulipas sin perder tiempo buscando,
recortando y dando estilo a las capas de referencia. Añade al proyecto
actual un grupo "Tamaulipas" con todo preparado.

## Cómo se usa

Se abre desde tres sitios, y los tres llevan a la misma ventana:

- **Caja de herramientas de Processing:** VaquerosGIS →
  Cartografía base → VaquerosGIS.
- **Botón** con el logo de la FIC en la barra de herramientas de
  complementos.
- **Menú Complementos** → VaquerosGIS → VaquerosGIS.

En la ventana hay cinco casillas. Todas vienen marcadas salvo la de relieve:

- **Imagen de satélite (Google).**
- **Relieve:** modelo digital de elevaciones con sombreado. Viene
  desmarcada porque, dentro del estado, tapa la imagen de satélite.
- **Polígonos:** estado, municipios (con su nombre) y localidades (áreas).
- **Distritos de riego:** los 7 de Tamaulipas.
- **Puntos:** localidades, colonias y campus.

Marca lo que quieras y pulsa Ejecutar. Solo se añade lo marcado, siempre
en el mismo orden: puntos arriba, polígonos en medio, relieve debajo e
imagen al fondo.

## Qué añade

Con todas las casillas marcadas, las capas se añaden en este orden:

| Posición | Capa | Elementos | Estilo |
|---|---|---|---|
| Arriba | Campus (puntos) | 1 | Magenta, 0,5 mm |
| | Colonias (puntos) | 87 | Cian, 0,5 mm |
| | Localidades (puntos) | 8.004 | Rojo, 0,5 mm |
| En medio | Estado (polígono) | 1 | Contorno blanco, sin relleno |
| | Municipios (polígonos) | 43 | Contorno amarillo, sin relleno. Nombres en cursiva de 8 pt, del mismo amarillo, con un halo negro fino |
| | Localidades (áreas) | 63 | Contorno verde, sin relleno |
| | Distritos de riego | 7 | Azul celeste, trama rayada a 45° y contorno del mismo color |
| Debajo | Sombreado | | Multidireccional, mezclado por multiplicación (opacidad 55 %) |
| | Elevación (m) | | Tintas hipsométricas suaves, de verde a ocre y blanco |
| Abajo | Google Satellite | | Imagen de fondo |

Todas las capas están recortadas con el límite del estado y se cargan en
**solo lectura**, para no modificar por error los datos del plugin. Si el
proyecto está vacío, el SRC pasa a WGS 84 / UTM zona 14N (EPSG:32614), que
cubre todo el estado, y el mapa se encuadra en Tamaulipas. Si el proyecto
ya tiene capas, no se toca su SRC.

### Distritos de riego

Son los 7 distritos de riego de Tamaulipas según CONAGUA. Traen, entre
otros, estos campos del año agrícola 2016-2017: `id_dr` (clave), `nom_dr`
(nombre), `num_usu` (usuarios), `sup_tot` (superficie total), `sup_rasup`,
`sup_rasub` y `sup_rtot` (superficie regada con agua superficial,
subterránea y total), y `vol_asup`, `vol_asub` y `vol_atot` (volúmenes de
agua). Las unidades no vienen en la fuente; por las cifras, las superficies
parecen hectáreas (sin confirmar con CONAGUA). Los nombres se
dejan tal como vienen en la fuente (por ejemplo, "Xicotencatl" y "Animas",
sin tilde).

Se cargan **con su geometría oficial, sin recortar**. Casi todos caen
enteros dentro del estado; la excepción es el 050 Acuña Falcón, con solo el
65 % dentro.

**Ojo con las superficies.** El área del polígono no coincide con el campo
`sup_tot` de la propia fuente:

| Distrito | Área del polígono (ha) | `sup_tot` | Dentro de Tamaulipas |
|---|---|---|---|
| 002 Mante | 20.194 | 16.767 | 100 % |
| 025 Bajo Río Bravo | 255.163 | 201.431 | 99,9 % |
| 026 Bajo Río San Juan | 85.416 | 75.901 | 100 % |
| 029 Xicoténcatl | 27.997 | 23.673 | 100 % |
| 050 Acuña Falcón | 31.601 | 14.036 | 65 % |
| 086 Soto la Marina | 42.754 | 35.925 | 100 % |
| 092A Río Pánuco, Unidad Ánimas | 56.835 | 41.526 | 100 % |

El polígono marca el perímetro del distrito, que probablemente incluye
superficie sin derecho a riego (poblaciones, caminos, canales). Para
superficies, usa los atributos, no el área del polígono.

### Relieve

Modelo digital de elevaciones (MDE) de Tamaulipas, ya recortado con el
estado:

| Dato | Valor |
|---|---|
| Fuente | sin determinar |
| SRC | EPSG:32614 |
| Resolución | 84 × 92 m (píxeles no cuadrados, habitual al reproyectar un MDE de 3 segundos de arco) |
| Alturas | de −15 a 3.503 m; la mitad del estado está por debajo de 133 m |
| Archivo | GeoTIFF en teselas, comprimido sin pérdida (DEFLATE), con pirámides, 7,6 MB |

Se carga en dos capas del mismo archivo: **Elevación (m)**, con tintas
hipsométricas suaves, y **Sombreado**, un sombreado multidireccional que
se mezcla por multiplicación sobre los colores. Ambas se suavizan con
remuestreo bilineal. Colores, opacidad y exageración vertical están al
principio de `loader.py`.

Avisos:

- Hay un 4 % de píxeles bajo 0 m, sobre todo en la costa y la Laguna
  Madre. Es normal en estos modelos y no son necesariamente errores, pero
  no son profundidades.
- A esta resolución, y con los errores verticales habituales de varios
  metros, el MDE sirve como base general del estado, **no para estudios
  costeros** de playas o dunas.

Al ver el estado entero, QGIS puede ocultar algunos nombres
de municipios para que no se pisen; al acercarse aparecen.

## Datos

- **Who's On First** (https://whosonfirst.org). Es obligatorio enlazar a su
  licencia: https://whosonfirst.org/docs/licenses/. Algunas de sus fuentes
  exigen atribución (por ejemplo, GeoNames y Quattroshapes, CC-BY).
- **Procesado:** todas las capas se recortaron con el límite de Tamaulipas
  de Who's On First. En los polígonos se eliminaron los fragmentos de
  municipios o localidades vecinas con menos del 1 % de su superficie
  dentro del estado (astillas del recorte). SRC: EPSG:32614.
- **Relieve:** fuente del modelo digital de elevaciones sin determinar.
  Recortado con el estado y comprimido sin pérdida.
- **Distritos de riego:** Comisión Nacional del Agua (CONAGUA), a través
  del servicio INFOTECA de SEMARNAT
  (`geomatica.semarnat.gob.mx/arcgis/rest/services/INFOTECA/Agua`, capa
  "Distritos de Riego"), año agrícola 2016-2017. Descargado en WGS 84 y
  reproyectado a EPSG:32614.
- **Imagen de fondo: Google.** Su uso está sujeto a las condiciones de
  servicio de Google.

## Estado

Experimental. Si encuentras un error, abre un
[issue](https://github.com/adanielibarra/VaquerosGIS/issues).

## Cambios

- **0.1.1:** relieve (modelo digital de elevaciones con sombreado), en
  su propia casilla; los 7 distritos de riego de Tamaulipas (CONAGUA), en azul
  celeste con trama rayada y con su propia casilla;
  nombres de los municipios a 8 pt.
- **0.1.0:** primera versión.

## Licencia

Código: GPL v3. Ver [LICENSE](LICENSE). Datos: ver la sección Datos.
