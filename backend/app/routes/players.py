from typing import Optional
from fastapi import APIRouter, Query, HTTPException

from app.db import get_collection

router = APIRouter()


def _serialize(doc: dict) -> dict:
    doc = dict(doc)
    doc["_id"] = str(doc.get("_id"))
    return doc


@router.get("/players/search")
def search_players(
    name: Optional[str] = Query(default=None, description="Nombre (contiene, case-insensitive)"),
    temporada: Optional[str] = Query(default=None, description='Ej: "23/24" o "24/25"'),
    squad: Optional[str] = Query(default=None, description="Equipo exacto"),
    comp: Optional[str] = Query(default=None, description="Liga exacta"),
    pos: Optional[str] = Query(default=None, description="Posición exacta"),
    rango_edad: Optional[str] = Query(default=None, description='Ej: "18-27", "28-37", "38+"'),
    min_minutes: int = Query(default=0, ge=0),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
):
    col = get_collection()

    q = {}
    if name:
        q["player"] = {"$regex": name, "$options": "i"}
    if temporada:
        q["team_info.temporada"] = temporada
    if squad:
        q["team_info.squad"] = squad
    if comp:
        q["team_info.comp"] = comp
    if pos:
        q["pos"] = pos
    if rango_edad:
        q["rango_edad"] = rango_edad
    if min_minutes and min_minutes > 0:
        q["stats_base.min"] = {"$gte": min_minutes}

    skip = (page - 1) * page_size

    cursor = (
        col.find(q, projection={
            "player": 1,
            "nation": 1,
            "pos": 1,
            "age": 1,
            "rango_edad": 1,
            "team_info": 1,
            "stats_base.min": 1,
            "stats_ataque.gls": 1,
            "stats_ataque.ast": 1,
        })
        .sort([("player", 1), ("team_info.temporada", 1)])
        .skip(skip)
        .limit(page_size)
    )

    items = [_serialize(d) for d in cursor]
    total = col.count_documents(q)

    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "items": items,
    }


@router.get("/player")
def get_player_by_name_and_squad(
    name: str = Query(..., description="Nombre exacto del jugador (tal como viene en BD)"),
    squad: str = Query(..., description="Equipo exacto"),
):
    col = get_collection()

    q = {"player": name, "team_info.squad": squad}
    docs = list(col.find(q).sort([("team_info.temporada", 1)]))

    if not docs:
        raise HTTPException(status_code=404, detail="Jugador no encontrado para ese equipo")

    return {
        "player": name,
        "squad": squad,
        "seasons": [_serialize(d) for d in docs],
    }
