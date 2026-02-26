import os
from dotenv import load_dotenv

# Cargamos las variables de entorno desde el fichero .env (si existe)
load_dotenv()

# URI de conexión a MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")

# Nombre de la base de datos
MONGO_DB = os.getenv("MONGO_DB", "ProyectoFutbol")

# Nombre de la colección donde se almacenan los jugadores
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "Jugadores")

# Rangos de edad para clasificar a los jugadores
RANGOS_EDAD = [
    (18, 27, "18-27"),   # Jugadores jóvenes
    (28, 37, "28-37"),   # Jugadores en plenitud
    (38, None, "38+"),   # Jugadores veteranos
]

# Rutas a los archivos Excel de Kaggle (relativas a la raíz del proyecto)
RUTA_2324 = os.getenv("RUTA_2324", "data/top5-players-2324.xlsx")
RUTA_2425 = os.getenv("RUTA_2425", "data/top5-players-2425.xlsx")
