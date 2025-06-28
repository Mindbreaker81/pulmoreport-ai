import math
import pandas as pd
from typing import Dict, Tuple

# Variables globales para almacenar las tablas de lookup
gli_tables = {}
gli_coefficients = {}
gli_dlco_tables = {}
gli_vol_tables = {}

# Coeficientes fijos para ecuaciones GLI 2017 DLCO
DLCO_COEFFICIENTS = {
    'males': {'a': -7.034920, 'p': 2.018368, 'q': 0.012425},
    'females': {'a': -5.159451, 'p': 1.618697, 'q': 0.015390}
}

KCO_COEFFICIENTS = {
    'males': {'a': 4.088408, 'p': 0.415334, 'q': 0.113166},
    'females': {'a': 5.131492, 'p': 0.645656, 'q': 0.097395}
}

VA_COEFFICIENTS = {
    'males': {'a': -11.086573, 'p': 2.430021, 'q': 0.097047},
    'females': {'a': -9.873970, 'p': 2.182316, 'q': 0.082868}
}

# Coeficientes fijos para ecuaciones GLI 2021 Volúmenes
TLC_COEFFICIENTS = {
    'males': {'a': -10.5861, 'p': 0.1433, 'q': 2.3155},
    'females': {'a': -10.1128, 'p': 0.1062, 'q': 2.2259}
}

VC_COEFFICIENTS = {
    'males': {'a': -10.134371, 'p': -0.003532, 'q': 2.307980},
    'females': {'a': -9.230600, 'p': -0.005517, 'q': 2.116822}
}

RV_COEFFICIENTS = {
    'males': {'a': -2.37211, 'p': 0.01346, 'q': 0.01307},
    'females': {'a': -2.50593, 'p': 0.01307, 'q': 0.01379}
}

RVTLC_COEFFICIENTS = {
    'males': {'a': 2.634, 'p': 0.01302, 'q': -0.00008862},
    'females': {'a': 2.666, 'p': 0.01411, 'q': -0.00003689}
}

def cargar_tablas_gli():
    """
    Carga las tablas de lookup de GLI 2012 desde el archivo Excel.
    """
    global gli_tables, gli_coefficients
    try:
        excel_file = 'lookuptables.xlsx'
        # Nombres de hoja exactos según el archivo
        sheet_names = {
            'fev1_males': 'FEV1 males',
            'fev1_females': 'FEV1 females',
            'fvc_males': 'FVC males',
            'fvc_females': 'FVC females',
            'fef2575_males': 'FEF2575 males',
            'fef2575_females': 'FEF2575 females'
        }
        
        for key, sheet in sheet_names.items():
            try:
                # Leer columnas: B (edad), C (Lspline), D (Mspline), E (Sspline)
                gli_tables[key] = pd.read_excel(excel_file, sheet_name=sheet, header=None, skiprows=4, usecols=[1, 2, 3, 4], engine='openpyxl')
                gli_tables[key].columns = ['age', 'Lspline', 'Mspline', 'Sspline']
                
                # Leer coeficientes a0-a5 y p0-p5 una sola vez por hoja
                original_table = pd.read_excel(excel_file, sheet_name=sheet, header=None, skiprows=4, engine='openpyxl')
                
                # Coeficientes a0-a5 (columna 8, filas 3-5)
                a0 = float(original_table.iloc[3, 8])  # a0
                a1 = float(original_table.iloc[4, 8])  # a1
                a2 = float(original_table.iloc[5, 8])  # a2
                a3 = 0.0  # No existe en el archivo
                a4 = 0.0  # No existe en el archivo
                a5 = 0.0  # No existe en el archivo
                
                # Coeficientes p0-p5 (columna 11, filas 3, 5)
                p0 = float(original_table.iloc[3, 11])  # p0
                p1 = float(original_table.iloc[5, 11])  # p1
                p2 = 0.0  # No existe en el archivo
                p3 = 0.0  # No existe en el archivo
                p4 = 0.0  # No existe en el archivo
                p5 = 0.0  # No existe en el archivo
                
                # Almacenar coeficientes
                gli_coefficients[key] = (a0, a1, a2, a3, a4, a5, p0, p1, p2, p3, p4, p5)
                
            except Exception as sheet_error:
                print(f"Error cargando hoja {sheet} del archivo {excel_file}: {sheet_error}")
                return False
                
        return True
    except Exception as e:
        print(f"Error general cargando tablas GLI: {e}")
        print("Asegúrate de que el archivo 'lookuptables.xlsx' esté presente y que openpyxl esté instalado correctamente.")
        return False

