import re

def convert_keywords(code, keyword_dict):
    def replace_func(match):
        keyword = match.group(0)
        # Determinar si la palabra clave debe ser convertida a mayúsculas o minúsculas
        return keyword_dict.get(keyword.lower(), keyword)
    
    # Patrón para identificar palabras clave relevantes
    pattern = re.compile(r'\b(' + '|'.join(re.escape(key) for key in keyword_dict.keys()) + r')\b', re.IGNORECASE)
    return pattern.sub(replace_func, code)

def convert_data_types_to_camel_case(code):
    # Lista de tipos de datos comunes
    data_types = ["integer", "string", "double", "boolean", "char", "long", "decimal", "date", "datetime", "time", "Dec"]
    
    def replace_func(match):
        # Especialmente para "dec", donde se mantiene el número entre {}
        if match.group(0).startswith("dec"):
            return "Dec" + match.group(0)[3:]
        else:
            return match.group(0).capitalize()
    
    # Compilar un patrón regex que coincida con los tipos de datos
    pattern = re.compile(r'\b(' + '|'.join(data_types) + r')\b', re.IGNORECASE)
    
    # Reemplazar en el código
    code = pattern.sub(replace_func, code)
    return code

def is_single_line_if(line):
    """
    Determina si la línea contiene una sentencia if de una sola línea.
    Ahora se excluyen los casos en los que hay un comentario después del 'then', tratándolos como si no fueran de una sola línea para la indentación.
    
    Ejemplos:
    - "if condition then action" -> True
    - "if condition then return something" -> True
    - "if condition then action // some comment" -> False
    """
    # Primero, verificamos si es un if con return, estos siempre se tratan como de una sola línea
    if_return_match = re.match(r'^\s*if .+ then return', line, re.IGNORECASE)
    if if_return_match:
        return True

    # Luego, verificamos si hay un comentario después del then. Si es así, no se trata como de una sola línea
    if_comment_match = re.match(r'^\s*if .+ then .+//', line, re.IGNORECASE)
    if if_comment_match:
        return False

    # Finalmente, el comportamiento por defecto para identificar un if de una sola línea sin considerar comentarios
    single_line_if_match = re.match(r'^\s*if .+ then [^//]+$', line.strip(), re.IGNORECASE)
    return bool(single_line_if_match)

def clean_comments(code):
     # Eliminar completamente las líneas de comentario vacías resultantes
    code = "\n".join([line for line in code.split('\n') if line.strip() != "//" and line.strip() != ""])

    # Limpiar comentarios de línea única
    code = re.sub(r'(//\s*)(.*)', lambda m: "// " + m.group(2).strip(), code)
    # Limpiar comentarios de bloque
    def clean_block_comment(match):
        # Primera línea después de /*
        start = match.group(1).lstrip()
        # Contenido interno del comentario de bloque
        content = match.group(2)
        # Última línea antes de */
        end = match.group(3).rstrip()

        # Limpia cada línea intermedia
        cleaned_lines = [line.strip() for line in content.split('\n')]
        full_comment = "/* " + start + "\n" + "\n".join(cleaned_lines) + "\n" + end + " */"
        return full_comment

    # Aplicar limpieza a comentarios de bloque
    code = re.sub(r'/\*\s*(.*?)\n(.*?)\n\s*(\*\/)', clean_block_comment, code, flags=re.DOTALL)
    return code

def remove_content_after_block_comment(code):
    # Eliminar contenido que sigue inmediatamente después de un cierre de comentario de bloque en la misma línea
    code = re.sub(r'(\/\*.*?\*\/)([^\n]*)', lambda m: m.group(1) if m.group(2).strip().startswith('//') else m.group(1) + "\n" + "//" + m.group(2).strip(), code, flags=re.DOTALL)
    return code

def adjust_code_formatting(code):
 # Ajustar los 'end if' como antes
    code = re.sub(r'\bend\s+if\b', 'end if', code, flags=re.IGNORECASE)
    
    # Corrección en la función para reubicar comentarios dentro de las sentencias if
    def relocate_comment_inside_if(match):
        before_comment = match.group(1)  # Todo antes del comentario
        comment = match.group(2).strip()  # El comentario, sin espacios adicionales
        after_comment = match.group(3)  # Todo después del comentario, que esperamos sea vacío o espacios hasta 'then'
        # Componer la nueva línea manteniendo el 'then' en su lugar y moviendo el comentario al final
        new_line = f"if {before_comment.strip()} then {after_comment.strip()} /* {comment} */"
        return new_line

    # Expresión regular ajustada para manejar el escenario específico descrito
    pattern = re.compile(r'if\s+(.*?)\s*/\*\s*(.*?)\s*\*/\s*then\s*(.*)', re.IGNORECASE | re.DOTALL)
    code = pattern.sub(relocate_comment_inside_if, code)
    
    return code


