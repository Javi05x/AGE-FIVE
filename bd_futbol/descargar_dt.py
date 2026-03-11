import os
import sys
import pandas as pd
from pymongo import MongoClient

# Añadimos el directorio raíz del proyecto al path para poder importar config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bd_futbol.config import (
    MONGO_URI, MONGO_DB, MONGO_COLLECTION,
    RANGOS_EDAD, RUTA_2122, RUTA_2223, RUTA_2324, RUTA_2425
)

# -----------------------------------------------------------------------
# Mapeo de columnas por temporada
# Formato: {nombre_interno: nombre_en_el_archivo}
# Solo se especifican las que difieren del estándar (23/24 y 24/25)
# -----------------------------------------------------------------------
MAPEO_COLUMNAS = {
    "21/22": {
        "Gls":         "Goals",
        "Ast":         "Assists",
        # xG y stats por 90 no existen en 21/22 → se rellenan con 0
        "xG":          None,
        "npxG":        None,
        "xAG":         None,
        "npxG+xAG":    None,
        "PrgC":        None,
        "PrgP":        None,
        "PrgR":        None,
        "G+A":         None,
        "G-PK":        None,
        "PK":          None,
        "Gls_90":      None,
        "Ast_90":      None,
        "G+A_90":      None,
        "G-PK_90":     None,
        "G+A-PK_90":   None,
        "xG_90":       None,
        "xAG_90":      None,
        "xG+xAG_90":   None,
        "npxG_90":     None,
        "npxG+xAG_90": None,
    },
    "22/23": {
        # Stats por 90 tienen nombre distinto en 22/23
        "Gls_90":      "Gls.1",
        "Ast_90":      "Ast.1",
        "G+A_90":      "G+A.1",
        "G-PK_90":     "G-PK.1",
        "G+A-PK_90":   "G+A-PK",
        "xG_90":       "xG.1",
        "xAG_90":      "xAG.1",
        "xG+xAG_90":   "xG+xAG",
        "npxG_90":     "npxG.1",
        "npxG+xAG_90": "npxG+xAG.1",
    },
}

# -----------------------------------------------------------------------
# Normalización de nombres de liga
# -----------------------------------------------------------------------
NORMALIZAR_LIGA = {
    # Con prefijo de país (22/23)
    "eng Premier League": "Premier League",
    "es La Liga":         "La Liga",
    "de Bundesliga":      "Bundesliga",
    "fr Ligue 1":         "Ligue 1",
    "it Serie A":         "Serie A",
    # Sin prefijo (21/22, 23/24, 24/25) — ya están bien, pero por si acaso
    "Premier League":     "Premier League",
    "La Liga":            "La Liga",
    "Bundesliga":         "Bundesliga",
    "Ligue 1":            "Ligue 1",
    "Serie A":            "Serie A",
}

def get_valor(row, col_estandar, temporada, default=0):
    """
    Obtiene el valor de una columna teniendo en cuenta el mapeo por temporada.
    Si la columna está mapeada a None, devuelve el valor por defecto.
    Si no hay mapeo, usa el nombre estándar directamente.
    """
    mapeo = MAPEO_COLUMNAS.get(temporada, {})
    if col_estandar in mapeo:
        col_real = mapeo[col_estandar]
        if col_real is None:
            return default
        return row.get(col_real, default)
    return row.get(col_estandar, default)


def clasificar_rango_edad(edad):
    """Clasifica un jugador en su rango de edad según la configuración."""
    for min_edad, max_edad, etiqueta in RANGOS_EDAD:
        if max_edad is None:
            if edad >= min_edad:
                return etiqueta
        elif min_edad <= edad <= max_edad:
            return etiqueta
    return "Desconocido"


