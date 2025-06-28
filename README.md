# 🫁 PulmoReport AI

**Análisis Inteligente de Funcionalismo Pulmonar con Dashboard Avanzado**

Una aplicación web desarrollada con Streamlit que permite el análisis automático de informes de funcionalismo pulmonar en formato PDF, utilizando ecuaciones GLI (Global Lung Function Initiative) para interpretación clínica precisa.

## 🚀 Características Principales

### 📊 Dashboard Overview
- **Métricas clave**: Z-score global, porcentaje de anormalidad, parámetros anormales
- **Indicadores visuales**: Colores dinámicos según severidad (verde, naranja, rojo)
- **Diseño moderno**: Tarjetas con gradientes y diseño responsivo

### 📈 Análisis Comparativo Temporal
- **Múltiples PDFs**: Procesamiento simultáneo para seguimiento temporal
- **Gráficos de evolución**: Visualización de progreso de parámetros
- **Comparación de Z-scores**: Tabla comparativa entre diferentes fechas

### 🔍 Detección Automática de Patrones
- **Patrón obstructivo**: Basado en FEV1, FEV1/FVC y TLC
- **Patrón restrictivo**: Identificación por FVC, TLC y ratios
- **Patrón mixto**: Combinación de patrones
- **Alteración de difusión**: Análisis de DLCO, KCO y VA
- **Respuesta broncodilatadora**: Detección de cambios significativos

### 📋 Extracción Automática de Datos
- **Datos demográficos**: Edad, sexo, altura, peso, etnia
- **Espirometría**: FVC, FEV1, FEV1/FVC, FEF25-75%, PEF
- **Difusión pulmonar**: DLCO, VA, DLCO/VA, KCO
- **Volúmenes pulmonares**: TLC, VC, RV, RV/TLC
- **FeNO**: Óxido nítrico exhalado

## 🛠️ Instalación

### Requisitos Previos
- Python 3.7 o superior
- pip (gestor de paquetes de Python)

### Instalación Local

1. **Clonar el repositorio**:
```bash
git clone https://github.com/tu-usuario/pulmoreport-ai.git
cd pulmoreport-ai
```

2. **Crear entorno virtual** (recomendado):
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

4. **Ejecutar la aplicación**:
```bash
streamlit run version_3_dashboard/app_clean.py
```

5. **Abrir en el navegador**:
La aplicación se abrirá automáticamente en `http://localhost:8501`

## 🌐 Despliegue en la Nube

### Streamlit Cloud (Recomendado)

1. **Fork este repositorio** en tu cuenta de GitHub
2. Ve a [Streamlit Cloud](https://streamlit.io/cloud)
3. Conecta tu cuenta de GitHub
4. Selecciona el repositorio `pulmoreport-ai`
5. Configura:
   - **Main file path**: `version_3_dashboard/app_clean.py`
   - **Python version**: 3.9
6. Haz clic en "Deploy"

### Heroku

1. **Crear archivos de configuración**:

`Procfile`:
```
web: streamlit run version_3_dashboard/app_clean.py --server.port=$PORT --server.address=0.0.0.0
```

`runtime.txt`:
```
python-3.9.18
```

2. **Desplegar en Heroku**:
```bash
heroku create tu-app-name
git push heroku main
```

## 📖 Uso de la Aplicación

### Análisis Individual
1. **Subir PDF**: Arrastra o selecciona un archivo PDF de funcionalismo pulmonar
2. **Ver Dashboard**: Métricas clave y estado general
3. **Explorar pestañas**: Espirometría, DLCO, Volúmenes, Patrones
4. **Exportar reporte**: Genera PDF con resultados completos

### Análisis Comparativo
1. **Subir múltiples PDFs**: Selecciona varios archivos del mismo paciente
2. **Ver evolución temporal**: Gráficos de progreso automáticos
3. **Comparar Z-scores**: Tabla de comparación entre fechas
4. **Interpretar tendencias**: Mejora o deterioro de parámetros

## 🏥 Aplicaciones Clínicas

### Para Médicos Especialistas
- **Interpretación rápida**: Dashboard con métricas clave
- **Seguimiento temporal**: Evolución de pacientes
- **Detección automática**: Patrones de enfermedad
- **Recomendaciones clínicas**: Sugerencias específicas

### Para Centros de Función Pulmonar
- **Estandarización**: Interpretación basada en GLI
- **Eficiencia**: Análisis automático de informes
- **Calidad**: Reducción de errores de interpretación
- **Documentación**: Reportes profesionales

## 🔬 Base Científica

### Ecuaciones GLI 2012
- **Espirometría**: FEV1, FVC, FEF25-75%
- **Cálculo de Z-scores**: Valores estandarizados por edad, sexo, altura y etnia
- **Límites de normalidad**: LLN (Lower Limit of Normal) = -1.64 Z-score

### Criterios de Interpretación
- **Severidad**: Basada en Z-scores (leve, moderada, severa, muy severa)
- **Patrones**: Criterios clínicos establecidos
- **Broncodilatación**: ≥12% y ≥200ml de mejora

## 📊 Estructura del Proyecto

```
pulmoreport-ai/
├── version_3_dashboard/
│   ├── app_clean.py           # Aplicación principal
│   ├── patrones_functions.py  # Funciones de detección de patrones
│   ├── requirements.txt       # Dependencias
│   └── utils/
│       ├── extraccion.py      # Extracción de datos PDF
│       └── analisis_gli.py    # Análisis GLI y cálculos
├── lookuptables*.xlsx         # Tablas de referencia GLI
├── coefdlco.txt              # Coeficientes DLCO
└── README.md
```

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crea un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👨‍⚕️ Autor

**Dr. Edmundo Rosales Mayor**
- Especialista en Medicina Interna y Neumología
- Desarrollador de aplicaciones médicas

## 🔗 Enlaces Útiles

- [Global Lung Function Initiative](https://www.ers-education.org/gli/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Reportar Issues](https://github.com/tu-usuario/pulmoreport-ai/issues)

## ⚠️ Disclaimer

Esta aplicación es una herramienta de apoyo diagnóstico. Los resultados deben ser siempre interpretados por un profesional médico calificado. No reemplaza el juicio clínico ni la evaluación médica integral.

---

**PulmoReport AI** - Transformando el análisis de función pulmonar con inteligencia artificial 🫁✨ 