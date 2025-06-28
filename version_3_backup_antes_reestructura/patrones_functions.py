import streamlit as st
import pdfplumber
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from utils.extraccion import extract_datos_pulmonar
from utils.analisis_gli import analizar_espirometria, analizar_dlco, analizar_volumenes

def mapear_claves_pre(datos):
    """
    Mapea automáticamente los valores extraídos a las claves con sufijo 'pre' si no existen.
    """
    claves = ['DLCO', 'KCO', 'VA', 'TLC', 'VC', 'RV', 'RV/TLC', 'FEV1', 'FVC', 'FEF25-75%']
    for clave in claves:
        if clave in datos and datos[clave] not in [None, '', 'Valor no encontrado']:
            clave_pre = clave + ' pre' if clave not in ['RV/TLC'] else 'RV/TLC pre'
            if clave_pre not in datos or datos[clave_pre] in [None, '', 'Valor no encontrado']:
                datos[clave_pre] = datos[clave]
    return datos

def procesar_multiples_pdfs(uploaded_files):
    """
    Procesa múltiples PDFs y almacena los resultados para comparación temporal
    """
    resultados_multiples = []
    
    for uploaded_file in uploaded_files:
        try:
            with pdfplumber.open(uploaded_file) as pdf:
                text = ''
                for page in pdf.pages:
                    text += page.extract_text() or ''
            
            # Extracción estructurada
            datos = extract_datos_pulmonar(text)
            datos = mapear_claves_pre(datos)
            
            # Análisis GLI si hay datos suficientes
            if datos.get('Edad') and datos.get('Altura') and datos.get('Sexo'):
                if datos['Edad'] != 'Valor no encontrado' and datos['Altura'] != 'Valor no encontrado':
                    resultados_espiro = analizar_espirometria(datos)
                    resultados_dlco = analizar_dlco(datos)
                    resultados_vol = analizar_volumenes(datos)
                    
                    # Extraer fecha del nombre del archivo o usar fecha actual
                    fecha_archivo = uploaded_file.name.split('_')[0] if '_' in uploaded_file.name else "Fecha N/A"
                    
                    resultados_multiples.append({
                        'archivo': uploaded_file.name,
                        'fecha': fecha_archivo,
                        'datos': datos,
                        'espiro': resultados_espiro,
                        'dlco': resultados_dlco,
                        'vol': resultados_vol
                    })
        
        except Exception as e:
            st.error(f"Error procesando {uploaded_file.name}: {str(e)}")
    
    return resultados_multiples

