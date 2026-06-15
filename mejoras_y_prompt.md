# PROPUESTAS DE MEJORA Y PROMPT IDEAL PARA EL PROYECTO
**combustible_ybarato.es — Optimización de Desarrollo**

Este documento detalla las mejoras funcionales sugeridas para llevar el prototipo actual a un nivel comercial avanzado y proporciona un **Prompt Ideal** optimizado para instruir a una Inteligencia Artificial a realizar la actualización del código de `app.py` de forma limpia y directa.

---

## 1. PROPUESTAS DE MEJORA SUGERIDAS

A partir del análisis técnico del prototipo actual, se identifican las siguientes áreas clave de mejora para enriquecer el valor aportado al usuario:

### A. Cálculo del "Ahorro Real" Neto (Evaluación de Desvío)
*   **Problema:** El usuario ve las gasolineras ordenadas por precio, pero ir a la más barata (p.ej. a 8 km) puede consumir más combustible de lo que se ahorra en el repostaje en comparación con una a 2 km.
*   **Mejora:** Introducir una calculadora interactiva en la barra lateral donde el usuario ingrese:
    1.  **Capacidad de repostaje estimada** (en Litros, ej: 50 L).
    2.  **Consumo medio del vehículo** (L/100km, ej: 6.5 L/100km).
*   **Algoritmo:** Calcular para cada estación el "Ahorro Neto Real" en euros considerando el coste de ida y vuelta:
$$\text{Coste del Desplazamiento (€)} = \frac{2 \cdot \text{Distancia (km)} \cdot \text{Consumo (L/100km)}}{100} \cdot \text{Precio Combustible (€/L)}$$
$$\text{Ahorro Neto Real (€)} = (\text{Precio Máximo Zona} - \text{Precio Estación}) \cdot \text{Litros} - \text{Coste del Desplazamiento}$$
*   **Valor:** El listado se ordenaría por este **Ahorro Neto Real**, mostrando en verde si compensa el viaje o en rojo si se pierde dinero por el desplazamiento.

### B. Análisis Predictivo e Historial de Precios
*   **Problema:** La aplicación solo conoce el precio del día actual. El usuario no sabe si es mejor repostar hoy o esperar a mañana.
*   **Mejora:** Almacenar de forma automatizada las lecturas diarias en una base de datos ligera (SQLite o archivos parquet históricos en el servidor).
*   **Valor:** Mostrar una pequeña gráfica de tendencia de los últimos 15 días en la zona y un indicador predictivo: *"Te recomendamos repostar hoy: los precios han subido un 2% esta semana y la tendencia sigue al alza"* o *"Espera al lunes: históricamente es el día con precios más bajos en esta provincia"*.

### C. Alertas de Precios en Canales de Mensajería (Telegram / Email)
*   **Problema:** El usuario debe entrar activamente a la web para buscar el precio.
*   **Mejora:** Integrar un webhook sencillo con un Bot de Telegram o servicio de email (SendGrid).
*   **Valor:** El usuario se suscribe a una zona y recibe una alerta automática: *"El precio del Gasóleo A ha bajado de 1.350 €/L en tu zona habitual (Sevilla Centro). ¡Es buen momento para repostar!"*.

### D. Interfaz Gráfica Avanzada (Persistencia de Preferencias)
*   **Problema:** Cada vez que el usuario refresca la página, debe volver a configurar su tipo de combustible, el radio y su ubicación.
*   **Mejora:** Guardar la configuración en los parámetros de la URL de Streamlit (`st.query_params`) o localmente mediante `LocalStorage` en el navegador.
*   **Valor:** La próxima vez que abra `combustible_ybarato.es`, la aplicación cargará instantáneamente su configuración preferida.

---

## 2. PROMPT IDEAL PARA HACERLO MEJOR

A continuación, se presenta el **Prompt de Ingeniería** diseñado para ser suministrado a una IA de código (como Gemini, Claude, etc.) para que implemente las mejoras de la calculadora de desvío y la persistencia de configuración de manera profesional:

