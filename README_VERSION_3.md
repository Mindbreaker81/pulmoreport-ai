# PulmoReport AI - Versión 3 Dashboard

## 🚀 Nuevas Características Implementadas

### 1. 📊 Dashboard Overview con Métricas Clave
- **Métricas principales**: Peor Z-score global, porcentaje de anormalidad, total de parámetros, parámetros anormales
- **Métricas por categoría**: Espirometría, DLCO, Volúmenes con sus respectivos Z-scores
- **Indicadores visuales**: Colores dinámicos según severidad (verde, naranja, rojo)
- **Diseño responsivo**: Tarjetas con gradientes y sombras para mejor UX

### 2. 📈 Comparación Temporal de Múltiples PDFs
- **Procesamiento múltiple**: Análisis simultáneo de varios PDFs
- **Evolución temporal**: Gráficos de evolución para parámetros seleccionados
- **Visualización dual**: Valores observados y Z-scores en gráficos separados
- **Tabla comparativa**: Comparación de Z-scores entre diferentes fechas
- **Extracción de fechas**: Automática desde nombres de archivos

### 3. 🔍 Detección de Patrones de Enfermedad
- **Patrón obstructivo**: Detección automática basada en FEV1, FEV1/FVC y TLC
- **Patrón restrictivo**: Identificación por FVC, TLC y ratio FEV1/FVC
- **Patrón mixto**: Combinación de patrones obstructivo y restrictivo
- **Alteración de difusión**: Análisis de DLCO, KCO y VA
- **Broncodilatación**: Detección de respuesta significativa
- **Interpretación clínica**: Recomendaciones específicas por patrón

## 🛠️ Funcionalidades Técnicas

### Dashboard Overview
```python
def crear_metricas_dashboard(datos, resultados_espiro, resultados_dlco, resultados_vol):
    # Calcula métricas clave para el dashboard
    # Retorna diccionario con todas las métricas

def mostrar_dashboard_overview(metricas):
    # Muestra el dashboard con tarjetas visuales
    # Colores dinámicos según severidad
```

### Comparación Temporal
```python
def procesar_multiples_pdfs(uploaded_files):
    # Procesa múltiples PDFs para comparación
    # Extrae fechas y almacena resultados

def crear_grafico_evolucion_temporal(resultados_multiples, parametro):
    # Crea gráficos de evolución temporal
    # Dos subplots: valores observados y Z-scores

def mostrar_comparacion_temporal(resultados_multiples):
    # Muestra comparación completa
    # Tabla de archivos y gráficos de evolución
```

### Detección de Patrones
```python
def detectar_patron_obstructivo(resultados_espiro, resultados_vol):
    # Detecta patrón obstructivo con criterios clínicos

def detectar_patron_restrictivo(resultados_espiro, resultados_vol):
    # Detecta patrón restrictivo

def detectar_patron_mixto(resultados_espiro, resultados_vol):
    # Detecta patrón mixto

def detectar_alteracion_difusion(resultados_dlco):
    # Detecta alteración de difusión

def detectar_broncodilatacion_significativa(datos):
    # Detecta respuesta a broncodilatador

def generar_diagnostico_patron(resultados_espiro, resultados_dlco, resultados_vol, datos):
    # Genera diagnóstico completo de patrones

def mostrar_deteccion_patrones(resultados_espiro, resultados_dlco, resultados_vol, datos):
    # Muestra detección de patrones con interpretación clínica
```

## 📋 Criterios de Detección

### Patrón Obstructivo
- FEV1 < LLN (-1.64)
- FEV1/FVC < 0.7
- TLC normal o aumentado (≥ -1.64)

### Patrón Restrictivo
- FVC < LLN (-1.64)
- TLC < LLN (-1.64)
- FEV1/FVC normal o aumentado (≥ 0.7)

### Patrón Mixto
- Criterios de obstructivo Y restrictivo simultáneamente

### Alteración de Difusión
- DLCO < LLN (-1.64)
- Clasificación por severidad y tipo

### Broncodilatación Significativa
- FEV1: ≥ 12% y ≥ 200ml
- FVC: ≥ 12% y ≥ 200ml

## 🎨 Mejoras de UI/UX

### Dashboard Metrics
- Gradientes de color atractivos
- Indicadores de estado con colores
- Diseño responsivo con columnas
- Sombras y bordes redondeados

### Comparación Temporal
- Gráficos duales (valores + Z-scores)
- Líneas de referencia (LLN, predicho, severidad)
- Anotaciones de valores en gráficos
- Tabla comparativa clara

### Detección de Patrones
- Tarjetas de patrones con colores
- Diagnóstico detallado con iconos
- Interpretación clínica estructurada
- Recomendaciones específicas

## 🔧 Instalación y Uso

1. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

2. **Ejecutar la aplicación**:
```bash
streamlit run app.py
```

3. **Subir PDFs**:
   - Un archivo: Análisis individual con dashboard
   - Múltiples archivos: Comparación temporal automática

## 📊 Flujo de Trabajo

1. **Subida de archivos**: Soporte para múltiples PDFs
2. **Dashboard overview**: Métricas clave inmediatas
3. **Comparación temporal**: Si hay múltiples archivos
4. **Análisis individual**: Pestañas detalladas por archivo
5. **Detección de patrones**: En la pestaña de resumen
6. **Exportación PDF**: Reporte completo

## 🎯 Beneficios Clínicos

### Para Médicos
- **Vista rápida**: Dashboard con métricas clave
- **Evolución temporal**: Seguimiento de pacientes
- **Detección automática**: Patrones de enfermedad
- **Interpretación clínica**: Recomendaciones específicas

### Para Pacientes
- **Visualización clara**: Gráficos intuitivos
- **Evolución temporal**: Progreso del tratamiento
- **Información estructurada**: Patrones y recomendaciones

## 🔮 Próximas Mejoras

- **Base de datos de casos**: Almacenamiento de historiales
- **Modo oscuro**: Tema alternativo
- **Optimizaciones técnicas**: Mejoras de rendimiento
- **Análisis predictivo**: Tendencias futuras
- **Integración con PACS**: Conexión con sistemas hospitalarios

---

**Desarrollado por**: Edmundo Rosales Mayor  
**Versión**: 3.0 Dashboard  
**Fecha**: 2025 