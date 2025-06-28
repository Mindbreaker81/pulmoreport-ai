import re

def get_nth_number(line, n):
    """Devuelve el n-ésimo número (1-indexed) en una línea, como string, o None si no existe."""
    numbers = re.findall(r'\d+[\.,]\d+', line)
    if len(numbers) >= n:
        return numbers[n-1].replace(',', '.')
    return None

def extract_values_from_multiline(lineas, start_idx, param_name):
    """Extrae valores de una línea y las siguientes hasta encontrar números o otra variable."""
    combined_text = ""
    i = start_idx
    
    # Lista de nombres de variables para detectar cuando parar
    variable_names = ['fvc', 'fev1', 'fev1/fvc', 'fef25-75', 'pef', 'fet', 'dlco', 'dladj', 'va', 'dlco/va', 'kco', 'tlc', 'vcmax', 'rv', 'rv/tlc']
    
    while i < len(lineas):
        l = lineas[i].strip()
        
        # Detener si encontramos otra variable (excepto la actual)
        for var_name in variable_names:
            if var_name in l.lower() and var_name not in param_name.lower():
                return combined_text.strip()
        
        combined_text += l + " "
        
        # Si encontramos números en esta línea, continuamos hasta la siguiente línea sin números
        if re.search(r'\d+[\.,]\d+', l):
            i += 1
            # Continuar hasta encontrar una línea sin números o con un nuevo parámetro
            while i < len(lineas):
                next_line = lineas[i].strip()
                
                # Detener si encontramos otra variable
                for var_name in variable_names:
                    if var_name in next_line.lower() and var_name not in param_name.lower():
                        return combined_text.strip()
                
                # Detener si no hay números en esta línea
                if not re.search(r'\d+[\.,]\d+', next_line):
                    break
                    
                combined_text += next_line + " "
                i += 1
            break
        i += 1
    
    return combined_text.strip()