def cargar_tablas_dlco():
    """
    Carga las tablas de lookup de DLCO desde el archivo Excel.
    """
    global gli_dlco_tables
    try:
        excel_file = 'lookuptablesdlco.xlsx'
        # Nombres de hoja para DLCO
        sheet_names = {
            'dlco_females': 'DLCO_f',
            'kco_females': 'KCO_f',
            'va_females': 'VA_f',
            'dlco_males': 'DLCO_m',
            'kco_males': 'KCO_m',
            'va_males': 'VA_m',
        }
        for key, sheet in sheet_names.items():
            # Leer columnas: B (edad, índice 1), C (Mspline, índice 2)
            df = pd.read_excel(excel_file, sheet_name=sheet, header=None, skiprows=1, usecols=[1,2])
            df.columns = ['age', 'Mspline']
            gli_dlco_tables[key] = df
        return True
    except Exception as e:
        print(f"Error cargando tablas DLCO: {e}")
        return False

def cargar_tablas_volumenes():
    """
    Carga las tablas de lookup de volúmenes desde el archivo Excel.
    """
    global gli_vol_tables
    try:
        excel_file = 'lookuptablesvol.xlsx'
        # Nombres de hoja para volúmenes (en minúsculas)
        sheet_names = {
            'tlc_males': 'tlc_m_lookuptable',
            'tlc_females': 'tlc_f_lookuptable',
            'vc_males': 'vc_m_lookuptable',
            'vc_females': 'vc_f_lookuptable',
            'rv_males': 'rv_m_lookuptable',
            'rv_females': 'rv_f_lookuptable',
            'rvtlc_males': 'rvtlc_m_lookuptable',
            'rvtlc_females': 'rvtlc_f_lookuptable'
        }
        for key, sheet in sheet_names.items():
            # Leer columnas: A (edad, índice 0), B (Mspline, índice 1)
            df = pd.read_excel(excel_file, sheet_name=sheet, header=None, skiprows=1, usecols=[0,1])
            df.columns = ['age', 'Mspline']
            gli_vol_tables[key] = df
        return True
    except Exception as e:
        print(f"Error cargando tablas volúmenes: {e}")
        return False

def obtener_spline_dlco(edad: float, sexo: str, parametro: str) -> float:
    """
    Obtiene el valor Mspline para DLCO, KCO o VA según la edad y sexo.
    """
    sexo_en = 'females' if 'femenino' in sexo.lower() else 'males'
    if parametro.lower() == 'dlco':
        key = f'dlco_{sexo_en}'
    elif parametro.lower() == 'kco':
        key = f'kco_{sexo_en}'
    elif parametro.lower() == 'va':
        key = f'va_{sexo_en}'
    else:
        raise ValueError('Parámetro DLCO no soportado')
    df = gli_dlco_tables[key]
    closest_row = df.iloc[(df['age'] - edad).abs().argsort()[:1]]
    mspline = float(closest_row.iloc[0]['Mspline'])
    return mspline

def calcular_valor_esperado_dlco(edad: float, altura: float, sexo: str) -> float:
    """
    Calcula el valor esperado de DLCO usando ecuaciones GLI 2017.
    ln(DLCO) = a + p*ln(altura) - q*ln(edad) + spline
    """
    sexo_en = 'females' if 'femenino' in sexo.lower() else 'males'
    coef = DLCO_COEFFICIENTS[sexo_en]
    spline = obtener_spline_dlco(edad, sexo, 'dlco')
    
    ln_altura = math.log(altura)
    ln_edad = math.log(edad)
    ln_valor = coef['a'] + coef['p'] * ln_altura - coef['q'] * ln_edad + spline
    
    return math.exp(ln_valor)

def calcular_valor_esperado_kco(edad: float, altura: float, sexo: str) -> float:
    """
    Calcula el valor esperado de KCO usando ecuaciones GLI 2017.
    ln(KCO) = a - p*ln(altura) - q*ln(edad) + spline
    """
    sexo_en = 'females' if 'femenino' in sexo.lower() else 'males'
    coef = KCO_COEFFICIENTS[sexo_en]
    spline = obtener_spline_dlco(edad, sexo, 'kco')
    
    ln_altura = math.log(altura)
    ln_edad = math.log(edad)
    ln_valor = coef['a'] - coef['p'] * ln_altura - coef['q'] * ln_edad + spline
    
    return math.exp(ln_valor)

