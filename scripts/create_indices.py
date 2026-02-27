from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017/"
DB = "ProyectoFutbol"
COL = "Jugadores"

client = MongoClient(MONGO_URI)
col = client[DB][COL]

print("Creating indexes...")

col.create_index([("player", 1)])
col.create_index([("team_info.squad", 1)])
col.create_index([("team_info.temporada", 1)])
col.create_index([("player", 1), ("team_info.squad", 1), ("team_info.temporada", 1)])

print("Done. Indexes:", col.index_information())
client.close()
