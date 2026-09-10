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

En la ventana hay tres casillas, todas marcadas por defecto:

- **Imagen de satélite (Google).**
- **Polígonos:** estado, municipios (con su nombre) y localidades (áreas).
- **Puntos:** localidades, colonias y campus.

Marca lo que quieras y pulsa Ejecutar. Solo se añade lo marcado, siempre
en el mismo orden: puntos arriba, polígonos en medio e imagen al fondo.

## Qué añade

Con las tres casillas marcadas, las capas se añaden en este orden:

| Posición | Capa | Elementos | Estilo |
|---|---|---|---|
| Arriba | Campus (puntos) | 1 | Magenta, 0,5 mm |
| | Colonias (puntos) | 87 | Cian, 0,5 mm |
| | Localidades (puntos) | 8.004 | Rojo, 0,5 mm |
| En medio | Estado (polígono) | 1 | Contorno blanco, sin relleno |
| | Municipios (polígonos) | 43 | Contorno amarillo, sin relleno. Nombres en cursiva de 5 pt, del mismo amarillo, con un halo negro fino |
| | Localidades (áreas) | 63 | Contorno verde, sin relleno |
| Abajo | Google Satellite | | Imagen de fondo |

Todas las capas están recortadas con el límite del estado y se cargan en
**solo lectura**, para no modificar por error los datos del plugin. Si el
proyecto está vacío, el SRC pasa a WGS 84 / UTM zona 14N (EPSG:32614), que
cubre todo el estado, y el mapa se encuadra en Tamaulipas. Si el proyecto
ya tiene capas, no se toca su SRC.

Con 5 puntos, al ver el estado entero QGIS puede ocultar algunos nombres
de municipios para que no se pisen; al acercarse aparecen.

## Datos

- **Who's On First** (https://whosonfirst.org). Es obligatorio enlazar a su
  licencia: https://whosonfirst.org/docs/licenses/. Algunas de sus fuentes
  exigen atribución (por ejemplo, GeoNames y Quattroshapes, CC-BY).
- **Procesado:** todas las capas se recortaron con el límite de Tamaulipas
  de Who's On First. En los polígonos se eliminaron los fragmentos de
  municipios o localidades vecinas con menos del 1 % de su superficie
  dentro del estado (astillas del recorte). SRC: EPSG:32614.
- **Imagen de fondo: Google.** Su uso está sujeto a las condiciones de
  servicio de Google.

## Estado

Experimental. Si encuentras un error, abre un
[issue](https://github.com/adanielibarra/VaquerosGIS/issues).

## Cambios

- **0.1.0:** primera versión.

## Licencia

Código: GPL v3. Ver [LICENSE](LICENSE). Datos: ver la sección Datos.