def calcular_valor_esperado_va(edad: float, altura: float, sexo: str) -> float:
    """
    Calcula el valor esperado de VA usando ecuaciones GLI 2017.
    ln(VA) = a + p*ln(altura) + q*ln(edad) + spline
    """
    sexo_en = 'females' if 'femenino' in sexo.lower() else 'males'
    coef = VA_COEFFICIENTS[sexo_en]
    spline = obtener_spline_dlco(edad, sexo, 'va')
    
    ln_altura = math.log(altura)
    ln_edad = math.log(edad)
    ln_valor = coef['a'] + coef['p'] * ln_altura + coef['q'] * ln_edad + spline
    
    return math.exp(ln_valor)

def obtener_coeficientes_regresion(edad: float, sexo: str, parametro: str) -> tuple:
    """
    Obtiene los coeficientes a, p, q (fijos) y el spline (varía por edad) para el parámetro y sexo dados.
    """
    # Traducir sexo a inglés para construir el nombre de la hoja correcto
    sexo_en = 'females' if 'femenino' in sexo.lower() else 'males'
    if parametro == 'fvc':
        sheet = f'FVC {sexo_en}'
        spline_col = 3  # Columna D (Mspline)
    elif parametro == 'fev1':
        sheet = f'FEV1 {sexo_en}'
        spline_col = 3  # Columna D (Mspline)
    elif parametro == 'fef2575':
        sheet = f'FEF2575 {sexo_en}'
        spline_col = 2  # Columna C (Mspline)
    else:
        raise ValueError('Parámetro no soportado')

    # Leer el archivo completo sin eliminar filas
    df = pd.read_excel('lookuptables.xlsx', sheet_name=sheet, header=None, engine='openpyxl')
    
    # Coeficientes fijos (no cambian con la edad)
    # I4, I5, I6 corresponden a las filas 3, 4, 5 del Excel (índices 3, 4, 5)
    a = float(df.iloc[3, 8])   # I4 (fila 4 del Excel)
    p = float(df.iloc[4, 8])   # I5 (fila 5 del Excel)
    q = float(df.iloc[5, 8])   # I6 (fila 6 del Excel)
    
    # Buscar el spline para la edad específica (saltando las primeras 4 filas de encabezados)
    df_data = df.iloc[4:]  # Datos sin encabezados
    closest_row = df_data.iloc[(df_data[1] - edad).abs().argsort()[:1]]
    spline = float(closest_row.iloc[0, spline_col])
    
    return a, p, q, spline

def calcular_valor_esperado_fvc(edad: float, altura: float, sexo: str) -> float:
    a, p, q, spline = obtener_coeficientes_regresion(edad, sexo, 'fvc')
    ln_altura = math.log(altura)
    ln_edad = math.log(edad)
    ln_valor = a + p * ln_altura + q * ln_edad + spline
    return math.exp(ln_valor)

def calcular_valor_esperado_fev1(edad: float, altura: float, sexo: str) -> float:
    a, p, q, spline = obtener_coeficientes_regresion(edad, sexo, 'fev1')
    ln_altura = math.log(altura)
    ln_edad = math.log(edad)
    ln_valor = a + p * ln_altura + q * ln_edad + spline
    return math.exp(ln_valor)

def calcular_valor_esperado_fef2575(edad: float, altura: float, sexo: str) -> float:
    a, p, q, spline = obtener_coeficientes_regresion(edad, sexo, 'fef2575')
    ln_altura = math.log(altura)
    ln_edad = math.log(edad)
    ln_valor = a + p * ln_altura + q * ln_edad + spline
    return math.exp(ln_valor)

def calcular_z_score(valor_observado: float, valor_esperado: float, rse: float = 0.12) -> float:
    """
    Calcula el z-score usando la fórmula: (ln(observado) - ln(esperado)) / RSE
    RSE (Residual Standard Error) típico para espirometría es ~0.12
    """
    if valor_observado <= 0 or valor_esperado <= 0:
        return 0
    return (math.log(valor_observado) - math.log(valor_esperado)) / rse

def interpretar_z_score_con_severidad(z_score: float) -> Tuple[str, str]:
    """
    Interpreta el z-score con grado de severidad según criterios ATS/ERS.
    Retorna (interpretación, severidad)
    """
    if z_score >= -1.64:
        return "Normal", "Sin alteración"
    elif z_score >= -2.5:
        return "Ligeramente reducido", "Leve"
    elif z_score >= -4.0:
        return "Moderadamente reducido", "Moderada"
    elif z_score >= -6.0:
        return "Severamente reducido", "Severa"
    else:
        return "Muy severamente reducido", "Muy severa"

