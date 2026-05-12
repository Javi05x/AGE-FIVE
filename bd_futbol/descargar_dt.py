import os
import sys
import pandas as pd
from pymongo import MongoClient

# Añadimos el directorio raíz del proyecto al path para poder importar config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bd_futbol.config import (  # noqa: E402
    MONGO_URI, MONGO_DB, MONGO_COLLECTION,
    RANGOS_EDAD, RUTA_2122, RUTA_2223, RUTA_2324, RUTA_2425
)

DEBUG = False  # pon True si quieres ver prints de columnas/top goals

# -----------------------------------------------------------------------
# Mapeo de columnas por temporada
# Formato: {nombre_interno: nombre_en_el_archivo}
# Solo se especifican las que difieren del estándar
# -----------------------------------------------------------------------
MAPEO_COLUMNAS = {
    "21/22": {
        # OJO: en este dataset 21/22 "Goals" y "Assists" son RATIOS (tipo por 90).
        # Se convertirán a totales usando minutos en el loop (ver procesar_y_subir).
        "Gls": "Goals",
        "Ast": "Assists",

        # No existen en 21/22 (en tu dataset actual)
        "xG": None,
        "npxG": None,
        "xAG": None,
        "npxG+xAG": None,
        "PrgC": None,
        "PrgP": None,
        "PrgR": None,
        "G+A": None,
        "G-PK": None,
        "PK": None,
        "Gls_90": None,
        "Ast_90": None,
        "G+A_90": None,
        "G-PK_90": None,
        "G+A-PK_90": None,
        "xG_90": None,
        "xAG_90": None,
        "xG+xAG_90": None,
        "npxG_90": None,
        "npxG+xAG_90": None,
    },
    "22/23": {
        # Stats por 90 tienen nombre distinto en 22/23
        "Gls_90": "Gls.1",
        "Ast_90": "Ast.1",
        "G+A_90": "G+A.1",
        "G-PK_90": "G-PK.1",
        "G+A-PK_90": "G+A-PK",
        "xG_90": "xG.1",
        "xAG_90": "xAG.1",
        "xG+xAG_90": "xG+xAG",
        "npxG_90": "npxG.1",
        "npxG+xAG_90": "npxG+xAG.1",
    },
}

# -----------------------------------------------------------------------
# Normalización de nombres de liga
# -----------------------------------------------------------------------
NORMALIZAR_LIGA = {
    # Con prefijo de país (22/23)
    "eng Premier League": "Premier League",
    "es La Liga": "La Liga",
    "de Bundesliga": "Bundesliga",
    "fr Ligue 1": "Ligue 1",
    "it Serie A": "Serie A",
    # Sin prefijo (21/22, 23/24, 24/25)
    "Premier League": "Premier League",
    "La Liga": "La Liga",
    "Bundesliga": "Bundesliga",
    "Ligue 1": "Ligue 1",
    "Serie A": "Serie A",
}

def clasificar_rango_edad(edad: int) -> str:
    for min_edad, max_edad, etiqueta in RANGOS_EDAD:
        if max_edad is None:
            if edad >= min_edad:
                return etiqueta
        elif min_edad <= edad <= max_edad:
            return etiqueta
    return "Desconocido"

def leer_archivo(ruta: str) -> pd.DataFrame:
    if ruta.endswith(".csv"):
        try:
            df = pd.read_csv(ruta, encoding="utf-8")
            if len(df.columns) == 1:
                df = pd.read_csv(ruta, encoding="utf-8", sep=";")
        except UnicodeDecodeError:
            df = pd.read_csv(ruta, encoding="latin-1", sep=";")
    else:
        df = pd.read_excel(ruta)

    # Limpieza ligera de miles en strings numéricos
    for col in df.columns:
        if df[col].dtype == object:
            s = df[col].astype(str).str.replace(",", "", regex=False)
            converted = pd.to_numeric(s, errors="ignore")
            if converted.dtype != object:
                df[col] = converted
            else:
                df[col] = s

    return df

def safe_int(valor, default=0) -> int:
    try:
        if valor is None:
            return default
        if isinstance(valor, bool):
            return int(valor)
        if isinstance(valor, int):
            return valor
        if isinstance(valor, float):
            if pd.isna(valor):
                return default
            return int(valor)
        s = str(valor).strip().replace(",", "")
        if s.lower() in ("nan", "none", ""):
            return default
        return int(float(s))
    except Exception:
        return default

def safe_float(valor, default=0.0) -> float:
    try:
        if valor is None:
            return default
        if isinstance(valor, float):
            if pd.isna(valor):
                return default
            return float(valor)
        if isinstance(valor, int):
            return float(valor)
        s = str(valor).strip().replace(",", "")
        if s.lower() in ("nan", "none", ""):
            return default
        return float(s)
    except Exception:
        return default

def get_valor(row, col_estandar: str, temporada: str, default=0):
    """
    Obtiene el valor de una columna teniendo en cuenta el mapeo por temporada.
    - Si la columna está mapeada a None => default
    - Si no hay mapeo => usa el nombre estándar
    """
    mapeo = MAPEO_COLUMNAS.get(temporada, {})
    if col_estandar in mapeo:
        col_real = mapeo[col_estandar]
        if col_real is None:
            return default
        return row.get(col_real, default)
    return row.get(col_estandar, default)