def extract_datos_pulmonar(texto: str) -> dict:
    datos = {
        'Sexo': None,
        'Altura': None,
        'Peso': None,
        'Edad': None,
        'Origen étnico': None,
        'FVC pre': None,
        'FVC post': None,
        'FEV1 pre': None,
        'FEV1 post': None,
        'FEV1/FVC pre': None,
        'FEV1/FVC post': None,
        'FEF25-75% pre': None,
        'FEF25-75% post': None,
        'DLCO': None,
        'VA': None,
        'DLCO/VA': None,
        'TLC': None,
        'VC': None,
        'RV': None,
        'RV/TLC': None,
        'FeNO': None
    }
    lineas = texto.splitlines()
    
    # Datos generales
    for l in lineas:
        if 'sexo' in l.lower() and datos['Sexo'] is None:
            m = re.search(r'(Femenino|Masculino)', l, re.IGNORECASE)
            if m:
                datos['Sexo'] = m.group(1).capitalize()
        if 'altura' in l.lower() and datos['Altura'] is None:
            m = re.search(r'(\d{2,3})\s*cm', l)
            if m:
                datos['Altura'] = m.group(1)
        if 'peso' in l.lower() and datos['Peso'] is None:
            m = re.search(r'(\d{2,3})\s*kg', l)
            if m:
                datos['Peso'] = m.group(1)
        if 'edad' in l.lower() and datos['Edad'] is None:
            m = re.search(r'Edad[:\s]*(\d+)', l)
            if m:
                datos['Edad'] = m.group(1)
        if 'origen étnico' in l.lower() and datos['Origen étnico'] is None:
            m = re.search(r'Origen étnico\s*([\wáéíóúüñ]+)', l, re.IGNORECASE)
            if m:
                datos['Origen étnico'] = m.group(1).capitalize()
    
    # Buscar parámetros funcionales
    for i, l in enumerate(lineas):
        l_strip = l.strip()
        
        # FVC [L]
        if 'fvc [l]' in l_strip.lower():
            combined_text = extract_values_from_multiline(lineas, i, 'fvc')
            numbers = re.findall(r'\d+[\.,]\d+', combined_text)
            if len(numbers) >= 5:
                # Si hay al menos 5 números, usar el primero para pre y el quinto para post
                datos['FVC pre'] = numbers[0].replace(',', '.')
                datos['FVC post'] = numbers[4].replace(',', '.')
            elif len(numbers) >= 3:
                # Si hay al menos 3 números pero menos de 5, usar el tercero para pre
                datos['FVC pre'] = numbers[2].replace(',', '.')
                datos['FVC post'] = 'Valor no encontrado'
            elif len(numbers) >= 1:
                # Si solo hay 1-2 números, usar el primero para pre
                datos['FVC pre'] = numbers[0].replace(',', '.')
                datos['FVC post'] = 'Valor no encontrado'
            else:
                datos['FVC pre'] = 'Valor no encontrado'
                datos['FVC post'] = 'Valor no encontrado'
        
        # FEV1 [L]
        elif 'fev1 [l]' in l_strip.lower():
            combined_text = extract_values_from_multiline(lineas, i, 'fev1')
            numbers = re.findall(r'\d+[\.,]\d+', combined_text)
            if len(numbers) >= 5:
                # Si hay al menos 5 números, usar el primero para pre y el quinto para post
                datos['FEV1 pre'] = numbers[0].replace(',', '.')
                datos['FEV1 post'] = numbers[4].replace(',', '.')
            elif len(numbers) >= 3:
                # Si hay al menos 3 números pero menos de 5, usar el tercero para pre
                datos['FEV1 pre'] = numbers[2].replace(',', '.')
                datos['FEV1 post'] = 'Valor no encontrado'
            elif len(numbers) >= 1:
                # Si solo hay 1-2 números, usar el primero para pre
                datos['FEV1 pre'] = numbers[0].replace(',', '.')
                datos['FEV1 post'] = 'Valor no encontrado'
            else:
                datos['FEV1 pre'] = 'Valor no encontrado'
                datos['FEV1 post'] = 'Valor no encontrado'
        
        # FEV1/FVC
        elif 'fev1/fvc' in l_strip.lower():
            combined_text = extract_values_from_multiline(lineas, i, 'fev1/fvc')
            numbers = re.findall(r'\d+[\.,]\d+', combined_text)
            if len(numbers) >= 5:
                # Si hay al menos 5 números, usar el primero para pre y el quinto para post
                datos['FEV1/FVC pre'] = numbers[0].replace(',', '.')
                datos['FEV1/FVC post'] = numbers[4].replace(',', '.')
            elif len(numbers) >= 3:
                # Si hay al menos 3 números pero menos de 5, usar el tercero para pre
                datos['FEV1/FVC pre'] = numbers[2].replace(',', '.')
                datos['FEV1/FVC post'] = 'Valor no encontrado'
            elif len(numbers) >= 1:
                # Si solo hay 1-2 números, usar el primero para pre
                datos['FEV1/FVC pre'] = numbers[0].replace(',', '.')
                datos['FEV1/FVC post'] = 'Valor no encontrado'
            else:
                datos['FEV1/FVC pre'] = 'Valor no encontrado'
                datos['FEV1/FVC post'] = 'Valor no encontrado'
        
        # FEF25-75
        elif 'fef25-75' in l_strip.lower():
            combined_text = extract_values_from_multiline(lineas, i, 'fef25-75')
            numbers = re.findall(r'\d+[\.,]\d+', combined_text)
            if len(numbers) >= 5:
                # Si hay al menos 5 números, usar el primero para pre y el quinto para post
                datos['FEF25-75% pre'] = numbers[0].replace(',', '.')
                datos['FEF25-75% post'] = numbers[4].replace(',', '.')
            elif len(numbers) >= 3:
                # Si hay al menos 3 números pero menos de 5, usar el tercero para pre
                datos['FEF25-75% pre'] = numbers[2].replace(',', '.')
                datos['FEF25-75% post'] = 'Valor no encontrado'
            elif len(numbers) >= 1:
                # Si solo hay 1-2 números, usar el primero para pre
                datos['FEF25-75% pre'] = numbers[0].replace(',', '.')
                datos['FEF25-75% post'] = 'Valor no encontrado'
            else:
                datos['FEF25-75% pre'] = 'Valor no encontrado'
                datos['FEF25-75% post'] = 'Valor no encontrado'
        
        # DLCO/VA
        elif 'dlco/va' in l_strip.lower() and datos['DLCO/VA'] is None:
            print(f"DEBUG: Encontrada línea DLCO/VA: {l_strip}")
            # Buscar números en las líneas siguientes
            for j in range(i+1, min(i+5, len(lineas))):
                next_line = lineas[j].strip()
                print(f"DEBUG: Línea siguiente {j}: {next_line}")
                numbers = re.findall(r'\d+[\.,]\d+', next_line)
                if numbers:
                    print(f"DEBUG: Números encontrados en línea {j}: {numbers}")
                    datos['DLCO/VA'] = numbers[0].replace(',', '.')
                    break
            if datos['DLCO/VA'] is None:
                datos['DLCO/VA'] = 'Valor no encontrado'
        
        # DLCO (pero no DLCO/VA)
        elif 'dlco' in l_strip.lower() and 'dlco/va' not in l_strip.lower() and datos['DLCO'] is None:
            print(f"DEBUG: Encontrada línea DLCO: {l_strip}")
            combined_text = extract_values_from_multiline(lineas, i, 'dlco')
            numbers = re.findall(r'\d+[\.,]\d+', combined_text)
            if len(numbers) >= 1:
                datos['DLCO'] = numbers[0].replace(',', '.')
            else:
                datos['DLCO'] = 'Valor no encontrado'
        
        # VA sb [L]
        elif 'va sb [l]' in l_strip.lower():
            print(f"DEBUG: Encontrada línea VA: {l_strip}")
            combined_text = extract_values_from_multiline(lineas, i, 'va')
            numbers = re.findall(r'\d+[\.,]\d+', combined_text)
            if len(numbers) >= 1:
                datos['VA'] = numbers[0].replace(',', '.')
            else:
                datos['VA'] = 'Valor no encontrado'
        
        # TLC sb [L]
        elif 'tlc sb [l]' in l_strip.lower():
            combined_text = extract_values_from_multiline(lineas, i, 'tlc')
            numbers = re.findall(r'\d+[\.,]\d+', combined_text)
            if len(numbers) >= 1:
                datos['TLC'] = numbers[0].replace(',', '.')
            else:
                datos['TLC'] = 'Valor no encontrado'
        
        # VCmax [L]
        elif 'vcmax [l]' in l_strip.lower():
            print(f"DEBUG: Encontrada línea VC: {l_strip}")
            # Buscar números en la misma línea
            numbers = re.findall(r'\d+[\.,]\d+', l_strip)
            if numbers:
                print(f"DEBUG: Números encontrados VC en la misma línea: {numbers}")
                datos['VC'] = numbers[0].replace(',', '.')
            else:
                datos['VC'] = 'Valor no encontrado'
        
        # RV sb [L]
        elif 'rv sb [l]' in l_strip.lower():
            combined_text = extract_values_from_multiline(lineas, i, 'rv')
            numbers = re.findall(r'\d+[\.,]\d+', combined_text)
            if len(numbers) >= 1:
                datos['RV'] = numbers[0].replace(',', '.')
            else:
                datos['RV'] = 'Valor no encontrado'
        
        # RV/TLC sb
        elif 'rv/tlc sb' in l_strip.lower():
            combined_text = extract_values_from_multiline(lineas, i, 'rv/tlc')
            numbers = re.findall(r'\d+[\.,]\d+', combined_text)
            if len(numbers) >= 1:
                datos['RV/TLC'] = numbers[0].replace(',', '.')
            else:
                datos['RV/TLC'] = 'Valor no encontrado'
    
    # FeNO (buscar línea que contenga FeNO)
    feno_found = False
    for l in lineas:
        if 'feno' in l.lower():
            m = re.search(r'(\d+)', l)
            if m:
                datos['FeNO'] = m.group(1)
                feno_found = True
    if not feno_found:
        datos['FeNO'] = 'Valor no encontrado'
    
    return datos 