def analizar_espirometria(datos: Dict) -> Dict:
    """
    Analiza los datos de espirometría usando ecuaciones GLI.
    """
    try:
        edad = float(datos.get('Edad', 0))
        altura = float(datos.get('Altura', 0))
        sexo = datos.get('Sexo', 'Femenino')
        
        if edad <= 0 or altura <= 0:
            return {"error": "Datos insuficientes para análisis"}
        
        # Validar rango de edad y altura
        if edad < 3 or edad > 95:
            return {"error": "Edad fuera del rango válido (3-95 años)"}
        if altura < 100 or altura > 250:
            return {"error": "Altura fuera del rango válido (100-250 cm)"}
        
        # Cargar tablas si no están cargadas
        if not gli_tables:
            cargar_tablas_gli()
        if not gli_dlco_tables:
            cargar_tablas_dlco()
        if not gli_vol_tables:
            cargar_tablas_volumenes()
        
        resultados = {}
        
        # FEV1
        if datos.get('FEV1 pre') and datos.get('FEV1 pre') != 'Valor no encontrado':
            fev1_obs = float(datos['FEV1 pre'])
            fev1_esp = calcular_valor_esperado_fev1(edad, altura, sexo)
            fev1_z = calcular_z_score(fev1_obs, fev1_esp)
            interpretacion, severidad = interpretar_z_score_con_severidad(fev1_z)
            resultados['FEV1'] = {
                'observado': fev1_obs,
                'esperado': round(fev1_esp, 2),
                'z_score': round(fev1_z, 2),
                'interpretacion': interpretacion,
                'severidad': severidad
            }
        
        # FVC
        if datos.get('FVC pre') and datos.get('FVC pre') != 'Valor no encontrado':
            fvc_obs = float(datos['FVC pre'])
            fvc_esp = calcular_valor_esperado_fvc(edad, altura, sexo)
            fvc_z = calcular_z_score(fvc_obs, fvc_esp)
            interpretacion, severidad = interpretar_z_score_con_severidad(fvc_z)
            resultados['FVC'] = {
                'observado': fvc_obs,
                'esperado': round(fvc_esp, 2),
                'z_score': round(fvc_z, 2),
                'interpretacion': interpretacion,
                'severidad': severidad
            }
        
        # FEF25-75%
        if datos.get('FEF25-75% pre') and datos.get('FEF25-75% pre') != 'Valor no encontrado':
            fef_obs = float(datos['FEF25-75% pre'])
            fef_esp = calcular_valor_esperado_fef2575(edad, altura, sexo)
            fef_z = calcular_z_score(fef_obs, fef_esp)
            interpretacion, severidad = interpretar_z_score_con_severidad(fef_z)
            resultados['FEF25-75%'] = {
                'observado': fef_obs,
                'esperado': round(fef_esp, 2),
                'z_score': round(fef_z, 2),
                'interpretacion': interpretacion,
                'severidad': severidad
            }
        
        # DLCO
        if datos.get('DLCO pre') and datos.get('DLCO pre') != 'Valor no encontrado':
            dlco_obs = float(datos['DLCO pre'])
            dlco_esp = calcular_valor_esperado_dlco(edad, altura, sexo)
            dlco_z = calcular_z_score(dlco_obs, dlco_esp, rse=0.15)  # RSE específico para DLCO
            interpretacion, severidad = interpretar_z_score_con_severidad(dlco_z)
            resultados['DLCO'] = {
                'observado': dlco_obs,
                'esperado': round(dlco_esp, 2),
                'z_score': round(dlco_z, 2),
                'interpretacion': interpretacion,
                'severidad': severidad
            }
        
        # KCO (si está disponible)
        if datos.get('KCO pre') and datos.get('KCO pre') != 'Valor no encontrado':
            kco_obs = float(datos['KCO pre'])
            kco_esp = calcular_valor_esperado_kco(edad, altura, sexo)
            kco_z = calcular_z_score(kco_obs, kco_esp, rse=0.15)
            interpretacion, severidad = interpretar_z_score_con_severidad(kco_z)
            resultados['KCO'] = {
                'observado': kco_obs,
                'esperado': round(kco_esp, 2),
                'z_score': round(kco_z, 2),
                'interpretacion': interpretacion,
                'severidad': severidad
            }
        
        # VA (si está disponible)
        if datos.get('VA pre') and datos.get('VA pre') != 'Valor no encontrado':
            va_obs = float(datos['VA pre'])
            va_esp = calcular_valor_esperado_va(edad, altura, sexo)
            va_z = calcular_z_score(va_obs, va_esp, rse=0.12)
            interpretacion, severidad = interpretar_z_score_con_severidad(va_z)
            resultados['VA'] = {
                'observado': va_obs,
                'esperado': round(va_esp, 2),
                'z_score': round(va_z, 2),
                'interpretacion': interpretacion,
                'severidad': severidad
            }
        
        # TLC (si está disponible)
        if datos.get('TLC pre') and datos.get('TLC pre') != 'Valor no encontrado':
            tlc_obs = float(datos['TLC pre'])
            tlc_esp = calcular_valor_esperado_tlc(edad, altura, sexo)
            tlc_z = calcular_z_score(tlc_obs, tlc_esp, rse=0.12)
            interpretacion, severidad = interpretar_z_score_con_severidad(tlc_z)
            resultados['TLC'] = {
                'observado': tlc_obs,
                'esperado': round(tlc_esp, 2),
                'z_score': round(tlc_z, 2),
                'interpretacion': interpretacion,
                'severidad': severidad
            }
        
        # VC (si está disponible)
        if datos.get('VC pre') and datos.get('VC pre') != 'Valor no encontrado':
            vc_obs = float(datos['VC pre'])
            vc_esp = calcular_valor_esperado_vc(edad, altura, sexo)
            vc_z = calcular_z_score(vc_obs, vc_esp, rse=0.12)
            interpretacion, severidad = interpretar_z_score_con_severidad(vc_z)
            resultados['VC'] = {
                'observado': vc_obs,
                'esperado': round(vc_esp, 2),
                'z_score': round(vc_z, 2),
                'interpretacion': interpretacion,
                'severidad': severidad
            }
        
        # RV (si está disponible)
        if datos.get('RV pre') and datos.get('RV pre') != 'Valor no encontrado':
            rv_obs = float(datos['RV pre'])
            rv_esp = calcular_valor_esperado_rv(edad, altura, sexo)
            rv_z = calcular_z_score(rv_obs, rv_esp, rse=0.15)
            interpretacion, severidad = interpretar_z_score_con_severidad(rv_z)
            resultados['RV'] = {
                'observado': rv_obs,
                'esperado': round(rv_esp, 2),
                'z_score': round(rv_z, 2),
                'interpretacion': interpretacion,
                'severidad': severidad
            }
        
        # RV/TLC (si está disponible)
        if datos.get('RV/TLC pre') and datos.get('RV/TLC pre') != 'Valor no encontrado':
            rvtlc_obs = float(datos['RV/TLC pre'])
            rvtlc_esp = calcular_valor_esperado_rvtlc(edad, altura, sexo)
            rvtlc_z = calcular_z_score(rvtlc_obs, rvtlc_esp, rse=0.15)
            interpretacion, severidad = interpretar_z_score_con_severidad(rvtlc_z)
            resultados['RV/TLC'] = {
                'observado': rvtlc_obs,
                'esperado': round(rvtlc_esp, 2),
                'z_score': round(rvtlc_z, 2),
                'interpretacion': interpretacion,
                'severidad': severidad
            }
        
        return resultados
        
    except Exception as e:
        return {"error": f"Error en análisis: {str(e)}"}

