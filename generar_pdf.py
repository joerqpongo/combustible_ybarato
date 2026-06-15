#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para generar el PDF del Informe Ejecutivo del Proyecto combustible_ybarato.es
Utiliza la librería ReportLab para dar un formato profesional y académico.
"""

import os
import sys
import subprocess

# Asegurar que reportlab esté instalado
try:
    import reportlab
except ImportError:
    print("La librería 'reportlab' no está instalada. Instalándola automáticamente...")
    subprocess.run([sys.executable, "-m", "pip", "install", "reportlab"])
    import reportlab

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """
    Canvas personalizado para realizar la numeración de páginas en dos pasadas
    y mostrar el formato "Página X de Y" con cabecera y pie de página.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        
        # Omitir cabecera y pie en la primera página (Portada)
        if self._pageNumber == 1:
            self.restoreState()
            return

        # Cabecera
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        self.drawString(54, 800, "INFORME EJECUTIVO: combustible_ybarato.es")
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 792, 558, 792)

        # Pie de página
        self.drawString(54, 40, "© 2026 combustible_ybarato.es — Proyecto Fin de Fase")
        page_str = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(558, 40, page_str)
        self.line(54, 52, 558, 52)
        
        self.restoreState()


def generar_pdf():
    pdf_filename = "informe_ejecutivo.pdf"
    
    # Configurar el documento A4 con márgenes de 2cm
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=A4,
        leftMargin=2*cm,
        rightMargin=2*cm,
        topMargin=2.5*cm,
        bottomMargin=2.5*cm
    )

    styles = getSampleStyleSheet()
    
    # Definición de la paleta de colores premium
    PRIMARY_COLOR = colors.HexColor("#1e3c72")   # Azul marino oscuro
    SECONDARY_COLOR = colors.HexColor("#2a5298") # Azul medio
    TEXT_COLOR = colors.HexColor("#1e293b")      # Gris oscuro/Negro pizarra
    LIGHT_BG = colors.HexColor("#f8fafc")        # Fondo claro
    LINE_COLOR = colors.HexColor("#e2e8f0")      # Color de líneas
    
    # Nuevos estilos tipográficos
    style_normal = ParagraphStyle(
        'TextoNormal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=TEXT_COLOR,
        spaceAfter=8
    )
    
    style_normal_bold = ParagraphStyle(
        'TextoNormalNegrita',
        parent=style_normal,
        fontName='Helvetica-Bold'
    )
    
    style_title = ParagraphStyle(
        'TituloPortada',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=26,
        leading=32,
        textColor=PRIMARY_COLOR,
        alignment=1, # Centrado
        spaceAfter=15
    )
    
    style_subtitle = ParagraphStyle(
        'SubtituloPortada',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=13,
        leading=18,
        textColor=SECONDARY_COLOR,
        alignment=1, # Centrado
        spaceAfter=30
    )
    
    style_h1 = ParagraphStyle(
        'Heading1_Custom',
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=PRIMARY_COLOR,
        spaceBefore=16,
        spaceAfter=10,
        keepWithNext=True
    )
    
    style_h2 = ParagraphStyle(
        'Heading2_Custom',
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=SECONDARY_COLOR,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    
    style_bullet = ParagraphStyle(
        'Bullet_Custom',
        parent=style_normal,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=5
    )

    style_table_header = ParagraphStyle(
        'TableHeader',
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.white
    )

    style_table_cell = ParagraphStyle(
        'TableCell',
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=TEXT_COLOR
    )

    story = []

    # ─── PÁGINA 1: PORTADA ───
    story.append(Spacer(1, 4 * cm))
    # Icono grande de gasolinera
    story.append(Paragraph("<font size=72 color='#2a5298'>⛽</font>", style_title))
    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph("INFORME EJECUTIVO DEL PROYECTO", style_title))
    story.append(Paragraph("<b>combustible_ybarato.es</b><br/>Optimización del Gasto en Carburantes en España mediante Inteligencia de Datos", style_subtitle))
    
    story.append(Spacer(1, 5 * cm))
    
    # Metadatos en la portada
    meta_text = """
    <b>Autor:</b> Jose L. Romero<br/>
    <b>Entidad:</b> ybarato.es<br/>
    <b>Fecha:</b> Junio de 2026<br/>
    <b>Estado del Proyecto:</b> Prototipo Operativo (MVP)<br/>
    <b>Tecnologías:</b> Python, Streamlit, Pandas, Docker, AWS EC2
    """
    story.append(Paragraph(meta_text, ParagraphStyle('Meta', parent=style_normal, alignment=1, fontSize=9.5, leading=14)))
    story.append(PageBreak())

    # ─── PÁGINA 2: ÍNDICE Y DESCRIPCIÓN DEL PROBLEMA ───
    story.append(Paragraph("ÍNDICE DEL INFORME", style_h1))
    
    indice_data = [
        ["1. Descripción del Problema", "Pág. 3"],
        ["   - Contexto del mercado de hidrocarburos", ""],
        ["   - El reto del acceso a la información", ""],
        ["   - La paradoja del desplazamiento inútil", ""],
        ["2. Impacto del Proyecto", "Pág. 4"],
        ["   - Impacto económico (particular y corporativo)", ""],
        ["   - Impacto medioambiental (emisiones de CO2)", ""],
        ["   - Impacto social y de transparencia", ""],
        ["3. Solución Tecnológica Creada", "Pág. 5"],
        ["   - Arquitectura del sistema y flujo de datos", ""],
        ["   - Algoritmo de geolocalización (Fórmula de Haversine)", ""],
        ["   - UX/UI Responsive Premium", ""],
        ["4. Indicadores Clave de Rendimiento (KPIs)", "Pág. 6"],
        ["5. Riesgos y Plan de Mitigación", "Pág. 7"],
        ["6. Plan de Implantación", "Pág. 8"],
    ]
    
    t_indice_data = []
    for item in indice_data:
        t_indice_data.append([
            Paragraph(f"<b>{item[0]}</b>" if not item[0].startswith("  ") else item[0], style_normal),
            Paragraph(f"<b>{item[1]}</b>", ParagraphStyle('Right', parent=style_normal, alignment=2))
        ])
    
    t_indice = Table(t_indice_data, colWidths=[13*cm, 3*cm])
    t_indice.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('TOPPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(t_indice)
    story.append(Spacer(1, 1 * cm))
    
    story.append(Paragraph("1. DESCRIPCIÓN DEL PROBLEMA", style_h1))
    story.append(Paragraph("<b>Contexto del Mercado de Hidrocarburos en España</b>", style_h2))
    story.append(Paragraph(
        "En los últimos años, el precio de los combustibles en España ha experimentado una volatilidad extrema, impulsada por tensiones geopolíticas internacionales y fluctuaciones del barril Brent. A pesar de que el mercado es libre y competitivo, existe una gran dispersión de precios. En un radio de apenas 10 kilómetros, el precio de un mismo tipo de carburante puede variar hasta en un 20% entre diferentes marcas operadoras. Esta asimetría de precios representa un potencial ahorro neto de entre 10 y 15 euros por cada repostaje de un turismo de tamaño medio.",
        style_normal
    ))
    story.append(Paragraph(
        "Para los conductores profesionales, empresas de reparto de última milla y familias de clase trabajadora, esta diferencia no es trivial; constituye un factor determinante en su flujo de caja y costes operativos mensuales.",
        style_normal
    ))
    story.append(PageBreak())

    # ─── PÁGINA 3: DESCRIPCIÓN DEL PROBLEMA (CONT.) Y 2. IMPACTO DEL PROYECTO ───
    story.append(Paragraph("<b>El Reto del Acceso a la Información en Tiempo Real</b>", style_h2))
    story.append(Paragraph(
        "El Ministerio para la Transición Ecológica publica diariamente los precios oficiales de más de 12.000 estaciones de servicio de España a través del Geoportal de Gasolineras. Sin embargo, el acceso móvil a esta plataforma es lento y poco intuitivo, lo que imposibilita la consulta rápida y en tiempo real para usuarios que se encuentran en tránsito por carretera.",
        style_normal
    ))
    story.append(Paragraph("<b>La Paradoja del Desplazamiento Inútil</b>", style_h2))
    story.append(Paragraph(
        "Un error frecuente entre los conductores consiste en desplazarse a gasolineras alejadas motivados por un precio bajo por litro, sin cuantificar matemáticamente si el consumo del trayecto de desvío excede el beneficio monetario directo del repostaje. El proyecto solventa este problema al integrar simultáneamente precio y distancia en la lógica de ordenación.",
        style_normal
    ))
    
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph("2. IMPACTO DEL PROYECTO", style_h1))
    story.append(Paragraph(
        "El proyecto combustible_ybarato.es genera un impacto directo estructurado en tres vertientes:",
        style_normal
    ))
    story.append(Paragraph("• <b>Impacto Económico:</b> Permite un ahorro familiar directo estimado en unos 144 € anuales por vehículo (basado en un consumo promedio anual de 1.200 litros y un ahorro de 0,12 €/Litro). A nivel corporativo, reduce el coste de combustible en flotas logísticas urbanas entre un 6% y un 10%.", style_bullet))
    story.append(Paragraph("• <b>Impacto Medioambiental:</b> Al orientar al usuario con precisión hacia la estación óptima en distancia y precio, se evitan trayectos innecesarios por desvíos redundantes. Esto minimiza las emisiones de CO2 derivadas del tráfico ineficiente.", style_bullet))
    story.append(Paragraph("• <b>Impacto Social y Transparencia:</b> Fomenta la libre competencia en el mercado de hidrocarburos español, otorgando poder de decisión inmediato al usuario y beneficiando indirectamente a las estaciones automatizadas independientes y cooperativas locales.", style_bullet))
    story.append(PageBreak())

    # ─── PÁGINA 4: 3. SOLUCIÓN TECNOLÓGICA CREADA ───
    story.append(Paragraph("3. SOLUCIÓN TECNOLÓGICA CREADA", style_h1))
    story.append(Paragraph(
        "La solución consiste en una aplicación web interactiva responsiva programada enteramente en Python mediante el framework Streamlit, y procesada analíticamente en memoria a través de Pandas.",
        style_normal
    ))
    
    story.append(Paragraph("<b>Arquitectura del Sistema y Flujo de Datos</b>", style_h2))
    story.append(Paragraph(
        "El pipeline de datos está estructurado para operar en tiempo real minimizando las consultas de red:",
        style_normal
    ))
    story.append(Paragraph("1. <b>Ingesta Diaria Condicional:</b> Se conecta con el API de datos del Geoportal Ministerial y descarga el fichero maestro en formato .xls de forma automática una vez al día.", style_bullet))
    story.append(Paragraph("2. <b>Caché Compartida en Memoria:</b> Para evitar la degradación del rendimiento por peticiones concurrentes, el set de datos nacional se almacena en memoria de manera global. La caché se invalida tras las 06:00 AM de cada día, coincidiendo con la actualización de datos ministeriales.", style_bullet))
    story.append(Paragraph("3. <b>Mecanismo de Resiliencia (Offline):</b> Si la descarga directa falla debido a problemas en el servidor gubernamental, la aplicación detecta la anomalía, carga el último fichero almacenado localmente y advierte al usuario, garantizando el 100% de disponibilidad de consulta.", style_bullet))
    story.append(Paragraph("4. <b>Pipeline ETL (Pandas):</b> Se eliminan filas huérfanas o sin coordenadas válidas, se normaliza la codificación UTF-8, y se convierten las comas decimales europeas del Excel a punto de tipo float de alta precisión.", style_bullet))

    story.append(Paragraph("<b>Algoritmo de Distancia (Fórmula de Haversine)</b>", style_h2))
    story.append(Paragraph(
        "El cálculo de la distancia geodésica lineal en km entre la posición GPS de búsqueda y las estaciones de servicio se realiza en memoria aplicando la trigonometría esférica de Haversine:",
        style_normal
    ))
    story.append(Paragraph(
        "<i>Distancia (km) = 2 · R · arcsin( √( sin²(Δlat/2) + cos(lat1)·cos(lat2)·sin²(Δlon/2) ) )</i>",
        ParagraphStyle('Formula', parent=style_normal, fontName='Helvetica-Oblique', alignment=1, textColor=SECONDARY_COLOR)
    ))
    story.append(Paragraph("Donde R = 6371.0 km (Radio de la Tierra). Esta fórmula proporciona un cálculo de distancia eficiente y rápido para el volumen de datos manejado.", style_normal))
    story.append(PageBreak())

    # ─── PÁGINA 5: SOLUCIÓN TECNOLÓGICA (CONT.) Y 4. KPIs ───
    story.append(Paragraph("<b>UX/UI Responsive Premium</b>", style_h2))
    story.append(Paragraph(
        "La interfaz del usuario se ha diseñado de forma limpia y moderna con un tema oscuro que reduce la fatiga visual. Para solventar los problemas de legibilidad típicos en pantallas pequeñas (móviles), se implementó una tipografía fluida escalable usando la propiedad <i>clamp()</i> en CSS. Además, la tabla de resultados HTML está contenida en un bloque responsivo que permite el scroll horizontal fluido sin desestructurar la maquetación. Integra triple posicionamiento: GPS automático mediante el navegador, buscador textual de municipios (geocodificado en la nube mediante Nominatim) y coordenadas de configuración manual.",
        style_normal
    ))
    
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("4. INDICADORES CLAVE DE RENDIMIENTO (KPIS)", style_h1))
    story.append(Paragraph(
        "El éxito operativo y técnico del proyecto se monitorea con los siguientes indicadores métricos clave:",
        style_normal
    ))
    
    # Tabla de KPIs
    kpi_headers = ["Dimensión", "Indicador (KPI)", "Fórmula / Criterio", "Objetivo"]
    kpi_rows = [
        ["Financiera / Ahorro", "Ahorro por Repostaje", "Diferencia €/Litro vs Precio Máx.", ">= 0.10 €/L"],
        ["Financiera / Ahorro", "Ahorro Anual Estimado", "Ahorro acumulado (1.200 L/año)", ">= 120 €/año"],
        ["Técnica / Sistema", "Tiempo de Respuesta", "Petición a renderizado en UI", "< 1.2 seg"],
        ["Técnica / Sistema", "ETL Processing Time", "Lectura y limpieza del XLS", "< 5.0 seg"],
        ["Técnica / Sistema", "Disponibilidad (Uptime)", "Tiempo total operativo online", ">= 99.9%"],
        ["Negocio / Producto", "Tasa de Rebote", "Abandono en los primeros 10s", "< 25%"],
        ["Negocio / Producto", "Conversión a Ruta GPS", "Clic en Google Maps vs Total", ">= 40%"]
    ]
    
    table_content = [[Paragraph(f"<b>{h}</b>", style_table_header) for h in kpi_headers]]
    for row in kpi_rows:
        table_content.append([
            Paragraph(row[0], style_table_cell),
            Paragraph(row[1], style_table_cell),
            Paragraph(row[2], style_table_cell),
            Paragraph(row[3], style_table_cell)
        ])
        
    kpi_table = Table(table_content, colWidths=[3.2*cm, 4*cm, 6.2*cm, 2.6*cm])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY_COLOR),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, LINE_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_BG]),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(kpi_table)
    story.append(PageBreak())

    # ─── PÁGINA 6: 5. RIESGOS Y PLAN DE MITIGACIÓN ───
    story.append(Paragraph("5. RIESGOS Y PLAN DE MITIGACIÓN", style_h1))
    story.append(Paragraph(
        "El correcto funcionamiento a largo plazo de la plataforma requiere mitigar riesgos clave de datos, usabilidad e infraestructura:",
        style_normal
    ))
    
    story.append(Paragraph("<b>1. Riesgo de Caída de los Servidores del Ministerio (Severidad: Alta)</b>", style_h2))
    story.append(Paragraph(
        "<b>Impacto:</b> La imposibilidad de descargar los datos actualizados del Geoportal impediría mostrar precios o estaciones al usuario.",
        style_normal
    ))
    story.append(Paragraph(
        "<b>Mitigación:</b> Implementación de un mecanismo fallback de contingencia. La aplicación cuenta con almacenamiento de respaldo en disco local del último archivo correcto. Si el servidor ministerial falla, el sistema conmuta automáticamente al archivo local y emite un banner informativo de advertencia sin interrumpir el servicio.",
        style_normal
    ))
    
    story.append(Paragraph("<b>2. Riesgo de Modificación Estructural del Archivo Origen (Severidad: Media)</b>", style_h2))
    story.append(Paragraph(
        "<b>Impacto:</b> Si el Ministerio renombra las columnas de precios, coordenadas o cabeceras, el motor analítico de Pandas fallaría durante la carga.",
        style_normal
    ))
    story.append(Paragraph(
        "<b>Mitigación:</b> Se ha diseñado el motor de análisis con tolerancia sintáctica parcial (búsquedas por prefijo, insensibilidad a mayúsculas/minúsculas y strips automatizados). En futuras versiones, se incorporará una biblioteca de validación de esquema como Pydantic que notificará vía logs de incidencias de forma automática.",
        style_normal
    ))
    
    story.append(Paragraph("<b>3. Bloqueo de Ubicación GPS por Navegadores (Severidad: Media)</b>", style_h2))
    story.append(Paragraph(
        "<b>Impacto:</b> La imposibilidad de acceder al sensor GPS nativo del dispositivo del usuario impide una búsqueda de proximidad automática.",
        style_normal
    ))
    story.append(Paragraph(
        "<b>Mitigación:</b> Triple lógica de redundancia en la interfaz de usuario. Al fallar el GPS, la aplicación desvía la experiencia hacia la geocodificación mediante texto a través de Nominatim OpenStreetMap o a las coordenadas manuales por defecto fijadas en Madrid.",
        style_normal
    ))
    story.append(PageBreak())

    # ─── PÁGINA 7: 6. PLAN DE IMPLANTACIÓN Y CRONOGRAMA ───
    story.append(Paragraph("6. PLAN DE IMPLANTACIÓN", style_h1))
    story.append(Paragraph(
        "La puesta en marcha completa y optimización de la aplicación combustible_ybarato.es se divide en seis fases sucesivas a lo largo de un período estimado de seis semanas:",
        style_normal
    ))
    
    implantacion_fases = [
        ["Fase 1: Análisis e Investigación", "5 días", "Estudio de las APIs de origen y viabilidad analítica."],
        ["Fase 2: Diseño de la Solución", "7 días", "Definición del diseño de UI responsivo y estructura lógica."],
        ["Fase 3: Desarrollo del Prototipo", "10 días", "Programación del pipeline ETL y la interfaz interactiva."],
        ["Fase 4: Control de Calidad", "5 días", "Pruebas responsive en móviles (iOS/Android) y tests unitarios."],
        ["Fase 5: Despliegue en Producción", "4 días", "Configuración en AWS EC2, contenerización Docker y SSL Let's Encrypt."],
        ["Fase 6: Operación y SEO", "Continuo", "Monitorización de KPIs, indexación en motores de búsqueda y mejoras."]
    ]
    
    story.append(Spacer(1, 0.2 * cm))
    
    fases_table_data = [[
        Paragraph("<b>Fase del Proyecto</b>", style_table_header),
        Paragraph("<b>Duración</b>", style_table_header),
        Paragraph("<b>Descripción Clave</b>", style_table_header)
    ]]
    
    for fase in implantacion_fases:
        fases_table_data.append([
            Paragraph(fase[0], style_table_cell),
            Paragraph(fase[1], style_table_cell),
            Paragraph(fase[2], style_table_cell)
        ])
        
    fases_table = Table(fases_table_data, colWidths=[5.5*cm, 2.5*cm, 8*cm])
    fases_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), SECONDARY_COLOR),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, LINE_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_BG]),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(fases_table)
    
    story.append(Spacer(1, 0.8 * cm))
    story.append(Paragraph("<b>Estimación Presupuestaria de Lanzamiento (Año 1)</b>", style_h2))
    story.append(Paragraph(
        "El coste proyectado para la construcción, puesta en marcha y mantenimiento durante el primer año se resume en los siguientes puntos principales:",
        style_normal
    ))
    story.append(Paragraph("• <b>Desarrollo de Software y Diseño de UI:</b> 3.500 € (pago único por arquitectura, ETL y diseño responsivo).", style_bullet))
    story.append(Paragraph("• <b>Infraestructura de Servidor VPS (AWS EC2):</b> 180 € / año (gratuitos los primeros meses bajo la capa de uso libre).", style_bullet))
    story.append(Paragraph("• <b>Dominio Web y Certificación SSL:</b> 25 € / año (cifrado obligatorio HTTPS).", style_bullet))
    story.append(Paragraph("• <b>Mantenimiento Correctivo y Adaptaciones:</b> 600 € / año (soporte de APIs y actualizaciones).", style_bullet))
    story.append(Paragraph("• <b>Campaña de Optimización SEO y Lanzamiento:</b> 1.000 € / año.", style_bullet))
    
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("<b>Inversión Total Estimada Año 1: 5.305 €</b>", style_normal_bold))
    story.append(Paragraph("El coste mensual recurrente del servicio a partir del segundo año se estabiliza en aproximadamente 80 €/mes para cubrir servidores de bajo consumo y tareas básicas de mantenimiento correctivo.", style_normal))

    # Construir el PDF
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"El informe ejecutivo en PDF se ha generado correctamente como '{pdf_filename}'.")

if __name__ == "__main__":
    generar_pdf()
