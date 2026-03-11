import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymongo import MongoClient, ASCENDING, DESCENDING
from bd_futbol.config import MONGO_URI, MONGO_DB, MONGO_COLLECTION

def crear_indices():
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    collection = db[MONGO_COLLECTION]

    print("Creando índices...")

    # Búsqueda por nombre de jugador
    collection.create_index([("player", ASCENDING)], name="idx_player")

    # Filtros más comunes
    collection.create_index([("team_info.temporada", ASCENDING)], name="idx_temporada")
    collection.create_index([("team_info.comp", ASCENDING)], name="idx_liga")
    collection.create_index([("pos", ASCENDING)], name="idx_posicion")
    collection.create_index([("rango_edad", ASCENDING)], name="idx_rango_edad")

    # Análisis de rendimiento
    collection.create_index([("stats_ataque.gls", DESCENDING)], name="idx_goles")
    collection.create_index([("stats_ataque.ast", DESCENDING)], name="idx_asistencias")
    collection.create_index([("stats_avanzadas.xg", DESCENDING)], name="idx_xg")

    # Índice compuesto para filtros combinados (temporada + liga + posición)
    collection.create_index(
        [("team_info.temporada", ASCENDING),
         ("team_info.comp", ASCENDING),
         ("pos", ASCENDING)],
        name="idx_temporada_liga_pos"
    )

    print("Índices creados:")
    for idx in collection.list_indexes():
        print(f"  ✅ {idx['name']}")

    client.close()

if __name__ == "__main__":
    crear_indices()