def analizar_dlco(datos: Dict) -> Dict:
    """
    Analiza específicamente los datos de DLCO usando ecuaciones GLI.
    """
    try:
        edad = float(datos.get('Edad', 0))
        altura = float(datos.get('Altura', 0))
        sexo = datos.get('Sexo', 'Femenino')
        
        if edad <= 0 or altura <= 0:
            return {"error": "Datos insuficientes para análisis"}
        
        # Validar rango de edad y altura
        if edad < 5 or edad > 90:  # Rango específico para DLCO
            return {"error": "Edad fuera del rango válido para DLCO (5-90 años)"}
        if altura < 100 or altura > 250:
            return {"error": "Altura fuera del rango válido (100-250 cm)"}
        
        # Cargar tablas DLCO si no están cargadas
        if not gli_dlco_tables:
            cargar_tablas_dlco()
        
        resultados = {}
        
        # DLCO
        if datos.get('DLCO pre') and datos.get('DLCO pre') != 'Valor no encontrado':
            dlco_obs = float(datos['DLCO pre'])
            dlco_esp = calcular_valor_esperado_dlco(edad, altura, sexo)
            dlco_z = calcular_z_score(dlco_obs, dlco_esp, rse=0.15)
            interpretacion, severidad = interpretar_z_score_con_severidad(dlco_z)
            resultados['DLCO'] = {
                'observado': dlco_obs,
                'esperado': round(dlco_esp, 2),
                'z_score': round(dlco_z, 2),
                'interpretacion': interpretacion,
                'severidad': severidad
            }
        
        # KCO
        if datos.get('KCO pre') and datos.get('KCO pre') != 'Valor no encontrado':
            kco_obs = float(datos['KCO pre'])
            kco_esp = calcular_valor_esperado_kco(edad, altura, sexo)
            kco_z = calcular_z_score(kco_obs, kco_esp, rse=0.15)
            interpretacion, severidad = interpretar_z_score_con_severidad(kco_z)
            resultados['KCO'] = {
                'observado': kco_obs,
                'esperado': round(kco_esp, 2),
                'z_score': round(kco_z, 2),
                'interpretacion': interpretacion,
                'severidad': severidad
            }
        
        # VA
        if datos.get('VA pre') and datos.get('VA pre') != 'Valor no encontrado':
            va_obs = float(datos['VA pre'])
            va_esp = calcular_valor_esperado_va(edad, altura, sexo)
            va_z = calcular_z_score(va_obs, va_esp, rse=0.12)
            interpretacion, severidad = interpretar_z_score_con_severidad(va_z)
            resultados['VA'] = {
                'observado': va_obs,
                'esperado': round(va_esp, 2),
                'z_score': round(va_z, 2),
                'interpretacion': interpretacion,
                'severidad': severidad
            }
        
        return resultados
        
    except Exception as e:
        return {"error": f"Error en análisis DLCO: {str(e)}"}

