from fastapi import APIRouter
from app.db import get_collection

router = APIRouter()


@router.get("/filters/temporadas")
def temporadas():
    return ["23/24", "24/25"]


@router.get("/filters/rangos")
def rangos():
    return ["18-27", "28-37", "38+"]


@router.get("/filters/squads")
def squads():
    col = get_collection()
    vals = col.distinct("team_info.squad")
    return sorted([v for v in vals if v])


@router.get("/filters/comps")
def comps():
    col = get_collection()
    vals = col.distinct("team_info.comp")
    return sorted([v for v in vals if v])


@router.get("/filters/pos")
def positions():
    col = get_collection()
    vals = col.distinct("pos")
    return sorted([v for v in vals if v])
