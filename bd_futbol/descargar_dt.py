import os
import sys
import pandas as pd
from pymongo import MongoClient

# Añadimos el directorio raíz del proyecto al path para poder importar config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bd_futbol.config import (
    MONGO_URI, MONGO_DB, MONGO_COLLECTION,
    RANGOS_EDAD, RUTA_2324, RUTA_2425
)


def clasificar_rango_edad(edad):
    """Clasifica un jugador en su rango de edad según la configuración."""
    for min_edad, max_edad, etiqueta in RANGOS_EDAD:
        if max_edad is None:
            if edad >= min_edad:
                return etiqueta
        elif min_edad <= edad <= max_edad:
            return etiqueta
    return "Desconocido"


def procesar_y_subir(ruta_excel, etiqueta_temporada, collection):
    """Carga un Excel, limpia los datos y los inserta en MongoDB."""
    try:
        print(f"\n--- Iniciando proceso para temporada: {etiqueta_temporada} ---")
        df = pd.read_excel(ruta_excel)

        # Columnas de texto que se rellenan con cadena vacía si están vacías
        columnas_texto = ["Player", "Nation", "Pos", "Squad", "Comp"]
        for col in columnas_texto:
            if col in df.columns:
                df[col] = df[col].fillna("")

        # Columnas numéricas: rellenamos NaN con 0
        columnas_numericas = [
            "Rk", "Age", "Born", "MP", "Starts", "Min", "90s",
            "Gls", "Ast", "G+A", "G-PK", "PK", "PKatt", "CrdY", "CrdR",
            "xG", "npxG", "xAG", "npxG+xAG", "PrgC", "PrgP", "PrgR",
            "Gls/90", "Ast/90", "G+A/90", "G-PK/90", "G+A-PK/90",
            "xG/90", "xAG/90", "xG+xAG/90", "npxG/90", "npxG+xAG/90",
        ]
        for col in columnas_numericas:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        jugadores_list = []
        # Contadores para el resumen final
        resumen_liga = {}
        resumen_rango = {}

        for _, row in df.iterrows():
            # Obtenemos la edad como entero
            edad = int(row.get("Age", 0))

            # Clasificamos el rango de edad
            rango = clasificar_rango_edad(edad)

            # Obtenemos la liga para el resumen
            liga = str(row.get("Comp", ""))
            resumen_liga[liga] = resumen_liga.get(liga, 0) + 1
            resumen_rango[rango] = resumen_rango.get(rango, 0) + 1

            # Construimos el documento MongoDB con estructura enriquecida
            doc = {
                "player": str(row.get("Player", "")),
                "nation": str(row.get("Nation", "")),
                "pos": str(row.get("Pos", "")),
                "age": edad,
                "born": int(row.get("Born", 0)),
                "rango_edad": rango,
                "team_info": {
                    "squad": str(row.get("Squad", "")),
                    "comp": liga,
                    "temporada": etiqueta_temporada,
                },
                "stats_base": {
                    "mp": int(row.get("MP", 0)),
                    "starts": int(row.get("Starts", 0)),
                    "min": int(row.get("Min", 0)),
                    "90s": float(row.get("90s", 0)),
                },
                "stats_ataque": {
                    "gls": int(row.get("Gls", 0)),
                    "ast": int(row.get("Ast", 0)),
                    "g_a": int(row.get("G+A", 0)),
                    "g_pk": int(row.get("G-PK", 0)),
                    "pk": int(row.get("PK", 0)),
                    "pkatt": int(row.get("PKatt", 0)),
                },
                "stats_disciplina": {
                    "crdy": int(row.get("CrdY", 0)),
                    "crdr": int(row.get("CrdR", 0)),
                },
                "stats_avanzadas": {
                    "xg": float(row.get("xG", 0)),
                    "npxg": float(row.get("npxG", 0)),
                    "xag": float(row.get("xAG", 0)),
                    "npxg_xag": float(row.get("npxG+xAG", 0)),
                    "prgc": int(row.get("PrgC", 0)),
                    "prgp": int(row.get("PrgP", 0)),
                    "prgr": int(row.get("PrgR", 0)),
                },
                "stats_por_90": {
                    "gls_90": float(row.get("Gls/90", 0)),
                    "ast_90": float(row.get("Ast/90", 0)),
                    "g_a_90": float(row.get("G+A/90", 0)),
                    "g_pk_90": float(row.get("G-PK/90", 0)),
                    "g_a_pk_90": float(row.get("G+A-PK/90", 0)),
                    "xg_90": float(row.get("xG/90", 0)),
                    "xag_90": float(row.get("xAG/90", 0)),
                    "xg_xag_90": float(row.get("xG+xAG/90", 0)),
                    "npxg_90": float(row.get("npxG/90", 0)),
                    "npxg_xag_90": float(row.get("npxG+xAG/90", 0)),
                },
            }
            jugadores_list.append(doc)

        # Insertamos todos los jugadores en MongoDB
        if jugadores_list:
            collection.insert_many(jugadores_list)
            print(f"ÉXITO: Se han subido {len(jugadores_list)} jugadores de la temporada {etiqueta_temporada}.")

        # Mostramos el resumen por liga y por rango de edad
        print(f"\nResumen por liga ({etiqueta_temporada}):")
        for liga, total in sorted(resumen_liga.items()):
            print(f"  {liga}: {total} jugadores")

        print(f"\nResumen por rango de edad ({etiqueta_temporada}):")
        for rango, total in sorted(resumen_rango.items()):
            print(f"  {rango}: {total} jugadores")

    except FileNotFoundError:
        print(f"ERROR: No se encontró el archivo '{ruta_excel}'. "
              f"Descárgalo de Kaggle y colócalo en la carpeta 'data/'.")
    except Exception as e:
        print(f"ERROR procesando {etiqueta_temporada}: {e}")


def main():
    # Conexión a MongoDB
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    collection = db[MONGO_COLLECTION]

    # Procesamos cada temporada
    temporadas = [
        (RUTA_2324, "23/24"),
        (RUTA_2425, "24/25"),
    ]

    for ruta, etiqueta in temporadas:
        # Comprobamos si ya existen datos de esta temporada en la colección
        existentes = collection.count_documents({"team_info.temporada": etiqueta})
        if existentes > 0:
            respuesta = input(
                f"\nYa existen {existentes} registros de la temporada {etiqueta}. "
                f"¿Deseas sobreescribirlos? (s/n): "
            ).strip().lower()
            if respuesta in ("s", "si", "y", "yes"):
                # Eliminamos los registros existentes antes de reinsertar
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