def obtener_spline_volumen(edad: float, sexo: str, parametro: str) -> float:
    """
    Obtiene el valor Mspline para volúmenes según la edad y sexo.
    """
    sexo_en = 'females' if 'femenino' in sexo.lower() else 'males'
    if parametro.lower() == 'tlc':
        key = f'tlc_{sexo_en}'
    elif parametro.lower() == 'vc':
        key = f'vc_{sexo_en}'
    elif parametro.lower() == 'rv':
        key = f'rv_{sexo_en}'
    elif parametro.lower() == 'rvtlc':
        key = f'rvtlc_{sexo_en}'
    else:
        raise ValueError('Parámetro volumen no soportado')
    
    df = gli_vol_tables[key]
    closest_row = df.iloc[(df['age'] - edad).abs().argsort()[:1]]
    mspline = float(closest_row.iloc[0]['Mspline'])
    return mspline

def calcular_valor_esperado_tlc(edad: float, altura: float, sexo: str) -> float:
    """
    Calcula el valor esperado de TLC usando ecuaciones GLI 2021.
    ln(TLC) = a + p*ln(edad) + q*ln(altura) + spline
    """
    sexo_en = 'females' if 'femenino' in sexo.lower() else 'males'
    coef = TLC_COEFFICIENTS[sexo_en]
    spline = obtener_spline_volumen(edad, sexo, 'tlc')
    
    ln_edad = math.log(edad)
    ln_altura = math.log(altura)
    ln_valor = coef['a'] + coef['p'] * ln_edad + coef['q'] * ln_altura + spline
    
    return math.exp(ln_valor)

def calcular_valor_esperado_vc(edad: float, altura: float, sexo: str) -> float:
    """
    Calcula el valor esperado de VC usando ecuaciones GLI 2021.
    ln(VC) = a + p*edad + q*ln(altura) + spline
    """
    sexo_en = 'females' if 'femenino' in sexo.lower() else 'males'
    coef = VC_COEFFICIENTS[sexo_en]
    spline = obtener_spline_volumen(edad, sexo, 'vc')
    
    ln_altura = math.log(altura)
    ln_valor = coef['a'] + coef['p'] * edad + coef['q'] * ln_altura + spline
    
    return math.exp(ln_valor)