def calc_total_from_rate(rate_per90: float, minutes: int) -> int:
    # Convierte un ratio "por 90" en total aproximado
    if minutes <= 0:
        return 0
    return int(rate_per90 * (minutes / 90.0))

def procesar_y_subir(ruta: str, etiqueta_temporada: str, collection):
    try:
        print(f"\n--- Iniciando proceso para temporada: {etiqueta_temporada} ---")
        df = leer_archivo(ruta)

        if DEBUG:
            print("Columnas detectadas:", list(df.columns))
            if "Goals" in df.columns:
                print("Max Goals en CSV:", pd.to_numeric(df["Goals"], errors="coerce").max())
                print(
                    "Top 5 Goals en CSV:\n",
                    df[["Player", "Squad", "Comp", "Goals", "Min"]]
                    .sort_values("Goals", ascending=False)
                    .head(5),
                )

        # Columnas de texto
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
            edad = safe_int(row.get("Age", 0))
            rango = clasificar_rango_edad(edad)
            liga_raw = str(row.get("Comp", ""))
            liga = NORMALIZAR_LIGA.get(liga_raw, liga_raw)

            resumen_liga[liga] = resumen_liga.get(liga, 0) + 1
            resumen_rango[rango] = resumen_rango.get(rango, 0) + 1

            minutos = safe_int(row.get("Min", 0))

            # ---- GOLES / ASISTENCIAS ----
            if etiqueta_temporada == "21/22":
                # En TU dataset 21/22, Goals y Assists son RATIOS (por 90 aprox.)
                goals_rate = safe_float(get_valor(row, "Gls", etiqueta_temporada, 0.0), 0.0)
                assists_rate = safe_float(get_valor(row, "Ast", etiqueta_temporada, 0.0), 0.0)
                gls = calc_total_from_rate(goals_rate, minutos)
                ast = calc_total_from_rate(assists_rate, minutos)
                g_a = gls + ast
            else:
                gls = safe_int(get_valor(row, "Gls", etiqueta_temporada, 0))
                ast = safe_int(get_valor(row, "Ast", etiqueta_temporada, 0))
                g_a = safe_int(get_valor(row, "G+A", etiqueta_temporada, gls + ast))

            doc = {
                "player": str(row.get("Player", "")),
                "nation": str(row.get("Nation", "")),
                "pos": str(row.get("Pos", "")),
                "age": edad,
                "born": safe_int(row.get("Born", 0)),
                "rango_edad": rango,
                "team_info": {
                    "squad": str(row.get("Squad", "")),
                    "comp": liga,
                    "temporada": etiqueta_temporada,
                },
                "stats_base": {
                    "mp": safe_int(row.get("MP", 0)),
                    "starts": safe_int(row.get("Starts", 0)),
                    "min": minutos,
                    "90s": safe_float(row.get("90s", 0)),
                },
                "stats_ataque": {
                    "gls": gls,
                    "ast": ast,
                    "g_a": g_a,
                    "g_pk": safe_int(get_valor(row, "G-PK", etiqueta_temporada, 0)),
                    "pk": safe_int(get_valor(row, "PK", etiqueta_temporada, 0)),
                    "pkatt": safe_int(row.get("PKatt", 0)),
                },
                "stats_disciplina": {
                    "crdy": safe_int(row.get("CrdY", 0)),
                    "crdr": safe_int(row.get("CrdR", 0)),
                },
                "stats_avanzadas": {
                    "xg": safe_float(get_valor(row, "xG", etiqueta_temporada, 0.0)),
                    "npxg": safe_float(get_valor(row, "npxG", etiqueta_temporada, 0.0)),
                    "xag": safe_float(get_valor(row, "xAG", etiqueta_temporada, 0.0)),
                    "npxg_xag": safe_float(get_valor(row, "npxG+xAG", etiqueta_temporada, 0.0)),
                    "prgc": safe_int(get_valor(row, "PrgC", etiqueta_temporada, 0)),
                    "prgp": safe_int(get_valor(row, "PrgP", etiqueta_temporada, 0)),
                    "prgr": safe_int(get_valor(row, "PrgR", etiqueta_temporada, 0)),
                },
                "stats_por_90": {
                    "gls_90": safe_float(get_valor(row, "Gls_90", etiqueta_temporada, 0.0)),
                    "ast_90": safe_float(get_valor(row, "Ast_90", etiqueta_temporada, 0.0)),
                    "g_a_90": safe_float(get_valor(row, "G+A_90", etiqueta_temporada, 0.0)),
                    "g_pk_90": safe_float(get_valor(row, "G-PK_90", etiqueta_temporada, 0.0)),
                    "g_a_pk_90": safe_float(get_valor(row, "G+A-PK_90", etiqueta_temporada, 0.0)),
                    "xg_90": safe_float(get_valor(row, "xG_90", etiqueta_temporada, 0.0)),
                    "xag_90": safe_float(get_valor(row, "xAG_90", etiqueta_temporada, 0.0)),
                    "xg_xag_90": safe_float(get_valor(row, "xG+xAG_90", etiqueta_temporada, 0.0)),
                    "npxg_90": safe_float(get_valor(row, "npxG_90", etiqueta_temporada, 0.0)),
                    "npxg_xag_90": safe_float(get_valor(row, "npxG+xAG_90", etiqueta_temporada, 0.0)),
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
        for r, total in sorted(resumen_rango.items()):
            print(f"  {r}: {total} jugadores")

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