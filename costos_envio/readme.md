
## costo_envio_gbp.py


Trae un listado de publicaciones de Mercado Libre con sus costos de envío promedio (el costo de envío que informa ML en cada publicación) para importar en GBP (Global Blue Point) y suma ese costo al precio de venta, si aplica en base a las reglas que configuramos.
 
Hay configuraciones que permiten determinar de qué publicaciones calcular el costo de envío, y en base a qué coeficiente.

Para esto se configura un listado de proveedores de productos que queremos afectar, y también distintos umbrales y coeficientes para calcular el costo de envío a agregar al precio.

Las configuraciones se hacen en envio_config.py

El script asume que todas las publicaciones de una tienda que estén activas en Mercado Libre están importadas a GBP (hay otro script que controla eso) y genera un excel para importar con las publicaciones que tienen cargado un costo distinto al calculado.
 
Una vez que importamos el excel a GBP, se va actualizando automáticamente el precio publicado en Mercado Libre.

## envio_config.py
Este archivo configura constantes relacionadas con envíos que se usan en varios scripts.

- **LISTA_TIENDAS** = ["tecnorium", "lenovo"]
Configura en qué tiendas busca costos de envío.

- **ALIAS_PROVEEDORES_CON_COSTO_ENVIO** = ["microglobal", "bowie"]
Configura a los productos de qué proveedores les vamos a agregar el costo de envío.

- **MAP_PROVEEDORES** =  {"microglobal":  {"name": "MICROGLOBALA RGENTINA SOCIEDAD",  "pid": "16", "umbrales":   {90000: 1, 1200000: 0.5}}, "bowie": {"name": "Bowie SRL", "pid": "79", "umbrales":   {90000: 1, 1200000: 0.5}}}
Configura, para cada proveedor, alias, nombre (como aparece en GBP), id de proveedor en GBP, y los distintos umbrales.

Cada umbral tiene un precio y un coeficiente. El cálculo de envío va a tomar el coeficiente del umbral que más se acerque al precio de venta superándolo.
Por ej, para un producto del proveedor "microglobal" que se venda por $95000 (mayor a 90000 y menor a 120000), según el mapa del ejemplo va a tomar un coeficiente de 0.5. Si tuviera un precio de 
$89000, tomaría el coeficiente 1.
 
El coeficiente determina directamente por cuánto se multiplica el costo de envío que se trae de Mercado Libre.
Con coeficiente 1, se va a sumar la totalidad del costo de envío al precio de venta.
Con coeficiente 0.5, se va a sumar el 50% del costo de envío al precio de venta.

- **DATA_DIR_REL_PATH** = ".."
Configura a qué distancia están los scripts del directorio raíz.
Esto lo usa para poder llegar de forma relativa al directorio "data" donde se alojan db, excel y otra data.
Por lo general, todos los scripts van a estar a un directorio de distancia del raíz, que es el mismo nivel donde se cuenta el directorio "data".

- **DATA_DIR_NAME** = "data"
Nombre del directorio "data"

- **PUBLIS_GBP_SOURCE_FILE** = "Publis_GBP.xlsx"
Configura el nombre del archivo con PUBLIS_GBP

- **ARTICULOS_GBP_EXTENDIDA** = "Articulos_GBP_extendida.xlsx"
Configura el nombre del archivo con ARTICULOS GBP EXTENDIDA

- **MS_SHIPMENT_MULTIPLIER**  = 2
Configura el coeficiente que se aplica al cálculo del costo de envío de Mercado Shops respecto del costo de envío de Mercado Libre. 


#### Configuración del excel que generamos:  
Tiene que ser compatible con el formato que acepta GBP!
Actualmente está configurado en base al formato v18 de GBP.
La versión del formato así como la importación del archivo que generamos, se encuentran en GBP en esta ubicación:
MercadoLibre > Publicaciones > Gestionar Publicaciones > Procesos Disponibles (debajo del listado de publicaciones) > Actualizar masivamente el estado de publicaciones y tipo de publicación mediante Excel©


    - GBP_UPDATER_FILE = "actualizador_publis_gbp.xlsx"
    Nombre del archivo que generamos.

    - GBP_UPDATER_FILE_TITLE_CELLS = {"A1": "ID de Publicación", "B1": "Costo de Envío"}
    Nombre de las columnas que vamos a poner en la fila 1 del excel.

    - GBP_UPDATER_FILE_SHEET_TITLE = "Publicaciones"
    Nombre de la hoja de cálculo donde va el listado de publicaciones.

    - GBP_UPDATER_FILE_COLUMNS_WIDTH = 18
    Ancho de las columnas. Esto no es importante, sólo para practicidad a la hora de controlar el contenido.

- **SHIPMENT_TYPES_CATALOG**  
Configura el catálogo de tipos de envío de ML para calcular el costo de envío de referencia.
Con priority >= 50 se toma directamente el costo de envío, con menos, se promedia el costo de todas las prioridades => 0

## recolectar_tipos_envio_ml.py
 
 Este script releva los distintos tipos de envío disponibles en ML para todas las publicaciones activas de las tiendas que especifiquemos y si encuentra algún tipo de envío que no tengamos catalogado en SHIPMENT_TYPES_CATALOG (en envio_config.py), lo lista para que lo agreguemos manualmente al catálogo así lo usa para calcular el costo de envío de referencia.