def calcular_valor_esperado_rv(edad: float, altura: float, sexo: str) -> float:
    """
    Calcula el valor esperado de RV usando ecuaciones GLI 2021.
    ln(RV) = a + p*edad + q*altura + spline
    """
    sexo_en = 'females' if 'femenino' in sexo.lower() else 'males'
    coef = RV_COEFFICIENTS[sexo_en]
    spline = obtener_spline_volumen(edad, sexo, 'rv')
    
    ln_valor = coef['a'] + coef['p'] * edad + coef['q'] * altura + spline
    
    return math.exp(ln_valor)

def calcular_valor_esperado_rvtlc(edad: float, altura: float, sexo: str) -> float:
    """
    Calcula el valor esperado de RV/TLC usando ecuaciones GLI 2021.
    ln(RV/TLC) = a + p*edad + q*altura + spline
    """
    sexo_en = 'females' if 'femenino' in sexo.lower() else 'males'
    coef = RVTLC_COEFFICIENTS[sexo_en]
    spline = obtener_spline_volumen(edad, sexo, 'rvtlc')
    
    ln_valor = coef['a'] + coef['p'] * edad + coef['q'] * altura + spline
    
    return math.exp(ln_valor)

def generar_interpretacion_general(resultados: Dict) -> str:
    """
    Genera una interpretación general basada en los resultados del análisis.
    """
    if "error" in resultados:
        return f"❌ **Error en el análisis**: {resultados['error']}"
    
    interpretaciones = []
    
    # Analizar patrones de espirometría
    fev1_ok = resultados.get('FEV1', {}).get('z_score', 0) >= -1.64
    fvc_ok = resultados.get('FVC', {}).get('z_score', 0) >= -1.64
    fef_ok = resultados.get('FEF25-75%', {}).get('z_score', 0) >= -1.64
    
    if fev1_ok and fvc_ok and fef_ok:
        interpretaciones.append("✅ **Espirometría Normal**: Todos los parámetros están dentro del rango normal.")
    elif not fev1_ok and not fvc_ok and fef_ok:
        interpretaciones.append("🔍 **Patrón Restrictivo**: FEV1 y FVC reducidos con FEF25-75% normal.")
    elif not fev1_ok and fvc_ok and not fef_ok:
        interpretaciones.append("🔍 **Patrón Obstructivo**: FEV1 y FEF25-75% reducidos con FVC normal.")
    elif not fev1_ok and not fvc_ok and not fef_ok:
        interpretaciones.append("🔍 **Patrón Mixto**: FEV1, FVC y FEF25-75% reducidos.")
    
    # Analizar DLCO
    dlco_ok = resultados.get('DLCO', {}).get('z_score', 0) >= -1.64
    kco_ok = resultados.get('KCO', {}).get('z_score', 0) >= -1.64
    va_ok = resultados.get('VA', {}).get('z_score', 0) >= -1.64
    
    if 'DLCO' in resultados:
        if dlco_ok and kco_ok and va_ok:
            interpretaciones.append("✅ **DLCO Normal**: Capacidad de difusión y volúmenes alveolares normales.")
        elif not dlco_ok and not kco_ok and va_ok:
            interpretaciones.append("🔍 **Alteración de la membrana**: DLCO y KCO reducidos con VA normal.")
        elif not dlco_ok and kco_ok and not va_ok:
            interpretaciones.append("🔍 **Alteración del volumen alveolar**: DLCO y VA reducidos con KCO normal.")
        elif not dlco_ok and not kco_ok and not va_ok:
            interpretaciones.append("🔍 **Alteración mixta**: DLCO, KCO y VA reducidos.")
    
    # Analizar volúmenes pulmonares
    tlc_ok = resultados.get('TLC', {}).get('z_score', 0) >= -1.64
    vc_ok = resultados.get('VC', {}).get('z_score', 0) >= -1.64
    rv_ok = resultados.get('RV', {}).get('z_score', 0) >= -1.64
    rvtlc_ok = resultados.get('RV/TLC', {}).get('z_score', 0) <= 1.64  # RV/TLC alto es anormal
    
    if 'TLC' in resultados:
        if tlc_ok and vc_ok and rv_ok and rvtlc_ok:
            interpretaciones.append("✅ **Volúmenes Pulmonares Normales**: TLC, VC, RV y RV/TLC dentro del rango normal.")
        elif not tlc_ok and not vc_ok and rv_ok and rvtlc_ok:
            interpretaciones.append("🔍 **Patrón Restrictivo**: TLC y VC reducidos con RV y RV/TLC normales.")
        elif tlc_ok and vc_ok and not rv_ok and not rvtlc_ok:
            interpretaciones.append("🔍 **Hiperinsuflación**: RV y RV/TLC elevados con TLC y VC normales.")
        elif not tlc_ok and not vc_ok and not rv_ok and not rvtlc_ok:
            interpretaciones.append("🔍 **Alteración mixta de volúmenes**: Múltiples parámetros alterados.")
    
    # Agregar detalles específicos con severidad
    for param, datos in resultados.items():
        if 'z_score' in datos:
            z = datos['z_score']
            if z < -1.64 or (param == 'RV/TLC' and z > 1.64):
                severidad = datos.get('severidad', '')
                interpretaciones.append(f"⚠️ **{param}**: {datos['interpretacion']} (Z-score = {z}, Severidad: {severidad})")
    
    return "\n\n".join(interpretaciones) if interpretaciones else "📊 Análisis completado. Revisar valores individuales."

