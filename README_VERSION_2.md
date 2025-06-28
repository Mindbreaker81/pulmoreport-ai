# PulmoReport AI - Versión 2.0 Visual

## 📋 Descripción del Proyecto
Versión mejorada de la aplicación de análisis inteligente de informes de funcionalismo pulmonar con **visualización avanzada** y **interfaz gráfica moderna**.

## 🎨 Nuevas Características Visuales

### 1. **Gráficos Interactivos con Plotly**
- **📊 Gráficos de barras** para espirometría, DLCO y volúmenes
- **🎯 Colores automáticos** basados en z-scores (verde=normal, amarillo=leve, rojo=severo)
- **📈 Líneas de referencia** para valores esperados
- **💨 Gráficos de broncodilatación** con comparación pre/post

### 2. **Semáforo de Interpretación**
- **🟢 Verde**: Función normal
- **🟡 Amarillo**: Alteración leve
- **🔴 Rojo**: Alteración severa
- **📊 Análisis automático** de todos los parámetros

### 3. **Diseño Moderno**
- **🎨 Tema personalizado** con CSS
- **📱 Layout responsive** y adaptativo
- **🎯 Interfaz intuitiva** con pestañas organizadas
- **🔄 Sistema de limpieza** mejorado

## 🚀 Funcionalidades Implementadas

### **Análisis Visual Completo:**
- **📊 Espirometría**: Gráficos de FEV1, FVC, FEF25-75% con colores por severidad
- **🫁 DLCO**: Visualización de DLCO, KCO, VA con indicadores de alteración
- **📏 Volúmenes**: Gráficos de TLC, VC, RV, RV/TLC con interpretación visual
- **💨 Broncodilatación**: Comparación visual pre/post con porcentajes de cambio

### **Sistema de Semáforos:**
- **🟢 Función Normal**: Todos los parámetros dentro del rango normal
- **🟡 Alteración Leve**: Al menos un parámetro con alteración leve
- **🔴 Alteración Severa**: Al menos un parámetro con alteración severa

## 📁 Estructura del Proyecto

```
version_2_visual/
├── app.py                          # Aplicación principal con visualización
├── requirements.txt                # Dependencias actualizadas
├── utils/
│   ├── analisis_gli.py            # Módulo de análisis GLI
│   ├── extraccion.py              # Módulo de extracción
│   └── extraccion_backup.py       # Backup del extractor
├── Archivos de datos GLI:
│   ├── lookuptables.xls           # Tablas GLI 2012 espirometría
│   ├── lookuptablesdlco.xlsx      # Tablas GLI 2017 DLCO
│   ├── lookuptablesvol.xlsx       # Tablas GLI 2021 volúmenes
│   ├── coefdlco.txt               # Coeficientes DLCO
│   └── formvol.xls                # Coeficientes volúmenes
└── Archivos de prueba:
    ├── test_analisis.py           # Test de análisis
    ├── test_app_completa.py       # Test completo
    └── prueba.pdf                 # PDF de ejemplo
```

## 🔧 Instalación y Uso

### Requisitos Actualizados
- Python 3.8+
- Streamlit
- pandas
- pdfplumber
- openpyxl
- **plotly** (nuevo)
- **streamlit-plotly-events** (nuevo)
- **Pillow** (nuevo)

### Instalación
```bash
pip install -r requirements.txt
```

### Ejecución
```bash
streamlit run app.py
```

## 🎯 Características Técnicas

### **Visualización Avanzada:**
- **Plotly Graph Objects**: Gráficos interactivos y responsivos
- **Colores Dinámicos**: Basados en z-scores y severidad
- **Anotaciones Automáticas**: Porcentajes y valores en los gráficos
- **Templates Modernos**: Diseño limpio y profesional

### **Sistema de Colores:**
- **🟢 Verde (#28a745)**: Z-score ≥ -1.64 (Normal)
- **🟡 Amarillo (#ffc107)**: Z-score entre -2.5 y -1.64 (Leve)
- **🔴 Rojo (#dc3545)**: Z-score < -2.5 (Moderado/Severo)

### **Gráficos Específicos:**
1. **Espirometría**: Barras con valores observados vs línea de esperados
2. **DLCO**: Visualización de capacidad de difusión
3. **Volúmenes**: Análisis de volúmenes pulmonares
4. **Broncodilatación**: Comparación pre/post con cambios porcentuales

## 📊 Mejoras de Usabilidad

### **Interfaz Mejorada:**
- **Header Personalizado**: Diseño moderno y atractivo
- **Botón de Limpieza**: Centrado y más visible
- **Pestañas Organizadas**: Navegación intuitiva
- **Responsive Design**: Adaptable a diferentes pantallas

### **Información Visual:**
- **Semáforo Central**: Indicador rápido del estado general
- **Gráficos Interactivos**: Zoom, pan, hover information
- **Colores Intuitivos**: Interpretación inmediata del estado
- **Anotaciones Claras**: Valores y porcentajes visibles

## 🔄 Control de Versiones
- **Versión 1.0**: Implementación básica funcional
- **Versión 2.0**: Visualización avanzada y diseño moderno
- **Sistema de backup**: Versiones anteriores preservadas

## 📞 Soporte
Proyecto desarrollado para análisis clínico de funcionalismo pulmonar con **interpretaciones visuales** basadas en las guías GLI más actuales.

---
**Fecha de creación**: 22 de junio de 2025
**Versión**: 2.0 Visual
**Estado**: Completado y funcional con visualización avanzada 