# ⛽ Instrucciones completas del Proyecto: combustible_ybarato.es

Este documento contiene toda la información técnica, lógica de negocio y directrices de diseño necesarias para construir desde cero la aplicación **combustible_ybarato.es**. Está diseñado para ser leído y comprendido fácilmente tanto por programadores humanos como por Modelos de Inteligencia Artificial (I.A.).

---

## 1. Descripción General del Proyecto
**combustible_ybarato.es** es una aplicación interactiva desarrollada en **Python** utilizando el framework **Streamlit**. Su objetivo es permitir a los usuarios encontrar las gasolineras más baratas de España en un radio de búsqueda seleccionado a partir de su ubicación. 

La aplicación debe ser completamente **responsive** y compatible visualmente con ordenadores personales (PC), ordenadores portátiles, tablets y teléfonos móviles.

---

## 2. Origen y Estructura de los Datos

*   **Fuente Oficial:** Los datos se obtienen del Geoportal de Gasolineras del Ministerio para la Transición Ecológica de España.
*   **Fichero de Datos:** Hoja de cálculo de Excel en formato `.xls` obtenida de:
    `https://geoportalgasolineras.es/geoportal/resources/files/preciosEESS_es.xls`
*   **Actualización y Caché:**
    *   Los datos se almacenan localmente en `preciosEESS_es.xls`.
    *   Debe existir un mecanismo de caché diaria. Los datos se descargan automáticamente una sola vez al día si son más antiguos de las **06:00 AM** del día en curso.
    *   Si la descarga online falla, la aplicación debe intentar utilizar el archivo local existente y mostrar un mensaje de advertencia.
*   **Estructura del Excel:**
    *   La cabecera real de los datos comienza en la **fila 4** (índice `3` en Pandas).
    *   Las columnas de coordenadas se llaman `"Latitud"` y `"Longitud"`.
    *   Las columnas de precios comienzan con el prefijo `"Precio"`.
*   **Limpieza de Datos:**
    *   Los separadores decimales de la fuente original utilizan coma (`,`). Deben convertirse a punto (`.`) y convertirse a tipo flotante (`float`).
    *   Se deben descartar todas las filas que no contengan valores válidos para Latitud (rango -90 a 90) y Longitud (rango -180 a 180).
    *   Para filtrar, se omiten precios nulos o iguales a `0`.

---

## 3. Lógica de Negocio y Algoritmos

### A. Cálculo de Distancia (Fórmula de Haversine)
Para calcular la distancia en kilómetros entre la ubicación del usuario $(lat_1, lon_1)$ y una gasolinera $(lat_2, lon_2)$, se utiliza la fórmula de Haversine:
$$R = 6371.0\text{ km (Radio de la Tierra)}$$
$$\Delta lat = lat_2 - lat_1,\quad \Delta lon = lon_2 - lon_1$$
$$a = \sin^2\left(\frac{\Delta lat}{2}\right) + \cos(lat_1) \cdot \cos(lat_2) \cdot \sin^2\left(\frac{\Delta lon}{2}\right)$$
$$\text{Distancia} = R \cdot 2 \cdot \arcsin(\sqrt{a})$$

### B. Criterio de Búsqueda y Ordenación (Multinivel)
El usuario puede filtrar las gasolineras especificando un **Radio de búsqueda (en km)** y un **Límite máximo de resultados**. Los resultados se ordenan en base a dos criterios seleccionables:

1.  **Ordenar por Precio (Opción por defecto):**
    *   **Criterio Primario:** Precio del combustible seleccionado (de más barato a más caro).
    *   **Criterio Secundario (desempate):** Distancia calculada en kilómetros (de más cercana a más lejana).
2.  **Ordenar por Distancia:**
    *   **Criterio Primario:** Distancia calculada en kilómetros (de más cercana a más lejana).
    *   **Criterio Secundario (desempate):** Precio del combustible seleccionado (de más barato a más caro).

---

## 4. Interfaz de Usuario y Experiencia Visual (UX/UI)

La aplicación utiliza un diseño premium, moderno y dinámico con las siguientes pautas visuales:

### A. Sistema de Diseño (CSS Personalizado)
*   **Tipografía:** Fuente **Inter** importada desde Google Fonts para toda la aplicación.
*   **Fondo:** Gradiente oscuro y moderno: `linear-gradient(135deg, #0f0c29 0%, #1a1a3e 50%, #0d0d2b 100%)`.
*   **Hero Header (Cabecera):** Un contenedor llamativo en la parte superior con un gradiente vibrante (`#1e3c72` a `#6a3093`) y una tipografía clara que destaca el nombre del buscador.
*   **Metric Cards (Tarjetas de resumen):** Cuatro tarjetas con efecto de desenfoque de fondo (*glassmorphism*), sombras suaves, y efectos de transformación al pasar el cursor (microanimación hover: desplazamiento de `3px` hacia arriba).
*   **Botones:** Gradiente estilizado entre `#667eea` y `#764ba2`, con esquinas redondeadas y microanimaciones de sombreado en hover.