def reformat_power_script(code):
    # Aplicar el ajuste a los comentarios de bloque y formateo de 'end if'
    code = adjust_code_formatting(code)
    # Primero, limpiar los bloques de comentarios
    code = remove_content_after_block_comment(code)
    # Aplicar limpieza de espacios en comentarios
    code = clean_comments(code)
    # Formatear tipos de datos a minúsculas
    code = convert_data_types_to_camel_case(code)
    
    # Eliminar espacios en blanco al comienzo de cada línea
    code = "\n".join(line.lstrip() for line in code.split('\n'))
  

       # Palabras clave para convertir a minúsculas
    lowercase_keywords = {
        "if": "if", "end if": "end if", "for": "for", "next": "next", 
        "choose case": "choose case", "end choose": "end choose", "try": "try", "catch": "catch", 
        "finally": "finally", "end try": "end try", "else": "else", "elseif": "elseif", "case":"case", "do while":"do while", "loop":"loop","do":"do","loop while":"loop while"
    }
    # Palabras clave SQL para convertir a mayúsculas
    uppercase_sql_keywords = {
        "select": "SELECT", "update": "UPDATE", "delete": "DELETE", "insert into": "INSERT INTO", 
        "from": "FROM", "where": "WHERE", "join": "JOIN", "inner join": "INNER JOIN", 
        "left join": "LEFT JOIN", "right join": "RIGHT JOIN", "on": "ON", "order by": "ORDER BY",
        "group by": "GROUP BY", "having": "HAVING", "into":"INTO"
    }


    # Lista de palabras clave para aumentar la indentación
    open_keywords = ["if", "for", "do while", "try", "choose case", "then", "do until", "do"]
    # Lista de palabras clave para mantener la indentación (especialmente para elseif)
    maintain_keywords = ["elseif","else", "case"]
    # Lista de palabras clave para disminuir la indentación
    close_keywords = ["end if", "next", "end choose", "end case", "end try","loop", "loop while"]

    # Convertir a minúsculas/mayúsculas fuera de los bloques SQL
    code = convert_keywords(code, lowercase_keywords)
    
    # Identificar y procesar bloques SQL
    sql_blocks = re.split(r'(;)', code)  # Dividir en bloques usando ';' como delimitador
    for i in range(0, len(sql_blocks) - 1, 2):  # Iterar solo en bloques de SQL (ignorando los ';')
        if any(kw.upper() in sql_blocks[i].upper() for kw in uppercase_sql_keywords):
            sql_blocks[i] = convert_keywords(sql_blocks[i], uppercase_sql_keywords)
    code = ''.join(sql_blocks)

    # Preprocesamiento: Convertir a minúsculas y eliminar espacios extra
    code_lines = code.split('\n')
    indented_code = ""
    indent_level = 0
    in_multiline_comment = False

    for line in code_lines:
        line = line.rstrip()
        if not line and not in_multiline_comment:
            # Si la línea está vacía y no estamos en un comentario multilínea, continuar
            continue
        stripped_line = line.strip()
        stripped_line = line.strip()
        # Manejo de comentarios
        if stripped_line.startswith("/*"):
            in_multiline_comment = True
        if in_multiline_comment or stripped_line.startswith("//"):
            indented_code += "    " * indent_level + line + "\n"
            if stripped_line.endswith("*/"):
                in_multiline_comment = False
            continue

        line = re.sub(r"\bthis\.", "", line, flags=re.IGNORECASE)
        line = re.sub(r"\bsetitem\(", "setitem(", line, flags=re.IGNORECASE)

        # Ajuste previo de indentación para cierres y mantenimientos
        if any(stripped_line.startswith(kw) for kw in close_keywords):
            indent_level = max(indent_level - 1, 0)
        if any(stripped_line.startswith(kw) for kw in maintain_keywords):
            indented_code += "    " * max(indent_level - 1, 0) + line + "\n"
            continue

        # Agregar línea con la indentación actual
        indented_code += "    " * indent_level + line + "\n"

        # Ajuste de indentación después de la línea actual
        if any(stripped_line.startswith(kw) for kw in open_keywords) and not is_single_line_if(line):
            indent_level += 1

    return indented_code

# Leer el código original desde un archivo
ruta_archivo_original = r'C:\Pintulac\pos.srw'
with open(ruta_archivo_original, 'r', encoding='utf-8') as archivo:
    codigo_original = archivo.read()

# Formatear el código
formatted_code = reformat_power_script(codigo_original)

# Guardar el código formateado en un nuevo archivo
ruta_archivo_formateado = r'C:\Pintulac\pos_newly.srw'
with open(ruta_archivo_formateado, 'w', encoding='utf-8') as archivo:
    archivo.write(formatted_code)

print("El código ha sido formateado y guardado en:", ruta_archivo_formateado)
