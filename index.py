from flask import Flask, render_template, request, redirect, session, url_for, send_from_directory
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId  # Importamos ObjectId para trabajar con el ID de MongoDB
from werkzeug.utils import secure_filename
import os

# Conexión a la base de datos
from db import usuarios

app = Flask(__name__)
app.secret_key = "tu_secreto"

# Configuración de las rutas de los archivos
UPLOAD_FOLDER = 'uploads'
DOWNLOAD_FOLDER = 'downloads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

@app.route("/")
def home():
    print(f"Usuario en sesión: {session.get('usuario')} - Rol: {session.get('rol')}")  # Verificación de sesión
    if "usuario" in session:
        # Obtener los archivos en la carpeta 'uploads' para mostrar en la tabla
        archivos = os.listdir(app.config['UPLOAD_FOLDER'])
        return render_template("home.html", nombre=session["usuario"], archivos=archivos)
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        correo = request.form["correo"]
        password = request.form["password"]
        usuario = usuarios.find_one({"correo": correo})
        
        if usuario and check_password_hash(usuario["password"], password):
            session["usuario"] = usuario["nombre"]
            session["rol"] = usuario.get("rol", "usuario")
            
            # Agregamos el print para depurar el valor de "rol"
            print(f"Rol del usuario: {session['rol']}")  # Línea de depuración

            if session["rol"] == "admin":
                return redirect(url_for("admin"))
            return redirect(url_for("home"))
        else:
            return "Credenciales incorrectas", 401
    
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nombre = request.form["nombre"]
        correo = request.form["correo"]
        password = generate_password_hash(request.form["password"])
        
        if usuarios.find_one({"correo": correo}):
            return "El correo ya está registrado", 400
        
        rol = "admin" if request.form.get("admin") else "usuario"
        usuarios.insert_one({"nombre": nombre, "correo": correo, "password": password, "rol": rol})
        return redirect(url_for("login"))
    
    return render_template("register.html")

@app.route("/admin")
def admin():
    try:
        if "usuario" in session and session.get("rol") == "admin":
            print("Conexión a la base de datos está funcionando.")  # Verificación de conexión
            usuarios_lista = list(usuarios.find())
            return render_template("admin.html", usuarios=usuarios_lista)
        return redirect(url_for("login"))
    except Exception as e:
        # Si ocurre algún error, lo imprime en la consola
        print(f"Error en la ruta /admin: {e}")
        return "Ocurrió un error en la página de administrador", 500

@app.route("/eliminar_usuario/<id>", methods=["GET"])
def eliminar_usuario(id):
    try:
        usuarios.delete_one({"_id": ObjectId(id)})
        return redirect(url_for("admin"))
    except Exception as e:
        print(f"Error al eliminar usuario con ID {id}: {e}")
        return "Ocurrió un error al eliminar el usuario", 500

@app.route("/logout")
def logout():
    session.pop("usuario", None)
    session.pop("rol", None)
    return redirect(url_for("login"))

# Ruta para subir el archivo cifrado
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    
    return {"message": "Archivo subido correctamente"}, 200

# Ruta para descargar el archivo (después de descifrarlo)
@app.route('/download', methods=['GET'])
def download_file():
    filename = request.args.get('filename')
    if not filename:
        return 'No filename provided', 400

    try:
        # Cambié el directorio de descarga a 'uploads' en lugar de 'downloads'
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    except Exception as e:
        return f"Error al descargar el archivo: {e}", 500


if __name__ == "__main__":
    app.run(debug=True)