def analizar_volumenes(datos: Dict) -> Dict:
    """
    Analiza específicamente los datos de volúmenes pulmonares usando ecuaciones GLI 2021.
    """
    try:
        edad = float(datos.get('Edad', 0))
        altura = float(datos.get('Altura', 0))
        sexo = datos.get('Sexo', 'Femenino')
        
        if edad <= 0 or altura <= 0:
            return {"error": "Datos insuficientes para análisis"}
        
        # Validar rango de edad y altura para volúmenes
        if edad < 5 or edad > 90:  # Rango específico para volúmenes
            return {"error": "Edad fuera del rango válido para volúmenes (5-90 años)"}
        if altura < 100 or altura > 250:
            return {"error": "Altura fuera del rango válido (100-250 cm)"}
        
        # Cargar tablas de volúmenes si no están cargadas
        if not gli_vol_tables:
            cargar_tablas_volumenes()
        
        resultados = {}
        
        # TLC
        if datos.get('TLC pre') and datos.get('TLC pre') != 'Valor no encontrado':
            tlc_obs = float(datos['TLC pre'])
            tlc_esp = calcular_valor_esperado_tlc(edad, altura, sexo)
            tlc_z = calcular_z_score(tlc_obs, tlc_esp, rse=0.12)
            interpretacion, severidad = interpretar_z_score_con_severidad(tlc_z)
            resultados['TLC'] = {
                'observado': tlc_obs,
                'esperado': round(tlc_esp, 2),
                'z_score': round(tlc_z, 2),
                'interpretacion': interpretacion,
                'severidad': severidad
            }
        
        # VC
        if datos.get('VC pre') and datos.get('VC pre') != 'Valor no encontrado':
            vc_obs = float(datos['VC pre'])
            vc_esp = calcular_valor_esperado_vc(edad, altura, sexo)
            vc_z = calcular_z_score(vc_obs, vc_esp, rse=0.12)
            interpretacion, severidad = interpretar_z_score_con_severidad(vc_z)
            resultados['VC'] = {
                'observado': vc_obs,
                'esperado': round(vc_esp, 2),
                'z_score': round(vc_z, 2),
                'interpretacion': interpretacion,
                'severidad': severidad
            }
        
        # RV
        if datos.get('RV pre') and datos.get('RV pre') != 'Valor no encontrado':
            rv_obs = float(datos['RV pre'])
            rv_esp = calcular_valor_esperado_rv(edad, altura, sexo)
            rv_z = calcular_z_score(rv_obs, rv_esp, rse=0.15)
            interpretacion, severidad = interpretar_z_score_con_severidad(rv_z)
            resultados['RV'] = {
                'observado': rv_obs,
                'esperado': round(rv_esp, 2),
                'z_score': round(rv_z, 2),
                'interpretacion': interpretacion,
                'severidad': severidad
            }
        
        # RV/TLC
        if datos.get('RV/TLC pre') and datos.get('RV/TLC pre') != 'Valor no encontrado':
            rvtlc_obs = float(datos['RV/TLC pre'])
            rvtlc_esp = calcular_valor_esperado_rvtlc(edad, altura, sexo)
            rvtlc_z = calcular_z_score(rvtlc_obs, rvtlc_esp, rse=0.15)
            interpretacion, severidad = interpretar_z_score_con_severidad(rvtlc_z)
            resultados['RV/TLC'] = {
                'observado': rvtlc_obs,
                'esperado': round(rvtlc_esp, 2),
                'z_score': round(rvtlc_z, 2),
                'interpretacion': interpretacion,
                'severidad': severidad
            }
        
        return resultados
        
    except Exception as e:
        return {"error": f"Error en análisis volúmenes: {str(e)}"}