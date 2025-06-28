import streamlit as st
import pdfplumber
from utils.extraccion import extract_datos_pulmonar
from utils.analisis_gli import analizar_espirometria, analizar_dlco, analizar_volumenes, generar_interpretacion_general, calcular_valor_esperado_fev1, calcular_valor_esperado_fvc, interpretar_z_score_con_severidad, calcular_z_score
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import hashlib
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import io
import base64
from patrones_functions import (
    mostrar_deteccion_patrones, 
    procesar_multiples_pdfs, 
    mostrar_comparacion_temporal,
    mapear_claves_pre
)

st.set_page_config(
    page_title="PulmoReport AI - Dashboard",
    page_icon="🫁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configurar el tema personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .traffic-light {
        display: inline-block;
        width: 20px;
        height: 20px;
        border-radius: 50%;
        margin-right: 10px;
    }
    .green { background-color: #28a745; }
    .yellow { background-color: #ffc107; }
    .red { background-color: #dc3545; }
    .gray { background-color: #6c757d; }
    .dashboard-metric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .status-normal { border-left: 4px solid #28a745; }
    .status-warning { border-left: 4px solid #ffc107; }
    .status-critical { border-left: 4px solid #dc3545; }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">🫁 PulmoReport AI - Dashboard</h1>', unsafe_allow_html=True)
st.markdown('**Análisis Inteligente de Funcionalismo Pulmonar con Dashboard Avanzado**')
st.markdown('*Extracción automática, análisis GLI, interpretación visual y métricas en tiempo real*')

# Botón para limpiar todo el contenido
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("🗑️ Limpiar análisis previo", use_container_width=True, key="clear_analysis"):
        st.rerun()

uploaded_files = st.file_uploader('Sube uno o varios archivos PDF de informes de funcionalismo pulmonar', type='pdf', accept_multiple_files=True)

def crear_metricas_dashboard(datos, resultados_espiro, resultados_dlco, resultados_vol):
    """
    Crea métricas clave para el dashboard overview
    """
    metricas = {}
    
    # Métricas de espirometría
    if resultados_espiro:
        fev1_z = resultados_espiro.get('FEV1', {}).get('z_score', 0)
        fvc_z = resultados_espiro.get('FVC', {}).get('z_score', 0)
        
        # Peor z-score de espirometría
        z_scores_espiro = [fev1_z, fvc_z]
        peor_z_espiro = min(z_scores_espiro) if z_scores_espiro else 0
        
        metricas['peor_z_espiro'] = peor_z_espiro
        metricas['fev1_z'] = fev1_z
        metricas['fvc_z'] = fvc_z
    
    # Métricas de DLCO
    if resultados_dlco:
        dlco_z = resultados_dlco.get('DLCO', {}).get('z_score', 0)
        kco_z = resultados_dlco.get('KCO', {}).get('z_score', 0)
        va_z = resultados_dlco.get('VA', {}).get('z_score', 0)
        
        metricas['dlco_z'] = dlco_z
        metricas['kco_z'] = kco_z
        metricas['va_z'] = va_z
        metricas['peor_z_dlco'] = min([dlco_z, kco_z, va_z]) if [dlco_z, kco_z, va_z] else 0
    
    # Métricas de volúmenes
    if resultados_vol:
        tlc_z = resultados_vol.get('TLC', {}).get('z_score', 0)
        vc_z = resultados_vol.get('VC', {}).get('z_score', 0)
        rv_z = resultados_vol.get('RV', {}).get('z_score', 0)
        rv_tlc_z = resultados_vol.get('RV/TLC', {}).get('z_score', 0)
        
        metricas['tlc_z'] = tlc_z
        metricas['vc_z'] = vc_z
        metricas['rv_z'] = rv_z
        metricas['rv_tlc_z'] = rv_tlc_z
        metricas['peor_z_vol'] = min([tlc_z, vc_z, rv_z, rv_tlc_z]) if [tlc_z, vc_z, rv_z, rv_tlc_z] else 0
    
    # Métricas generales
    todos_z_scores = []
    if 'peor_z_espiro' in metricas:
        todos_z_scores.append(metricas['peor_z_espiro'])
    if 'peor_z_dlco' in metricas:
        todos_z_scores.append(metricas['peor_z_dlco'])
    if 'peor_z_vol' in metricas:
        todos_z_scores.append(metricas['peor_z_vol'])
    
    metricas['peor_z_global'] = min(todos_z_scores) if todos_z_scores else 0
    
    # Contar parámetros anormales
    parametros_anormales = sum(1 for z in todos_z_scores if z < -1.64)
    metricas['parametros_anormales'] = parametros_anormales
    metricas['total_parametros'] = len(todos_z_scores)
    
    # Porcentaje de anormalidad
    if metricas['total_parametros'] > 0:
        metricas['porcentaje_anormalidad'] = (parametros_anormales / metricas['total_parametros']) * 100
    else:
        metricas['porcentaje_anormalidad'] = 0
    
    return metricas

def mostrar_dashboard_overview(metricas):
    """
    Muestra el dashboard overview con métricas clave
    """
    st.markdown("## 📊 Dashboard Overview")
    
    # Primera fila de métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Peor Z-score global
        color = "green" if metricas['peor_z_global'] >= -1.64 else "orange" if metricas['peor_z_global'] >= -2.5 else "red"
        st.markdown(f"""
        <div class="dashboard-metric status-{color}">
            <div class="metric-value">{metricas['peor_z_global']:.2f}</div>
            <div class="metric-label">Peor Z-Score Global</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Porcentaje de anormalidad
        color = "green" if metricas['porcentaje_anormalidad'] == 0 else "orange" if metricas['porcentaje_anormalidad'] < 50 else "red"
        st.markdown(f"""
        <div class="dashboard-metric status-{color}">
            <div class="metric-value">{metricas['porcentaje_anormalidad']:.0f}%</div>
            <div class="metric-label">Parámetros Anormales</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Total de parámetros analizados
        st.markdown(f"""
        <div class="dashboard-metric">
            <div class="metric-value">{metricas['total_parametros']}</div>
            <div class="metric-label">Total Parámetros</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        # Parámetros anormales
        color = "green" if metricas['parametros_anormales'] == 0 else "orange" if metricas['parametros_anormales'] < 3 else "red"
        st.markdown(f"""
        <div class="dashboard-metric status-{color}">
            <div class="metric-value">{metricas['parametros_anormales']}</div>
            <div class="metric-label">Parámetros Anormales</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Segunda fila con métricas específicas por categoría
    st.markdown("### 📈 Métricas por Categoría")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if 'peor_z_espiro' in metricas:
            color = "green" if metricas['peor_z_espiro'] >= -1.64 else "orange" if metricas['peor_z_espiro'] >= -2.5 else "red"
            st.markdown(f"""
            <div class="metric-card status-{color}">
                <h4>🫁 Espirometría</h4>
                <p><strong>Peor Z-Score:</strong> {metricas['peor_z_espiro']:.2f}</p>
                <p><strong>FEV1:</strong> {metricas.get('fev1_z', 'N/A'):.2f}</p>
                <p><strong>FVC:</strong> {metricas.get('fvc_z', 'N/A'):.2f}</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        if 'peor_z_dlco' in metricas:
            color = "green" if metricas['peor_z_dlco'] >= -1.64 else "orange" if metricas['peor_z_dlco'] >= -2.5 else "red"
            st.markdown(f"""
            <div class="metric-card status-{color}">
                <h4>🩸 Difusión</h4>
                <p><strong>Peor Z-Score:</strong> {metricas['peor_z_dlco']:.2f}</p>
                <p><strong>DLCO:</strong> {metricas.get('dlco_z', 'N/A'):.2f}</p>
                <p><strong>KCO:</strong> {metricas.get('kco_z', 'N/A'):.2f}</p>
                <p><strong>VA:</strong> {metricas.get('va_z', 'N/A'):.2f}</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        if 'peor_z_vol' in metricas:
            color = "green" if metricas['peor_z_vol'] >= -1.64 else "orange" if metricas['peor_z_vol'] >= -2.5 else "red"
            st.markdown(f"""
            <div class="metric-card status-{color}">
                <h4>📊 Volúmenes</h4>
                <p><strong>Peor Z-Score:</strong> {metricas['peor_z_vol']:.2f}</p>
                <p><strong>TLC:</strong> {metricas.get('tlc_z', 'N/A'):.2f}</p>
                <p><strong>VC:</strong> {metricas.get('vc_z', 'N/A'):.2f}</p>
                <p><strong>RV/TLC:</strong> {metricas.get('rv_tlc_z', 'N/A'):.2f}</p>
            </div>
            """, unsafe_allow_html=True)

def crear_grafico_espirometria_horizontal(resultados):
    """Función placeholder - implementar según el archivo original"""
    return None

def crear_grafico_dlco_horizontal(resultados):
    """Función placeholder - implementar según el archivo original"""
    return None

def crear_grafico_volumenes_horizontal(resultados):
    """Función placeholder - implementar según el archivo original"""
    return None

def crear_grafico_broncodilatacion_horizontal(datos):
    """
    Crea un gráfico de barras horizontal para broncodilatación con:
    - Comparación pre/post broncodilatador
    - Porcentaje de cambio
    - Interpretación visual de la respuesta
    """
    if not datos:
        return None
    
    # Extraer datos de broncodilatación
    fev1_pre = datos.get('FEV1 pre')
    fev1_post = datos.get('FEV1 post')
    fvc_pre = datos.get('FVC pre')
    fvc_post = datos.get('FVC post')
    
    # Verificar si hay datos de broncodilatación
    if not all([fev1_pre, fev1_post, fvc_pre, fvc_post]):
        return None
    
    # Verificar que no sean "Valor no encontrado"
    if (fev1_pre == 'Valor no encontrado' or fev1_post == 'Valor no encontrado' or
        fvc_pre == 'Valor no encontrado' or fvc_post == 'Valor no encontrado'):
        return None
    
    try:
        # Convertir a números
        fev1_pre = float(fev1_pre)
        fev1_post = float(fev1_post)
        fvc_pre = float(fvc_pre)
        fvc_post = float(fvc_post)
        
        # Calcular porcentajes de cambio
        cambio_fev1 = ((fev1_post - fev1_pre) / fev1_pre) * 100
        cambio_fvc = ((fvc_post - fvc_pre) / fvc_pre) * 100
        
        # Configurar figura
        fig, ax = plt.subplots(figsize=(10, 4))  # Gráfico más pequeño
        
        # Parámetros y valores
        params = ['FEV1', 'FVC']
        cambios = [cambio_fev1, cambio_fvc]
        colores = []
        
        # Determinar colores basados en el cambio
        for cambio in cambios:
            if cambio >= 12:  # Respuesta significativa
                colores.append('#90EE90')  # Verde claro
            elif cambio >= 5:  # Respuesta parcial
                colores.append('#FFB347')  # Naranja claro
            else:  # Sin respuesta significativa
                colores.append('#FFB6C1')  # Rojo claro
        
        # Crear barras horizontales
        y_positions = np.arange(len(params))
        bar_width = 0.3
        
        # Calcular límites dinámicos primero
        min_cambio = min(cambios) if cambios else -20
        max_cambio = max(cambios) if cambios else 40
        
        # Ajustar límites para mantener valores cerca de las barras
        if min_cambio < -20:
            x_min = min_cambio - 2  # Un poco más allá del valor mínimo
        else:
            x_min = -20
        
        if max_cambio > 40:
            x_max = max_cambio + 2  # Un poco más allá del valor máximo
        else:
            x_max = 40
        
        # Crear barras de cambio
        for i, (param, cambio, color) in enumerate(zip(params, cambios, colores)):
            # Crear rectángulo de fondo
            rect = patches.Rectangle((x_min, i - bar_width/2), x_max - x_min, bar_width, 
                                   facecolor='lightgray', alpha=0.3, edgecolor='gray', linewidth=0.5)
            ax.add_patch(rect)
            
            # Marcar la posición del cambio
            ax.plot(cambio, i, '*', markersize=15, markeredgecolor='white', 
                    markeredgewidth=1, color=color)
            
            # Agregar valor del cambio como texto
            ax.text(cambio + 1, i, f'{cambio:.1f}%', ha='left', va='center', 
                    fontsize=10, fontweight='bold', color=color)
        
        # Líneas de referencia
        ax.axvline(x=0, color='black', linewidth=2, linestyle='-', alpha=0.7)
        ax.axvline(x=5, color='orange', linewidth=2, linestyle='--', alpha=0.7)
        ax.axvline(x=12, color='green', linewidth=2, linestyle='--', alpha=0.7)
        
        # Agregar etiquetas a las líneas
        ax.text(0, len(params) + 0.2, 'Sin cambio', ha='center', va='bottom', 
                fontsize=10, fontweight='bold', color='black')
        ax.text(5, len(params) + 0.2, '5%', ha='center', va='bottom', 
                fontsize=10, fontweight='bold', color='orange')
        ax.text(12, len(params) + 0.2, '12%', ha='center', va='bottom', 
                fontsize=10, fontweight='bold', color='green')
        
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(-0.5, len(params) - 0.5)
        ax.set_yticks(y_positions)
        ax.set_yticklabels(params, fontsize=12, fontweight='bold')
        ax.set_xlabel('Cambio (%)', fontsize=14, fontweight='bold')
        ax.set_title('Respuesta a Broncodilatador', fontsize=16, fontweight='bold', pad=20)
        
        # Agregar grid horizontal
        ax.grid(axis='x', alpha=0.3, linestyle='--')
        
        # Configurar espaciado
        plt.tight_layout()
        
        # Guardar con fondo transparente
        plt.savefig('broncodilatacion_z_scores.png', dpi=300, bbox_inches='tight', 
                    transparent=True, facecolor='none')
        plt.close()
        
        return 'broncodilatacion_z_scores.png'
        
    except (ValueError, TypeError):
        return None

def crear_semaforo_interpretacion(resultados_espiro, resultados_dlco, resultados_vol, interpretacion_bd=None):
    """
    Crea interpretación tipo semáforo basada en los peores z-scores, patrón espirométrico y broncodilatación
    """
    try:
        # Recopilar z-scores relevantes (sin FEF25-75%)
        z_scores = []
        z_labels = []
        # Espirometría (solo FEV1 y FVC)
        if resultados_espiro and "error" not in resultados_espiro:
            for param in ['FEV1', 'FVC']:
                if param in resultados_espiro:
                    z = resultados_espiro[param]['z_score']
                    z_scores.append(z)
                    z_labels.append(param)
        # DLCO
        if resultados_dlco and "error" not in resultados_dlco:
            for param in ['DLCO', 'KCO', 'VA']:
                if param in resultados_dlco:
                    z = resultados_dlco[param]['z_score']
                    z_scores.append(z)
                    z_labels.append(param)
        # Volúmenes
        if resultados_vol and "error" not in resultados_vol:
            for param in ['TLC', 'VC', 'RV', 'RV/TLC']:
                if param in resultados_vol:
                    z = resultados_vol[param]['z_score']
                    z_scores.append(z)
                    z_labels.append(param)
        if not z_scores:
            return "gray", "Sin datos para análisis", "No se encontraron parámetros válidos"
        # Encontrar el peor z-score y su etiqueta
        peor_z = min(z_scores)
        peor_param = z_labels[z_scores.index(peor_z)]
        # Determinar color y texto del semáforo
        if peor_z >= -1.64:
            color = "green"
            texto = "FUNCIÓN PULMONAR NORMAL"
        elif peor_z >= -2.5:
            color = "yellow"
            texto = "ALTERACIÓN LEVE"
        elif peor_z >= -4.0:
            color = "red"
            texto = "ALTERACIÓN MODERADA-SEVERA"
        else:
            color = "red"
            texto = "ALTERACIÓN MUY SEVERA"
        # Patrón espirométrico
        patron_espiro = ""
        if resultados_espiro and "error" not in resultados_espiro:
            patron_espiro = generar_interpretacion_general(resultados_espiro).split('\n')[0]  # Solo la primera línea
        # Broncodilatación
        texto_bd = ""
        if interpretacion_bd:
            texto_bd = f"<br/><b>Broncodilatación:</b> {interpretacion_bd.splitlines()[0]}"
        # Descripción de la base del color
        descripcion = f"<b>Color basado en:</b> {peor_param} (Z = {peor_z:.2f})<br/>{patron_espiro}{texto_bd}"
        return color, texto, descripcion
    except Exception as e:
        return "gray", f"Error en análisis: {str(e)}", "Error interno"

def interpretar_broncodilatacion(datos):
    """
    Interpreta la respuesta broncodilatadora usando doble umbral (≥12% y ≥200 mL),
    preferencia FEV1, FVC solo si FEV1 no mejora, y agrega interpretación clínica.
    """
    try:
        # Obtener valores pre y post
        fvc_pre = datos.get('FVC pre')
        fev1_pre = datos.get('FEV1 pre')
        fvc_post = datos.get('FVC post')
        fev1_post = datos.get('FEV1 post')
        edad = datos.get('Edad')
        altura = datos.get('Altura')
        sexo = datos.get('Sexo', 'Femenino')
        
        # Verificar si faltan datos post
        if not fvc_post or fvc_post == 'Valor no encontrado':
            return "⚠️ **No se puede interpretar broncodilatación**\n\nFaltan datos de FVC post-broncodilatación."
        if not fev1_post or fev1_post == 'Valor no encontrado':
            return "⚠️ **No se puede interpretar broncodilatación**\n\nFaltan datos de FEV1 post-broncodilatación."
        if not all([fvc_pre, fev1_pre, edad, altura]):
            return "⚠️ **No se puede interpretar broncodilatación**\n\nFaltan datos demográficos o valores pre-broncodilatación."
        
        # Convertir a float
        fvc_pre = float(fvc_pre)
        fev1_pre = float(fev1_pre)
        fvc_post = float(fvc_post)
        fev1_post = float(fev1_post)
        edad = float(edad)
        altura = float(altura)
        
        # Calcular cambios absolutos y porcentuales
        delta_fvc = fvc_post - fvc_pre
        delta_fev1 = fev1_post - fev1_pre
        delta_fvc_pct = (delta_fvc / fvc_pre) * 100
        delta_fev1_pct = (delta_fev1 / fev1_pre) * 100
        delta_fvc_ml = delta_fvc * 1000
        delta_fev1_ml = delta_fev1 * 1000
        
        # Doble umbral: ambos deben cumplirse
        respuesta_fev1 = (delta_fev1_pct >= 12) and (delta_fev1_ml >= 200)
        respuesta_fvc = (delta_fvc_pct >= 12) and (delta_fvc_ml >= 200)
        respuesta_fev1_400 = delta_fev1_ml >= 400
        
        # Calcular z-score pre y post
        fev1_esp = calcular_valor_esperado_fev1(edad, altura, sexo)
        fvc_esp = calcular_valor_esperado_fvc(edad, altura, sexo)
        z_fev1_pre = calcular_z_score(fev1_pre, fev1_esp)
        z_fev1_post = calcular_z_score(fev1_post, fev1_esp)
        z_fvc_pre = calcular_z_score(fvc_pre, fvc_esp)
        z_fvc_post = calcular_z_score(fvc_post, fvc_esp)
        int_fev1_pre, sev_fev1_pre = interpretar_z_score_con_severidad(z_fev1_pre)
        int_fev1_post, sev_fev1_post = interpretar_z_score_con_severidad(z_fev1_post)
        int_fvc_pre, sev_fvc_pre = interpretar_z_score_con_severidad(z_fvc_pre)
        int_fvc_post, sev_fvc_post = interpretar_z_score_con_severidad(z_fvc_post)

        texto = f"**FEV1**: +{delta_fev1:.2f}L ({delta_fev1_pct:.1f}%, {delta_fev1_ml:.0f} mL)\n"
        texto += f"Z-score pre: {z_fev1_pre:.2f} ({int_fev1_pre}), post: {z_fev1_post:.2f} ({int_fev1_post})\n"
        texto += f"**FVC**: +{delta_fvc:.2f}L ({delta_fvc_pct:.1f}%, {delta_fvc_ml:.0f} mL)\n"
        texto += f"Z-score pre: {z_fvc_pre:.2f} ({int_fvc_pre}), post: {z_fvc_post:.2f} ({int_fvc_post})\n\n"

        # Mensaje clínico
        clinica = ""
        if respuesta_fev1:
            if respuesta_fev1_400:
                clinica = "🔬 **Interpretación clínica:** Un aumento >400 mL en FEV₁ sugiere alta probabilidad de asma.\n"
            clinica += "🫁 **Interpretación clínica:** La positividad apoya diagnóstico de asma (reversibilidad típica). En EPOC, un test positivo sugiere componente reversible, pero no descarta EPOC.\n"
            return f"✅ **Broncodilatación positiva por FEV₁**\n\n{texto}{clinica}"
        elif respuesta_fvc:
            clinica = "🫁 **Interpretación clínica:** La positividad por FVC puede ser útil en enfisema con atrapamiento aéreo.\n"
            clinica += "En EPOC, un test positivo sugiere componente reversible, pero no descarta EPOC.\n"
            return f"✅ **Broncodilatación positiva por FVC**\n\n{texto}{clinica}"
        else:
            return f"❌ **Sin respuesta broncodilatadora significativa**\n\n{texto}Ningún parámetro cumple criterios de respuesta significativa (≥12% y ≥200 mL).\n\nNo usar FEV₁/FVC para determinar positividad."
    except Exception as e:
        return f"❌ Error en interpretación de broncodilatación: {str(e)}"

def generar_recomendaciones_clinicas(resultados_espiro, resultados_dlco, resultados_vol, interpretacion_bd):
    """Función placeholder - implementar según el archivo original"""
    return "Recomendaciones clínicas"

def generar_reporte_pdf(datos, resultados_espiro, resultados_dlco, resultados_vol, interpretacion_bd, nombre_archivo="PulmoReport_AI"):
    """
    Genera un reporte PDF completo del análisis de función pulmonar
    """
    try:
        # Crear buffer para el PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Estilos personalizados
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1,  # Centrado
            textColor=colors.HexColor('#1f77b4')
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=20,
            textColor=colors.HexColor('#2c3e50')
        )
        
        # Título principal
        story.append(Paragraph("🫁 PulmoReport AI", title_style))
        story.append(Paragraph("Análisis Inteligente de Funcionalismo Pulmonar", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Información del paciente
        story.append(Paragraph("📋 INFORMACIÓN DEL PACIENTE", subtitle_style))
        if datos.get('Edad') and datos.get('Altura') and datos.get('Sexo'):
            info_paciente = [
                ['Edad', datos.get('Edad', 'N/A')],
                ['Altura', f"{datos.get('Altura', 'N/A')} cm"],
                ['Sexo', datos.get('Sexo', 'N/A')],
                ['Peso', f"{datos.get('Peso', 'N/A')} kg"] if datos.get('Peso') else ['Peso', 'N/A']
            ]
            t = Table(info_paciente, colWidths=[2*inch, 3*inch])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(t)
        story.append(Spacer(1, 20))

        # Diagnóstico Detallado
        story.append(Paragraph("🩺 DIAGNÓSTICO DETALLADO", subtitle_style))
        try:
            interpretacion_general = generar_interpretacion_general(resultados_espiro)
        except Exception as e:
            interpretacion_general = f"Error generando diagnóstico: {str(e)}"
        story.append(Paragraph(interpretacion_general.replace('\n', '<br/>'), styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Resultados de Espirometría
        if resultados_espiro and "error" not in resultados_espiro:
            story.append(Paragraph("📊 RESULTADOS DE ESPIROMETRÍA", subtitle_style))
            espiro_data = []
            espiro_data.append(['Parámetro', 'Observado', 'Esperado', 'Z-Score', 'Interpretación'])
            
            for param in ['FEV1', 'FVC', 'FEF25-75%']:
                if param in resultados_espiro:
                    datos_analisis = resultados_espiro[param]
                    espiro_data.append([
                        param,
                        f"{datos_analisis['observado']:.2f}",
                        f"{datos_analisis['esperado']:.2f}",
                        f"{datos_analisis['z_score']:.2f}",
                        datos_analisis['interpretacion']
                    ])
            
            t = Table(espiro_data, colWidths=[1.2*inch, 1*inch, 1*inch, 1*inch, 2.8*inch])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(t)
            story.append(Spacer(1, 20))
        
        # Resultados de DLCO
        if resultados_dlco and "error" not in resultados_dlco:
            story.append(Paragraph("🫁 RESULTADOS DE DLCO", subtitle_style))
            dlco_data = []
            dlco_data.append(['Parámetro', 'Observado', 'Esperado', 'Z-Score', 'Interpretación'])
            
            for param in ['DLCO', 'KCO', 'VA']:
                if param in resultados_dlco:
                    datos_analisis = resultados_dlco[param]
                    dlco_data.append([
                        param,
                        f"{datos_analisis['observado']:.2f}",
                        f"{datos_analisis['esperado']:.2f}",
                        f"{datos_analisis['z_score']:.2f}",
                        datos_analisis['interpretacion']
                    ])
            
            t = Table(dlco_data, colWidths=[1.2*inch, 1*inch, 1*inch, 1*inch, 2.8*inch])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(t)
            story.append(Spacer(1, 20))
        
        # Resultados de Volúmenes
        if resultados_vol and "error" not in resultados_vol:
            story.append(Paragraph("📏 RESULTADOS DE VOLÚMENES PULMONARES", subtitle_style))
            vol_data = []
            vol_data.append(['Parámetro', 'Observado', 'Esperado', 'Z-Score', 'Interpretación'])
            
            for param in ['TLC', 'VC', 'RV', 'RV/TLC']:
                if param in resultados_vol:
                    datos_analisis = resultados_vol[param]
                    vol_data.append([
                        param,
                        f"{datos_analisis['observado']:.2f}",
                        f"{datos_analisis['esperado']:.2f}",
                        f"{datos_analisis['z_score']:.2f}",
                        datos_analisis['interpretacion']
                    ])
            
            t = Table(vol_data, colWidths=[1.2*inch, 1*inch, 1*inch, 1*inch, 2.8*inch])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(t)
            story.append(Spacer(1, 20))
        
        # Interpretación de Broncodilatación
        if interpretacion_bd:
            story.append(Paragraph("💨 ANÁLISIS DE BRONCODILATACIÓN", subtitle_style))
            story.append(Paragraph(interpretacion_bd, styles['Normal']))
            story.append(Spacer(1, 20))
        
        # Recomendaciones
        if resultados_espiro and "error" not in resultados_espiro:
            story.append(Paragraph("📝 ANÁLISIS CLÍNICO", subtitle_style))
            recomendaciones = generar_recomendaciones_clinicas(
                resultados_espiro, resultados_dlco, resultados_vol, interpretacion_bd
            )
            story.append(Paragraph(recomendaciones, styles['Normal']))
            story.append(Spacer(1, 20))
        
        # Footer
        story.append(Paragraph("© 2025 PulmoReport AI - Diseñado por Edmundo Rosales Mayor", 
                              ParagraphStyle('Footer', fontSize=8, alignment=1, textColor=colors.grey)))
        
        # Construir PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer
        
    except Exception as e:
        st.error(f"Error generando PDF: {str(e)}")
        return None

def validar_datos_extraidos(datos):
    """Función placeholder - implementar según el archivo original"""
    return {
        'errores': [],
        'advertencias': [],
        'sugerencias': [],
        'datos_espiro': True,
        'datos_dlco': True,
        'datos_vol': True,
        'parametros_disponibles': []
    }

# Código principal
if uploaded_files:
    # Generar un identificador único para este conjunto de archivos
    files_hash = hashlib.md5(str([f.name for f in uploaded_files]).encode()).hexdigest()
    
    # Verificar si es un nuevo conjunto de archivos
    if 'current_files_hash' not in st.session_state or st.session_state['current_files_hash'] != files_hash:
        st.session_state['current_files_hash'] = files_hash
        # Limpiar cualquier contenido previo
        st.empty()
    
    # Si hay múltiples archivos, mostrar comparación temporal
    if len(uploaded_files) > 1:
        st.markdown("## 📈 Análisis de Múltiples PDFs")
        
        # Procesar todos los PDFs para comparación temporal
        with st.spinner("Procesando múltiples PDFs para comparación temporal..."):
            resultados_multiples = procesar_multiples_pdfs(uploaded_files)
        
        if resultados_multiples:
            mostrar_comparacion_temporal(resultados_multiples)
            st.markdown("---")
    
    # Procesar cada archivo individualmente
    for uploaded_file in uploaded_files:
        st.subheader(f'📄 Archivo: {uploaded_file.name}')
        with pdfplumber.open(uploaded_file) as pdf:
            text = ''
            for page in pdf.pages:
                text += page.extract_text() or ''
            
            with st.expander("📋 Texto extraído del PDF"):
                st.text_area('Texto extraído', text, height=300, key=f"texto_area_{uploaded_file.name}")
            
            # Extracción estructurada
            datos = extract_datos_pulmonar(text)
            datos = mapear_claves_pre(datos)
            
            # Guardar datos en session_state para uso posterior
            st.session_state['datos_extraidos'] = datos
            
            # Validación de datos
            validacion = validar_datos_extraidos(datos)
            
            # Mostrar información de debug
            with st.expander("🔍 Información de Debug"):
                st.write(f"**Parámetros disponibles:** {', '.join(validacion['parametros_disponibles'])}")
                st.write(f"**Datos espirometría encontrados:** {validacion['datos_espiro']}")
                st.write(f"**Datos DLCO encontrados:** {validacion['datos_dlco']}")
                st.write(f"**Datos volúmenes encontrados:** {validacion['datos_vol']}")
            
            # Mostrar errores y advertencias
            if validacion['errores']:
                st.error("**Errores encontrados:**")
                for error in validacion['errores']:
                    st.error(error)
            
            if validacion['advertencias']:
                st.warning("**Advertencias:**")
                for advertencia in validacion['advertencias']:
                    st.warning(advertencia)
            
            if validacion['sugerencias']:
                with st.expander("💡 Sugerencias de corrección"):
                    for sugerencia in validacion['sugerencias']:
                        st.info(sugerencia)
            
            with st.expander("📊 Datos Extraídos (Click para ver)"):
                # Añadir unidades a los nombres de las variables
                datos_con_unidades = {}
                for k, v in datos.items():
                    if k.lower() == 'talla' or k.lower() == 'altura':
                        datos_con_unidades[k + ' (cm)'] = v
                    elif k.lower() == 'peso':
                        datos_con_unidades[k + ' (kg)'] = v
                    elif k.lower() == 'edad':
                        datos_con_unidades[k + ' (años)'] = v
                    else:
                        datos_con_unidades[k] = v
                st.table(datos_con_unidades)
            
            # Análisis GLI con caché
            st.subheader('🔬 Análisis GLI e Interpretación Visual')
            
            # Verificar datos mínimos necesarios
            if datos.get('Edad') and datos.get('Altura') and datos.get('Sexo'):
                if datos['Edad'] != 'Valor no encontrado' and datos['Altura'] != 'Valor no encontrado':
                    
                    # Caché de análisis - verificar si ya se realizó
                    cache_key = f"analisis_{hashlib.md5(str(datos).encode()).hexdigest()}"
                    
                    if cache_key not in st.session_state:
                        # Realizar análisis y guardar en caché
                        st.session_state[cache_key] = {
                            'espiro': analizar_espirometria(datos),
                            'dlco': analizar_dlco(datos),
                            'vol': analizar_volumenes(datos),
                            'bd': interpretar_broncodilatacion(datos)
                        }
                    
                    # Obtener resultados del caché
                    resultados_espiro = st.session_state[cache_key]['espiro']
                    resultados_dlco = st.session_state[cache_key]['dlco']
                    resultados_vol = st.session_state[cache_key]['vol']
                    interpretacion_bd = st.session_state[cache_key]['bd']
                    
                    # Crear y mostrar dashboard overview
                    metricas = crear_metricas_dashboard(datos, resultados_espiro, resultados_dlco, resultados_vol)
                    mostrar_dashboard_overview(metricas)
                    
                    # Botón de exportación PDF
                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col2:
                        if st.button("📄 Exportar Reporte PDF", use_container_width=True, type="primary", key=f"export_pdf_{uploaded_file.name}"):
                            with st.spinner("Generando reporte PDF..."):
                                pdf_buffer = generar_reporte_pdf(
                                    datos, resultados_espiro, resultados_dlco, 
                                    resultados_vol, interpretacion_bd, 
                                    f"PulmoReport_{uploaded_file.name.replace('.pdf', '')}"
                                )
                                if pdf_buffer:
                                    st.download_button(
                                        label="⬇️ Descargar PDF",
                                        data=pdf_buffer.getvalue(),
                                        file_name=f"PulmoReport_{uploaded_file.name.replace('.pdf', '')}.pdf",
                                        mime="application/pdf",
                                        use_container_width=True,
                                        key=f"download_pdf_{uploaded_file.name}"
                                    )
                                else:
                                    st.error("Error generando el PDF")
                    
                    # Crear pestañas para diferentes tipos de análisis
                    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Espirometría", "🫁 DLCO", "📏 Volúmenes", "💨 Broncodilatación", "📋 Resumen"])
                    
                    with tab1:
                        st.markdown("### 📊 Análisis Visual de Espirometría")
                        # Usar resultados del caché
                        
                        if "error" not in resultados_espiro:
                            # Filtrar solo parámetros de espirometría
                            espiro_params = ['FEV1', 'FVC', 'FEF25-75%']
                            resultados_filtrados = {k: v for k, v in resultados_espiro.items() if k in espiro_params}
                            
                            if resultados_filtrados:
                                # Crear gráfico visual horizontal
                                imagen_espiro = crear_grafico_espirometria_horizontal(resultados_filtrados)
                                if imagen_espiro:
                                    st.image(imagen_espiro, use_container_width=True, caption="Gráfico de Puntuaciones Z de Espirometría")
                                
                                # Tabla de resultados
                                st.markdown("**Resultados Detallados:**")
                                espiro_data = []
                                for param, datos_analisis in resultados_filtrados.items():
                                    espiro_data.append({
                                        'Parámetro': param,
                                        'Observado': datos_analisis['observado'],
                                        'Esperado': datos_analisis['esperado'],
                                        'Z-Score': datos_analisis['z_score'],
                                        'Interpretación': datos_analisis['interpretacion'],
                                        'Severidad': datos_analisis['severidad']
                                    })
                                
                                espiro_df = pd.DataFrame(espiro_data)
                                st.table(espiro_df)
                            else:
                                st.warning("⚠️ No se encontraron datos de espirometría válidos.")
                        else:
                            st.error(f"❌ Error en el análisis: {resultados_espiro['error']}")
                    
                    with tab2:
                        st.markdown("### 🫁 Análisis Visual de DLCO")
                        # Usar resultados del caché
                        
                        if "error" not in resultados_dlco:
                            dlco_params = ['DLCO', 'KCO', 'VA']
                            resultados_filtrados = {k: v for k, v in resultados_dlco.items() if k in dlco_params}
                            
                            if resultados_filtrados:
                                # Crear gráfico visual horizontal
                                imagen_dlco = crear_grafico_dlco_horizontal(resultados_filtrados)
                                if imagen_dlco:
                                    st.image(imagen_dlco, use_container_width=True, caption="Gráfico de Puntuaciones Z de DLCO")
                                
                                # Tabla de resultados
                                st.markdown("**Resultados Detallados:**")
                                dlco_data = []
                                for param, datos_analisis in resultados_filtrados.items():
                                    dlco_data.append({
                                        'Parámetro': param,
                                        'Observado': datos_analisis['observado'],
                                        'Esperado': datos_analisis['esperado'],
                                        'Z-Score': datos_analisis['z_score'],
                                        'Interpretación': datos_analisis['interpretacion'],
                                        'Severidad': datos_analisis['severidad']
                                    })
                                
                                dlco_df = pd.DataFrame(dlco_data)
                                st.table(dlco_df)
                            else:
                                st.warning("⚠️ No se encontraron datos de DLCO válidos.")
                        else:
                            st.error(f"❌ Error en el análisis DLCO: {resultados_dlco['error']}")
                    
                    with tab3:
                        st.markdown("### 📏 Análisis Visual de Volúmenes Pulmonares")
                        # Usar resultados del caché
                        
                        if "error" not in resultados_vol:
                            vol_params = ['TLC', 'VC', 'RV', 'RV/TLC']
                            resultados_filtrados = {k: v for k, v in resultados_vol.items() if k in vol_params}
                            
                            if resultados_filtrados:
                                # Crear gráfico visual horizontal
                                imagen_vol = crear_grafico_volumenes_horizontal(resultados_filtrados)
                                if imagen_vol:
                                    st.image(imagen_vol, use_container_width=True, caption="Gráfico de Puntuaciones Z de Volúmenes Pulmonares")
                                
                                # Tabla de resultados
                                st.markdown("**Resultados Detallados:**")
                                vol_data = []
                                for param, datos_analisis in resultados_filtrados.items():
                                    vol_data.append({
                                        'Parámetro': param,
                                        'Observado': datos_analisis['observado'],
                                        'Esperado': datos_analisis['esperado'],
                                        'Z-Score': datos_analisis['z_score'],
                                        'Interpretación': datos_analisis['interpretacion'],
                                        'Severidad': datos_analisis['severidad']
                                    })
                                
                                vol_df = pd.DataFrame(vol_data)
                                st.table(vol_df)
                            else:
                                st.warning("⚠️ No se encontraron datos de volúmenes válidos.")
                        else:
                            st.error(f"❌ Error en el análisis de volúmenes: {resultados_vol['error']}")
                    
                    with tab4:
                        st.markdown("### 💨 Análisis Visual de Broncodilatación")
                        # Usar resultados del caché
                        
                        # Crear gráfico de broncodilatación horizontal
                        imagen_bd = crear_grafico_broncodilatacion_horizontal(datos)
                        if imagen_bd:
                            st.image(imagen_bd, use_container_width=True, caption="Respuesta a Broncodilatador")
                        
                        # Mostrar interpretación del caché
                        st.markdown(interpretacion_bd)
                    
                    with tab5:
                        st.markdown("### 📋 Resumen General con Semáforo")
                        # Usar resultados del caché
                        
                        if "error" not in resultados_espiro:
                            # Crear semáforo de interpretación
                            color_semaforo, texto_semaforo, descripcion = crear_semaforo_interpretacion(
                                resultados_espiro, resultados_dlco, resultados_vol, interpretacion_bd
                            )
                            
                            # Mostrar semáforo
                            col1, col2, col3 = st.columns([1, 2, 1])
                            with col2:
                                st.markdown(f"""
                                <div style="text-align: center; padding: 20px; background-color: #f8f9fa; border-radius: 10px;">
                                    <div class="traffic-light {color_semaforo}" style="margin: 0 auto 10px auto;"></div>
                                    <h3 style="color: {color_semaforo}; margin: 0;">{texto_semaforo}</h3>
                                    <div style='font-size: 1rem; color: #333; margin-top: 10px; text-align: left;'>{descripcion}</div>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            # Detección de patrones de enfermedad
                            mostrar_deteccion_patrones(resultados_espiro, resultados_dlco, resultados_vol, datos)
                            
                            # Interpretación general
                            st.markdown("**📋 Interpretación General:**")
                            interpretacion = generar_interpretacion_general(resultados_espiro)
                            st.markdown(interpretacion)
                            
                            # Generar recomendaciones clínicas
                            st.markdown("**🎯 Recomendaciones Clínicas:**")
                            recomendaciones = generar_recomendaciones_clinicas(
                                resultados_espiro, 
                                resultados_dlco, 
                                resultados_vol, 
                                interpretacion_bd
                            )
                            st.markdown(recomendaciones)
                        else:
                            st.error(f"❌ Error en el análisis: {resultados_espiro['error']}")
                
                else:
                    st.warning("⚠️ Faltan datos de edad o altura para realizar el análisis GLI.")
            else:
                st.warning("⚠️ Faltan datos demográficos (edad, altura, sexo) para realizar el análisis GLI.") 

# Footer con copyright
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 20px; background-color: #f8f9fa; border-radius: 10px; margin-top: 30px;">
    <p style="color: #6c757d; font-size: 14px; margin: 0;">
        © 2025 PulmoReport AI - Diseñado por <strong>Edmundo Rosales Mayor</strong><br>
        Análisis Inteligente de Funcionalismo Pulmonar con Visualización Avanzada
    </p>
</div>
""", unsafe_allow_html=True) 