```markdown
Actúa como un desarrollador experto en Python, Streamlit y análisis de datos con Pandas. Necesito mejorar la funcionalidad del archivo `app.py` de nuestro proyecto de buscador de gasolineras baratas en España.

El código actual descarga datos oficiales de Geoportal de Gasolineras en formato XLS, calcula distancias lineales con la fórmula de Haversine y muestra una tabla interactiva y un mapa Pydeck.

Quiero implementar dos mejoras específicas de forma limpia, robusta y con un diseño estético premium:

### MEJORA 1: Calculadora de Ahorro Neto Real (Compensación de Desvío)
1. En la barra lateral (sidebar), añade una sección interactiva llamada "🚗 Parámetros de tu Vehículo".
2. Añade un slider para "Consumo medio (L/100km)" con un rango de 3.0 a 15.0 (por defecto 6.0, paso 0.1).
3. Añade un slider para "Volumen a repostar (Litros)" con un rango de 10 a 100 (por defecto 50, paso 5).
4. En la lógica de filtrado de estaciones (dentro del dataframe de resultados):
   - Calcula el coste de desplazamiento de ida y vuelta para cada gasolinera en euros: 
     CosteDesplazamiento = (2 * Distancia_KM * Consumo_L100km / 100) * Precio_Combustible
   - Calcula el Ahorro Bruto en euros tomando el precio más alto encontrado en la zona como referencia de "no optimizado":
     AhorroBruto = (Precio_Max_Zona - Precio_Combustible) * Litros_A_Repostar
   - Calcula el Ahorro Neto Real en euros:
     AhorroNeto = AhorroBruto - CosteDesplazamiento
5. En la tabla de resultados HTML final:
   - Añade una nueva columna llamada "Ahorro Neto (€)".
   - Formatea el valor con 2 decimales y añade el símbolo €.
   - Si el Ahorro Neto es positivo (> 0 €), píntalo en color verde (ej: #6ee7b7). Si es negativo (<= 0 €), píntalo en color rojo suave (ej: #fca5a5) para indicar al usuario que no le compensa el desvío.
6. Permite que en el selector de ordenación lateral el usuario pueda elegir ordenar por: "Ahorro Neto (más ahorro primero)".

### MEJORA 2: Persistencia de Filtros y Configuración
1. Modifica la inicialización de los widgets (combustible, radio, consumo, litros y ordenación) utilizando `st.query_params` para que se sincronicen con la URL.
2. Si el usuario accede a la web con parámetros en la URL (ej: ?combustible=Gasoleo+A&radio=15), los inputs de Streamlit deben inicializarse con esos valores automáticamente.
3. Si el usuario modifica los inputs, la aplicación debe actualizar los `st.query_params` dinámicamente para permitir compartir búsquedas concretas con un enlace copiado.

### REQUISITOS DE CÓDIGO:
- Mantén la arquitectura y modularidad existente en `app.py`.
- No elimines los estilos CSS personalizados ni el mapa de Pydeck.
- Asegúrate de controlar posibles errores de división por cero y valores NaN.
- Retorna el código completo listo para sustituir el archivo `app.py`.
```

---

## 3. INSTRUCCIONES DE APLICACIÓN

Para implementar estas mejoras en tu entorno de desarrollo, sigue estos pasos:

1.  **Copia el prompt completo** de la sección anterior.
2.  **Pégalo en tu asistente de programación de confianza** (Gemini, Claude, etc.) junto con el contenido del archivo [app.py](file:///c:/Users/JoseLuisRomero/OneDrive%20-%20GASTON%20Y%20DANIELA/_Made%20with%20IA/combustible_ybarato.es/app.py) como contexto.
3.  El asistente generará la versión optimizada del código que integra la calculadora financiera de desvío y la persistencia de URL.
4.  Reemplaza el contenido de `app.py` y reinicia tu servidor Streamlit en producción para ver los cambios aplicados en tiempo real.
