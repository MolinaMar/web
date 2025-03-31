from pymongo import MongoClient

# Conexión a MongoDB
cliente = MongoClient("mongodb://localhost:27017/")

# Seleccionar la base de datos
db = cliente["python_db"]

# Seleccionar la colección
usuarios = db["usuarios"]

# Verificar conexión
if "python_db" in cliente.list_database_names():
    print("Conexión a MongoDB establecida correctamente.")
else:
    print("Error en la conexión a MongoDB.")
