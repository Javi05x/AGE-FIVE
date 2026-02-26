import pandas as pd
from pymongo import MongoClient

# Configuración de conexión
client = MongoClient('mongodb://localhost:27017/')
db = client['ProyectoFutbol']
collection = db['Jugadores']

def procesar_y_subir(ruta_excel, etiqueta_temporada):
    try:
        print(f"--- Iniciando proceso para temporada: {etiqueta_temporada} ---")
        df = pd.read_excel(ruta_excel)

        # --- LIMPIEZA DE DATOS (Soluciona el error NaN) ---
        # Rellenamos celdas vacías con 0 para evitar errores de conversión
        df['Age'] = df['Age'].fillna(0)
        df['Gls'] = df['Gls'].fillna(0)
        df['Min'] = df['Min'].fillna(0)
        # --------------------------------------------------

        jugadores_list = []

        for _, row in df.iterrows():
            # Convertimos a entero de forma segura
            edad = int(row['Age'])
            
            # Clasificación de edad (Rango)
            if edad == 0:
                rango = "Desconocido"
            elif 18 <= edad <= 27:
                rango = "18-27"
            elif 28 <= edad <= 37:
                rango = "28-37"
            else:
                rango = "38+"

            # Estructura del documento NoSQL
            doc = {
                "player": row['Player'],
                "age": edad,
                "rango_edad": rango,
                "team_info": {
                    "squad": row['Squad'],
                    "comp": row['Comp'],
                    "temporada": etiqueta_temporada
                },
                "stats_base": {
                    # Convertimos también stats a int para que MongoDB los reconozca como números
                    "gls": int(row['Gls']),
                    "minutos": int(row['Min'])
                }
            }
            jugadores_list.append(doc)

        # Insertar en MongoDB
        if jugadores_list:
            collection.insert_many(jugadores_list)
            print(f"ÉXITO: Se han subido {len(jugadores_list)} jugadores de la {etiqueta_temporada}.")
        
    except Exception as e:
        print(f"ERROR procesando {etiqueta_temporada}: {e}")

# ==========================================================
# CONFIGURA AQUÍ TUS ARCHIVOS
# ==========================================================

ruta_2324 = r'C:\Users\Usuario\Documents\Cosas JAVIER\Asignaturas UNIVERSIDAD\TERCER CURSO\Segundo cuatri\BDNR\Proyecto\bd_futbol\all-football-players-stats-in-top-5-leagues-2324\versions\1\top5-players.xlsx'
ruta_2425 = r'C:\Users\Usuario\Documents\Cosas JAVIER\Asignaturas UNIVERSIDAD\TERCER CURSO\Segundo cuatri\BDNR\Proyecto\bd_futbol\all-football-players-stats-in-top-5-leagues-2425\versions\1\top5-players24-25.xlsx'

# EJECUCIÓN
procesar_y_subir(ruta_2324, "23/24")
procesar_y_subir(ruta_2425, "24/25")