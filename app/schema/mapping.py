# Todos los nombres EXACTOS según la hoja “Fichas 2025” (fila 2)
DOCX_TO_EXCEL = {
    "Nombre de la ayuda": "NOMBRE FICHA",
    "Fecha fin": "VENCIMIENTO",
    "Usuario": "TRABAJADOR QUE LA HACE",
    "Fecha": "FECHA DE REDACCION",

    # Multi-mapeo / reglas:
    "Portales": ["Mayores", "Discapacidad", "Familia", "Mujeres", "Salud"],  # columnas boolean/literal
    "Categoría": ["TEMATICA 1", "TEMATICA 2", "TEMATICA 3"],                 # hasta 3

    # Ámbito: exclusividad (solo una de las tres)
    "Ámbito territorial": ["AMBITO CC AA", "AMBITO PROVINCIAL", "AMBITO UE/ESTADO"],

    # Campos ampliados (si tu plantilla DOCX los trae)
    "Tipo de ayuda": "TIPO DE AYUDA",
    "Fecha inicio": "FECHA INICIO",
    "Fecha publicación": "FECHA PUBLICACION",
    "Administración": "ADMINISTRACION",
    "Plazo de presentación": "PLAZO PRESENTACION",
    "Beneficiarios": "BENEFICIARIOS",
    "Requisitos de acceso": "REQUISITOS ACCESO",
    "Descripción": "DESCRIPCION",
    "Cuantía": "CUANTIA",
    "Importe máximo": "IMPORTE MAXIMO",
    "Resolución": "RESOLUCION",
    "Documentos a presentar": "DOCUMENTOS PRESENTAR",
    "Normativa reguladora": "NORMATIVA REGULADORA",
    "Referencia Legislativa": "REFERENCIA LEGISLATIVA",
    "Lugar y forma de presentación": "LUGAR Y FORMA DE PRESENTACION",
    "Costes no subvencionables": "COSTES NO SUBVENCIONABLES",
    "Frase publicitaria": "FRASE PUBLICITARIA",
}