def leer_archivo(ruta):
    """Lee un archivo CSV o Excel y devuelve un DataFrame."""
    if ruta.endswith(".csv"):
        # Intentamos primero UTF-8, si falla usamos latin-1
        try:
            df = pd.read_csv(ruta, encoding="utf-8")
            # Comprobamos si el separador es punto y coma
            if len(df.columns) == 1:
                df = pd.read_csv(ruta, encoding="utf-8", sep=";")
        except UnicodeDecodeError:
            df = pd.read_csv(ruta, encoding="latin-1", sep=";")
    else:
        df = pd.read_excel(ruta)

    # Limpieza de columnas numéricas: quitar comas de miles (ej: "2,372" -> 2372)
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).str.replace(",", "", regex=False)
            convertida = pd.to_numeric(df[col], errors="ignore")
            if convertida.dtype != object:
                df[col] = convertida

    return df

def safe_int(valor, default=0):
    """Convierte a int limpiando comas de miles."""
    try:
        return int(str(valor).replace(",", "").replace(" ", "").split(".")[0])
    except (ValueError, TypeError):
        return default


def safe_float(valor, default=0.0):
    """Convierte a float limpiando comas de miles."""
    try:
        return float(str(valor).replace(",", "").replace(" ", ""))
    except (ValueError, TypeError):
        return default


def get_valor(row, col_estandar, temporada, default=0):
    """
    Obtiene el valor de una columna teniendo en cuenta el mapeo por temporada.
    Si la columna está mapeada a None, devuelve el valor por defecto.
    Si no hay mapeo, usa el nombre estándar directamente.
    """
    mapeo = MAPEO_COLUMNAS.get(temporada, {})
    if col_estandar in mapeo:
        col_real = mapeo[col_estandar]
        if col_real is None:
            return default
        return row.get(col_real, default)
    return row.get(col_estandar, default)