def crear_grafico_evolucion_temporal(resultados_multiples, parametro):
    """
    Crea un gráfico de evolución temporal para un parámetro específico
    """
    if len(resultados_multiples) < 2:
        return None
    
    fechas = []
    valores = []
    z_scores = []
    
    for resultado in resultados_multiples:
        fechas.append(resultado['fecha'])
        
        # Buscar el parámetro en los diferentes análisis
        valor = None
        z_score = None
        
        if parametro in ['FEV1', 'FVC', 'FEF25-75%']:
            if 'error' not in resultado['espiro'] and parametro in resultado['espiro']:
                valor = resultado['espiro'][parametro]['observado']
                z_score = resultado['espiro'][parametro]['z_score']
        elif parametro in ['DLCO', 'KCO', 'VA']:
            if 'error' not in resultado['dlco'] and parametro in resultado['dlco']:
                valor = resultado['dlco'][parametro]['observado']
                z_score = resultado['dlco'][parametro]['z_score']
        elif parametro in ['TLC', 'VC', 'RV', 'RV/TLC']:
            if 'error' not in resultado['vol'] and parametro in resultado['vol']:
                valor = resultado['vol'][parametro]['observado']
                z_score = resultado['vol'][parametro]['z_score']
        
        valores.append(valor)
        z_scores.append(z_score)
    
    # Filtrar valores válidos
    datos_validos = [(f, v, z) for f, v, z in zip(fechas, valores, z_scores) if v is not None and z is not None]
    
    if len(datos_validos) < 2:
        return None
    
    fechas_limpias, valores_limpias, z_scores_limpias = zip(*datos_validos)
    
    # Crear figura con dos subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # Gráfico de valores observados
    ax1.plot(range(len(fechas_limpias)), valores_limpias, 'o-', linewidth=2, markersize=8, color='#1f77b4')
    ax1.set_title(f'Evolución Temporal - {parametro} (Valores Observados)', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Valor Observado', fontsize=12)
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks(range(len(fechas_limpias)))
    ax1.set_xticklabels(fechas_limpias, rotation=45)
    
    # Agregar valores en los puntos
    for i, valor in enumerate(valores_limpias):
        ax1.annotate(f'{valor:.2f}', (i, valor), textcoords="offset points", xytext=(0,10), ha='center')
    
    # Gráfico de Z-scores
    colors = ['green' if z >= -1.64 else 'orange' if z >= -2.5 else 'red' for z in z_scores_limpias]
    bars = ax2.bar(range(len(fechas_limpias)), z_scores_limpias, color=colors, alpha=0.7)
    ax2.set_title(f'Evolución Temporal - {parametro} (Z-Scores)', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Z-Score', fontsize=12)
    ax2.set_xlabel('Fecha', fontsize=12)
    ax2.grid(True, alpha=0.3)
    ax2.set_xticks(range(len(fechas_limpias)))
    ax2.set_xticklabels(fechas_limpias, rotation=45)
    
    # Líneas de referencia para Z-scores
    ax2.axhline(y=-1.64, color='black', linestyle='--', linewidth=2, label='LLN')
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=2, label='Predicho')
    ax2.axhline(y=-2.5, color='red', linestyle=':', linewidth=2, label='Severidad')
    ax2.legend()
    
    # Agregar valores de Z-score en las barras
    for i, z_score in enumerate(z_scores_limpias):
        ax2.annotate(f'{z_score:.2f}', (i, z_score), textcoords="offset points", xytext=(0,3), ha='center')
    
    plt.tight_layout()
    
    # Guardar gráfico
    nombre_archivo = f'evolucion_{parametro.lower().replace("/", "_")}.png'
    plt.savefig(nombre_archivo, dpi=300, bbox_inches='tight', transparent=True)
    plt.close()
    
    return nombre_archivo

def mostrar_comparacion_temporal(resultados_multiples):
    """
    Muestra la comparación temporal de múltiples PDFs
    """
    if len(resultados_multiples) < 2:
        st.warning("⚠️ Se necesitan al menos 2 PDFs para mostrar comparación temporal.")
        return
    
    st.markdown("## 📈 Comparación Temporal")
    
    # Resumen de archivos procesados
    st.markdown("### 📋 Archivos Procesados")
    archivos_info = []
    for resultado in resultados_multiples:
        archivos_info.append({
            'Archivo': resultado['archivo'],
            'Fecha': resultado['fecha'],
            'Edad': resultado['datos'].get('Edad', 'N/A'),
            'Altura': resultado['datos'].get('Altura', 'N/A'),
            'Sexo': resultado['datos'].get('Sexo', 'N/A')
        })
    
    archivos_df = pd.DataFrame(archivos_info)
    st.table(archivos_df)
    
    # Selección de parámetro para evolución
    st.markdown("### 📊 Evolución Temporal por Parámetro")
    
    # Obtener parámetros disponibles
    parametros_disponibles = []
    for resultado in resultados_multiples:
        if 'error' not in resultado['espiro']:
            parametros_disponibles.extend(['FEV1', 'FVC', 'FEF25-75%'])
        if 'error' not in resultado['dlco']:
            parametros_disponibles.extend(['DLCO', 'KCO', 'VA'])
        if 'error' not in resultado['vol']:
            parametros_disponibles.extend(['TLC', 'VC', 'RV', 'RV/TLC'])
        break
    
    parametros_disponibles = list(set(parametros_disponibles))
    
    if parametros_disponibles:
        parametro_seleccionado = st.selectbox(
            "Selecciona el parámetro para visualizar su evolución:",
            parametros_disponibles,
            key="parametro_evolucion"
        )
        
        # Crear y mostrar gráfico de evolución
        imagen_evolucion = crear_grafico_evolucion_temporal(resultados_multiples, parametro_seleccionado)
        if imagen_evolucion:
            st.image(imagen_evolucion, use_container_width=True, 
                    caption=f"Evolución Temporal de {parametro_seleccionado}")
        else:
            st.warning(f"⚠️ No hay suficientes datos válidos para mostrar la evolución de {parametro_seleccionado}")
    
    # Tabla comparativa de Z-scores
    st.markdown("### 📊 Comparación de Z-Scores")
    
    # Crear tabla comparativa
    parametros_comparacion = ['FEV1', 'FVC', 'DLCO', 'TLC']
    datos_comparacion = []
    
    for resultado in resultados_multiples:
        fila = {'Fecha': resultado['fecha']}
        
        for param in parametros_comparacion:
            z_score = None
            if param in ['FEV1', 'FVC'] and 'error' not in resultado['espiro'] and param in resultado['espiro']:
                z_score = resultado['espiro'][param]['z_score']
            elif param == 'DLCO' and 'error' not in resultado['dlco'] and param in resultado['dlco']:
                z_score = resultado['dlco'][param]['z_score']
            elif param == 'TLC' and 'error' not in resultado['vol'] and param in resultado['vol']:
                z_score = resultado['vol'][param]['z_score']
            
            fila[param] = f"{z_score:.2f}" if z_score is not None else "N/A"
        
        datos_comparacion.append(fila)
    
    if datos_comparacion:
        comparacion_df = pd.DataFrame(datos_comparacion)
        st.table(comparacion_df)
    else:
        st.warning("⚠️ No hay datos suficientes para mostrar la comparación.")

def detectar_patron_obstructivo(resultados_espiro, resultados_vol):
    """
    Detecta patrón obstructivo basado en criterios clínicos
    """
    if 'error' in resultados_espiro or 'error' in resultados_vol:
        return False, "Datos insuficientes"
    
    # Criterios para patrón obstructivo
    fev1_z = resultados_espiro.get('FEV1', {}).get('z_score', 0)
    fvc_z = resultados_espiro.get('FVC', {}).get('z_score', 0)
    fef_z = resultados_espiro.get('FEF25-75%', {}).get('z_score', 0)
    fev1_fvc_ratio = resultados_espiro.get('FEV1/FVC', {}).get('observado', 0)
    
    # Criterios de volúmenes
    tlc_z = resultados_vol.get('TLC', {}).get('z_score', 0)
    rv_z = resultados_vol.get('RV', {}).get('z_score', 0)
    rv_tlc_z = resultados_vol.get('RV/TLC', {}).get('z_score', 0)
    
    # Patrón obstructivo: FEV1 < LLN, FEV1/FVC < LLN, TLC normal o aumentado
    es_obstructivo = (
        fev1_z < -1.64 and  # FEV1 reducido
        fev1_fvc_ratio < 0.7 and  # Ratio FEV1/FVC reducido
        tlc_z >= -1.64  # TLC normal o aumentado
    )
    
    severidad = "Leve"
    if fev1_z < -2.5:
        severidad = "Moderado"
    if fev1_z < -3.0:
        severidad = "Severo"
    
    return es_obstructivo, f"Patrón obstructivo {severidad}"

def detectar_patron_restrictivo(resultados_espiro, resultados_vol):
    """
    Detecta patrón restrictivo basado en criterios clínicos
    """
    if 'error' in resultados_espiro or 'error' in resultados_vol:
        return False, "Datos insuficientes"
    
    # Criterios para patrón restrictivo
    fev1_z = resultados_espiro.get('FEV1', {}).get('z_score', 0)
    fvc_z = resultados_espiro.get('FVC', {}).get('z_score', 0)
    fev1_fvc_ratio = resultados_espiro.get('FEV1/FVC', {}).get('observado', 0)
    
    # Criterios de volúmenes
    tlc_z = resultados_vol.get('TLC', {}).get('z_score', 0)
    vc_z = resultados_vol.get('VC', {}).get('z_score', 0)
    
    # Patrón restrictivo: FVC < LLN, TLC < LLN, FEV1/FVC normal o aumentado
    es_restrictivo = (
        fvc_z < -1.64 and  # FVC reducido
        tlc_z < -1.64 and  # TLC reducido
        fev1_fvc_ratio >= 0.7  # Ratio FEV1/FVC normal o aumentado
    )
    
    severidad = "Leve"
    if tlc_z < -2.5:
        severidad = "Moderado"
    if tlc_z < -3.0:
        severidad = "Severo"
    
    return es_restrictivo, f"Patrón restrictivo {severidad}"

def detectar_patron_mixto(resultados_espiro, resultados_vol):
    """
    Detecta patrón mixto (obstructivo + restrictivo)
    """
    es_obstructivo, _ = detectar_patron_obstructivo(resultados_espiro, resultados_vol)
    es_restrictivo, _ = detectar_patron_restrictivo(resultados_espiro, resultados_vol)
    
    if es_obstructivo and es_restrictivo:
        return True, "Patrón mixto (obstructivo + restrictivo)"
    
    return False, "No es patrón mixto"

def detectar_alteracion_difusion(resultados_dlco):
    """
    Detecta alteración de la difusión
    """
    if 'error' in resultados_dlco:
        return False, "Datos insuficientes"
    
    dlco_z = resultados_dlco.get('DLCO', {}).get('z_score', 0)
    kco_z = resultados_dlco.get('KCO', {}).get('z_score', 0)
    va_z = resultados_dlco.get('VA', {}).get('z_score', 0)
    
    # Alteración de difusión: DLCO < LLN
    es_alteracion = dlco_z < -1.64
    
    if es_alteracion:
        severidad = "Leve"
        if dlco_z < -2.5:
            severidad = "Moderada"
        if dlco_z < -3.0:
            severidad = "Severa"
        
        # Determinar tipo de alteración
        if dlco_z < -1.64 and va_z < -1.64:
            tipo = f"Alteración de difusión {severidad} con reducción de volumen alveolar"
        elif dlco_z < -1.64 and kco_z < -1.64:
            tipo = f"Alteración de difusión {severidad} con reducción de transferencia"
        else:
            tipo = f"Alteración de difusión {severidad}"
        
        return True, tipo
    
    return False, "Difusión normal"

def detectar_broncodilatacion_significativa(datos):
    """
    Detecta respuesta significativa a broncodilatador usando doble umbral y preferencia FEV1.
    """
    fev1_pre = datos.get('FEV1 pre')
    fev1_post = datos.get('FEV1 post')
    fvc_pre = datos.get('FVC pre')
    fvc_post = datos.get('FVC post')
    
    if fev1_pre and fev1_post and fvc_pre and fvc_post:
        # Verificar que no sean "Valor no encontrado"
        if (fev1_pre == 'Valor no encontrado' or fev1_post == 'Valor no encontrado' or
            fvc_pre == 'Valor no encontrado' or fvc_post == 'Valor no encontrado'):
            return False, "Datos de broncodilatación insuficientes"
        try:
            fev1_pre = float(fev1_pre)
            fev1_post = float(fev1_post)
            fvc_pre = float(fvc_pre)
            fvc_post = float(fvc_post)
            
            # Cambios porcentuales y absolutos
            cambio_fev1 = ((fev1_post - fev1_pre) / fev1_pre) * 100
            cambio_fvc = ((fvc_post - fvc_pre) / fvc_pre) * 100
            delta_fev1_ml = (fev1_post - fev1_pre) * 1000
            delta_fvc_ml = (fvc_post - fvc_pre) * 1000
            
            # Doble umbral
            respuesta_fev1 = cambio_fev1 >= 12 and delta_fev1_ml >= 200
            respuesta_fvc = cambio_fvc >= 12 and delta_fvc_ml >= 200
            respuesta_fev1_400 = delta_fev1_ml >= 400
            
            if respuesta_fev1:
                if respuesta_fev1_400:
                    return True, f"Broncodilatación positiva por FEV₁ (+{cambio_fev1:.1f}%, {delta_fev1_ml:.0f} mL, >400 mL: alta probabilidad de asma)"
                return True, f"Broncodilatación positiva por FEV₁ (+{cambio_fev1:.1f}%, {delta_fev1_ml:.0f} mL)"
            elif respuesta_fvc:
                return True, f"Broncodilatación positiva por FVC (+{cambio_fvc:.1f}%, {delta_fvc_ml:.0f} mL)"
            else:
                return False, f"Sin respuesta significativa: FEV₁ +{cambio_fev1:.1f}%, {delta_fev1_ml:.0f} mL; FVC +{cambio_fvc:.1f}%, {delta_fvc_ml:.0f} mL. No usar FEV₁/FVC para determinar positividad."
        except (ValueError, ZeroDivisionError):
            return False, "Error en cálculo de broncodilatación"
    return False, "Datos de broncodilatación insuficientes"

def generar_diagnostico_patron(resultados_espiro, resultados_dlco, resultados_vol, datos):
    """
    Genera diagnóstico de patrón basado en todos los resultados
    """
    diagnostico = []
    patrones = []
    
    # Detectar patrones ventilatorios
    es_obstructivo, desc_obstructivo = detectar_patron_obstructivo(resultados_espiro, resultados_vol)
    es_restrictivo, desc_restrictivo = detectar_patron_restrictivo(resultados_espiro, resultados_vol)
    es_mixto, desc_mixto = detectar_patron_mixto(resultados_espiro, resultados_vol)
    
    if es_mixto:
        patrones.append("🔄 Mixto")
        diagnostico.append(desc_mixto)
    elif es_obstructivo:
        patrones.append("🫁 Obstructivo")
        diagnostico.append(desc_obstructivo)
    elif es_restrictivo:
        patrones.append("📏 Restrictivo")
        diagnostico.append(desc_restrictivo)
    else:
        patrones.append("✅ Normal")
        diagnostico.append("Patrón ventilatorio normal")
    
    # Detectar alteración de difusión
    es_alteracion_difusion, desc_difusion = detectar_alteracion_difusion(resultados_dlco)
    if es_alteracion_difusion:
        patrones.append("🩸 Alteración difusión")
        diagnostico.append(desc_difusion)
    else:
        diagnostico.append("Difusión normal")
    
    # Detectar broncodilatación
    es_broncodilatacion, desc_broncodilatacion = detectar_broncodilatacion_significativa(datos)
    if es_broncodilatacion:
        patrones.append("💨 Broncodilatación +")
        diagnostico.append(desc_broncodilatacion)
    else:
        diagnostico.append("Sin respuesta significativa a broncodilatador")
    
    return patrones, diagnostico

def mostrar_deteccion_patrones(resultados_espiro, resultados_dlco, resultados_vol, datos):
    """
    Muestra la detección de patrones de enfermedad
    """
    st.markdown("## 🔍 Detección de Patrones de Enfermedad")
    
    # Generar diagnóstico
    patrones, diagnostico = generar_diagnostico_patron(resultados_espiro, resultados_dlco, resultados_vol, datos)
    
    # Mostrar patrones detectados
    st.markdown("### 📊 Patrones Detectados")
    
    # Crear tarjetas de patrones
    cols = st.columns(len(patrones))
    for i, patron in enumerate(patrones):
        with cols[i]:
            # Determinar color basado en el patrón
            if "Normal" in patron:
                color = "green"
            elif "Obstructivo" in patron or "Restrictivo" in patron or "Mixto" in patron:
                color = "orange"
            elif "Alteración" in patron:
                color = "red"
            else:
                color = "blue"
            
            st.markdown(f"""
            <div class="metric-card status-{color}">
                <h4>{patron}</h4>
            </div>
            """, unsafe_allow_html=True)
    
    # Mostrar diagnóstico detallado
    st.markdown("### 📋 Diagnóstico Detallado")
    
    for i, desc in enumerate(diagnostico):
        if "normal" in desc.lower():
            st.success(f"✅ {desc}")
        elif "error" in desc.lower() or "insuficientes" in desc.lower():
            st.warning(f"⚠️ {desc}")
        else:
            st.info(f"🔍 {desc}")
    
    # Interpretación clínica
    st.markdown("### 🎯 Interpretación Clínica")
    
    if "Obstructivo" in str(patrones):
        st.markdown("""
        **🫁 Patrón Obstructivo:**
        - Posibles diagnósticos: EPOC, asma, bronquiectasias
        - Considerar: espirometría post-broncodilatador, test de provocación
        - Seguimiento: función pulmonar anual, ajuste de tratamiento
        """)
    
    if "Restrictivo" in str(patrones):
        st.markdown("""
        **📏 Patrón Restrictivo:**
        - Posibles diagnósticos: fibrosis pulmonar, sarcoidosis, neumonía
        - Considerar: TAC de tórax, biopsia pulmonar, estudio de autoinmunidad
        - Seguimiento: función pulmonar cada 3-6 meses
        """)
    
    if "Mixto" in str(patrones):
        st.markdown("""
        **🔄 Patrón Mixto:**
        - Posibles diagnósticos: EPOC avanzado, fibrosis quística, enfermedades intersticiales
        - Considerar: evaluación multidisciplinaria, estudio completo
        - Seguimiento: función pulmonar frecuente, ajuste de tratamiento
        """)
    
    if "Alteración difusión" in str(patrones):
        st.markdown("""
        **🩸 Alteración de Difusión:**
        - Posibles causas: enfermedad intersticial, embolismo pulmonar, anemia
        - Considerar: TAC de tórax, ecocardiografía, estudio de coagulación
        - Seguimiento: DLCO seriada, evaluación cardiológica
        """)
    
    if "Broncodilatación +" in str(patrones):
        st.markdown("""
        **💨 Respuesta a Broncodilatador:**
        - Posibles diagnósticos: asma, EPOC con componente reversible
        - Considerar: optimización de tratamiento broncodilatador
        - Seguimiento: función pulmonar con tratamiento
        """) 