### B. Responsividad y Adaptabilidad (PC, Portátil, Tablet y Móvil)
*   **Tamaño de Texto Fluido (`clamp`):** Los textos del título principal (`hero-header h1`) y las métricas (`metric-card .value`) utilizan la función `clamp()` en CSS para escalar dinámicamente según el tamaño de la pantalla. Evita que los textos colapsen en teléfonos pequeños.
*   **Tabla de Resultados:** La tabla de resultados debe renderizarse en HTML. Para evitar que la tabla rompa el diseño responsivo del móvil debido a su cantidad de columnas, se envuelve en un contenedor `.table-container` con la propiedad `overflow-x: auto;` y las celdas tienen `white-space: nowrap;`. Esto permite que la tabla sea legible mediante un deslizamiento horizontal limpio en móviles.
*   **Media Queries (@media):** Para pantallas con un ancho inferior a `768px` (tablets y móviles):
    *   Se reduce el padding del *Hero Header* y de las *Metric Cards* para ahorrar espacio en la pantalla vertical.
    *   La barra lateral de Streamlit se oculta automáticamente bajo un botón de hamburguesa nativo.

---

## 5. Arquitectura y Componentes de la Interfaz

### A. Barra Lateral (Configuración)
1.  **Tipo de combustible:** Selector (`st.selectbox`) mapeado a las columnas del Excel (Gasolina 95 E5, Gasóleo A, Gasolina 98, Gasóleo Premium, Gases licuados, etc.).
2.  **Radio de búsqueda (km):** Control deslizante (`st.slider`) de 1 a 50 km (valor predeterminado: 10 km).
3.  **Límite de resultados:** Control deslizante (`st.slider`) de 10 a 100 (valor predeterminado: 25).
4.  **Ordenar resultados por:** Selector (`st.selectbox`) con las opciones de ordenación (Precio o Distancia).
5.  **Ubicación del usuario:** Selector de método con tres opciones:
    *   *Automática (GPS):* Intenta obtener la geolocalización del navegador usando `streamlit-js-eval`. Si no está disponible, utiliza por defecto las coordenadas de la Puerta del Sol, Madrid (Lat: `40.4168`, Lon: `-3.7038`).
    *   *Buscar ciudad:* Caja de texto para ingresar un municipio que se geocodifica mediante la API pública de **Nominatim** (OpenStreetMap).
    *   *Coordenadas manuales:* Dos campos numéricos para Latitud y Longitud.
6.  **Actualizar Datos:** Botón para borrar la caché y forzar la descarga de los precios actualizados.
7.  **Estado de los Datos:** Caja informativa con la fecha de la última actualización y el volumen total de gasolineras en la base de datos nacional.

### B. Panel Principal
1.  **Hero Header:** Logotipo y título explicativo.
2.  **Tarjetas Métricas:** Cuatro bloques superiores:
    *   *Precio más bajo:* El menor precio encontrado dentro del radio.
    *   *Precio medio:* Media aritmética de los resultados devueltos.
    *   *Precio más alto:* El precio más elevado dentro de la muestra.
    *   *Gasolineras encontradas:* Cantidad de gasolineras filtradas que cumplen las condiciones.
3.  **Tabla de Resultados:** Tabla HTML responsiva con las columnas: Rótulo de la Gasolinera, Dirección, Municipio, Provincia, Precio en €/L, Distancia en km, Horario de apertura, y un botón/enlace interactivo de Google Maps que abre las coordenadas en una pestaña nueva (`https://www.google.com/maps/search/?api=1&query={lat},{lon}`).
4.  **Gráfico Comparativo:** Un gráfico de barras (`st.bar_chart`) que compare los precios de las estaciones encontradas.
5.  **Mapa de Estaciones:** Un mapa interactivo (`st.map`) que sitúe geográficamente los resultados en un mapa dinámico con zoom automático.
6.  **Pie de página:** Sección de créditos oficiales con enlace al Geoportal de Gasolineras del Ministerio.

---

## 6. Stack Tecnológico y Requisitos
*   **Lenguaje:** Python 3.9 o superior.
*   **Dependencias principales (`requirements.txt`):**
    *   `streamlit` (Interfaz de usuario)
    *   `pandas` (Procesamiento de datos)
    *   `requests` (Descarga del fichero Excel y geocodificación)
    *   `xlrd` (Motor de lectura para ficheros Excel `.xls` antiguos)
    *   `streamlit-js-eval` (Geolocalización del cliente, opcional)