def procesar_y_subir(ruta, etiqueta_temporada, collection):
    """Carga un archivo, limpia los datos y los inserta en MongoDB."""
    try:
        print(f"\n--- Iniciando proceso para temporada: {etiqueta_temporada} ---")
        df = leer_archivo(ruta)

        # Columnas de texto que se rellenan con cadena vacía si están vacías
        columnas_texto = ["Player", "Nation", "Pos", "Squad", "Comp"]
        for col in columnas_texto:
            if col in df.columns:
                df[col] = df[col].fillna("")

        # Columnas numéricas estándar: rellenamos NaN con 0
        for col in df.select_dtypes(include="number").columns:
            df[col] = df[col].fillna(0)

        jugadores_list = []
        resumen_liga = {}
        resumen_rango = {}

        for _, row in df.iterrows():
            edad = int(row.get("Age", 0))
            rango = clasificar_rango_edad(edad)
            liga = NORMALIZAR_LIGA.get(str(row.get("Comp", "")), str(row.get("Comp", "")))
            resumen_liga[liga] = resumen_liga.get(liga, 0) + 1
            resumen_rango[rango] = resumen_rango.get(rango, 0) + 1

            doc = {
                "player":     str(row.get("Player", "")),
                "nation":     str(row.get("Nation", "")),
                "pos":        str(row.get("Pos", "")),
                "age":        safe_int(row.get("Age", 0)),
                "born":       safe_int(row.get("Born", 0)),
                "rango_edad": rango,
                "team_info": {
                    "squad":     str(row.get("Squad", "")),
                    "comp":      liga,
                    "temporada": etiqueta_temporada,
                },
                "stats_base": {
                    "mp":     safe_int(row.get("MP", 0)),
                    "starts": safe_int(row.get("Starts", 0)),
                    "min":    safe_int(row.get("Min", 0)),
                    "90s":    safe_float(row.get("90s", 0)),
                },
                "stats_ataque": {
                    "gls":   safe_int(get_valor(row, "Gls",  etiqueta_temporada)),
                    "ast":   safe_int(get_valor(row, "Ast",  etiqueta_temporada)),
                    "g_a":   safe_int(get_valor(row, "G+A",  etiqueta_temporada)),
                    "g_pk":  safe_int(get_valor(row, "G-PK", etiqueta_temporada)),
                    "pk":    safe_int(get_valor(row, "PK",   etiqueta_temporada)),
                    "pkatt": safe_int(row.get("PKatt", 0)),
                },
                "stats_disciplina": {
                    "crdy": safe_int(row.get("CrdY", 0)),
                    "crdr": safe_int(row.get("CrdR", 0)),
                },
                "stats_avanzadas": {
                    "xg":       safe_float(get_valor(row, "xG",       etiqueta_temporada)),
                    "npxg":     safe_float(get_valor(row, "npxG",     etiqueta_temporada)),
                    "xag":      safe_float(get_valor(row, "xAG",      etiqueta_temporada)),
                    "npxg_xag": safe_float(get_valor(row, "npxG+xAG", etiqueta_temporada)),
                    "prgc":     safe_int(get_valor(row,   "PrgC",     etiqueta_temporada)),
                    "prgp":     safe_int(get_valor(row,   "PrgP",     etiqueta_temporada)),
                    "prgr":     safe_int(get_valor(row,   "PrgR",     etiqueta_temporada)),
                },
                "stats_por_90": {
                    "gls_90":      safe_float(get_valor(row, "Gls_90",      etiqueta_temporada)),
                    "ast_90":      safe_float(get_valor(row, "Ast_90",      etiqueta_temporada)),
                    "g_a_90":      safe_float(get_valor(row, "G+A_90",      etiqueta_temporada)),
                    "g_pk_90":     safe_float(get_valor(row, "G-PK_90",     etiqueta_temporada)),
                    "g_a_pk_90":   safe_float(get_valor(row, "G+A-PK_90",   etiqueta_temporada)),
                    "xg_90":       safe_float(get_valor(row, "xG_90",       etiqueta_temporada)),
                    "xag_90":      safe_float(get_valor(row, "xAG_90",      etiqueta_temporada)),
                    "xg_xag_90":   safe_float(get_valor(row, "xG+xAG_90",   etiqueta_temporada)),
                    "npxg_90":     safe_float(get_valor(row, "npxG_90",     etiqueta_temporada)),
                    "npxg_xag_90": safe_float(get_valor(row, "npxG+xAG_90", etiqueta_temporada)),
                },
            }
            jugadores_list.append(doc)

        if jugadores_list:
            collection.insert_many(jugadores_list)
            print(f"ÉXITO: Se han subido {len(jugadores_list)} jugadores de la temporada {etiqueta_temporada}.")

        print(f"\nResumen por liga ({etiqueta_temporada}):")
        for liga, total in sorted(resumen_liga.items()):
            print(f"  {liga}: {total} jugadores")

        print(f"\nResumen por rango de edad ({etiqueta_temporada}):")
        for rango, total in sorted(resumen_rango.items()):
            print(f"  {rango}: {total} jugadores")

    except FileNotFoundError:
        print(f"ERROR: No se encontró el archivo '{ruta}'.")
    except Exception as e:
        print(f"ERROR procesando {etiqueta_temporada}: {e}")


def main():
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    collection = db[MONGO_COLLECTION]

    temporadas = [
        (RUTA_2122, "21/22"),
        (RUTA_2223, "22/23"),
        (RUTA_2324, "23/24"),
        (RUTA_2425, "24/25"),
    ]

    for ruta, etiqueta in temporadas:
        existentes = collection.count_documents({"team_info.temporada": etiqueta})
        if existentes > 0:
            respuesta = input(
                f"\nYa existen {existentes} registros de la temporada {etiqueta}. "
                f"¿Deseas sobreescribirlos? (s/n): "
            ).strip().lower()
            if respuesta in ("s", "si", "y", "yes"):
                collection.delete_many({"team_info.temporada": etiqueta})
                print(f"Registros de {etiqueta} eliminados. Reinsertando...")
                procesar_y_subir(ruta, etiqueta, collection)
            else:
                print(f"Se omite la temporada {etiqueta}.")
        else:
            procesar_y_subir(ruta, etiqueta, collection)

    client.close()


if __name__ == "__main__":
    main()