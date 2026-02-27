from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.players import router as players_router
from app.routes.filters import router as filters_router

app = FastAPI(title="AGE-FIVE API", version="0.1.0")

# En dev con Vite suele ser http://localhost:5173
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(players_router, prefix="/api", tags=["players"])
app.include_router(filters_router, prefix="/api", tags=["filters"])


@app.get("/health")
def health():
    return {"status": "ok"}
