from flask import Flask, jsonify, request
from utils import *
from config import *
import mysql.connector
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app)

# ruta para el proceso de inicio de sesión
@app.route("/login", methods=["POST"])
def login():
    try:
        # conexión a la base de datos
        connection = mysql.connector.connect(**DB_CONFIG)
        print("Conexion exitosa")

        try:
            # obtenemos datos de la solicitud JSON
            data = request.get_json()
            username = data.get("username")
            password = data.get("password")

            print(f"username: {username}, password: {password}")

            # Validamos el nombre de usuario y contraseña
            if not username or not password:
                return jsonify({"error": "Usuario y contraseña son requeridos"}), 400
            else:
                # generamos un token
                token = auth_user(username, connection, password, SECRET_KEY_CONFIG['token_secret_key'])
                if token:
                    print("Autenticacion exitosa")
                    return jsonify({"token": token})
                else:
                    print("Autenticacion fallida")
                    return jsonify({"error": "Autenticacion fallida"}), 401

        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"error": "Error interno del servidor"}), 500

    except mysql.connector.Error as err:
        print(f"Error de conexion: {err}")
        return jsonify({"type": "error", "message": "Error en la conexión"})

# Ruta para insertar registros en una tabla
@app.route("/dashboard/<view>/<token>", methods=["POST"])
def insertRecordTable(view, token):
    try:
        # conexión a la base de datos
        connection = mysql.connector.connect(**DB_CONFIG)
        print("Conexion exitosa")

        # verificamos si el usuario cuenta con autenticación
        if token != "" and user_is_authenticated(token, connection, SECRET_KEY_CONFIG['token_secret_key']):
            try:
                response = request.get_json()
                record = response["insertRecord"]
                # insertamos el registro en la tabla
                sendData = insert_records_table(token, record, connection, view, SECRET_KEY_CONFIG['token_secret_key'])
                return jsonify(sendData)
            except Exception as e:
                print(f"Error: {e}")
                return jsonify({"type": "error", "message": "Error interno del servidor"})
        else:
            print("No se encuentra autenticado")
            return jsonify({"type": "error", "message": "No se encuentra autenticado"})

    except mysql.connector.Error as err:
        print(f"Error de conexion: {err}")
        return jsonify({"type": "error", "message": "Falló la conexión con la base de datos"})

# Ruta para obtener registros de una tabla específica
@app.route("/dashboard/<view>/<token>", methods=["GET"])
def obtainRecordsTable(view, token):
    try:
        # conexión a la base de datos
        connection = mysql.connector.connect(**DB_CONFIG)

        print(f"token: {token}")

        # verificamos si el usuario cuenta con autenticación
        print(f"result: {user_is_authenticated(token, connection, SECRET_KEY_CONFIG['token_secret_key'])}")
        if token != "" and user_is_authenticated(token, connection, SECRET_KEY_CONFIG['token_secret_key']):
            try:
                # obtenemos los registros de la tabla
                data = get_records_table(token, connection, view, SECRET_KEY_CONFIG['token_secret_key'])
                print(f"data: {data}")
                return jsonify(data)

            except Exception as e:
                print(f"Error: {e}")
                return jsonify({"error": "Error interno del servidor"}), 500
        else:
            print("No se encuentra autenticado")
            return jsonify({"type": "error", "message": "No se encuentra autenticado"})

    except mysql.connector.Error as err:
        print(f"Error de conexion: {err}")
        return jsonify({"type": "error", "message": "Error en la conexión"})

# Ruta para obtener todos los registros de todas las tablas
@app.route("/dashboard/home/<token>", methods=["GET"])
def obtainAllTablesRecords(token):
    try:
        # conexión a la base de datos
        connection = mysql.connector.connect(**DB_CONFIG)
        if token != "" and user_is_authenticated(token, connection, SECRET_KEY_CONFIG['token_secret_key']):
            try:
                # Obtenemos los registros de todas las tablas
                data = get_all_tables_records(token, connection, SECRET_KEY_CONFIG['token_secret_key'])
                return jsonify(data)

            except Exception as e:
                print(f"Error: {e}")
                return jsonify({"error": "Error interno del servidor"}), 500 
        else:
            print("No se encuentra autenticado")
            return jsonify({"type": "error", "message": "No se encuentra autenticado"})
    except mysql.connector.Error as err:
        print(f"Error de conexion: {err}")
        return jsonify({"type": "error", "message": "Error en la conexión"})

# Ruta para actualizar un registro en una tabla
@app.route("/dashboard/<view>/<token>", methods=["PUT"])
def updateRecordTable(view, token):
    try:
        # conexión a la base de datos
        connection = mysql.connector.connect(**DB_CONFIG)
        print("Conexion exitosa")

        # verificamos si el usuario cuenta con autenticación
        if token != "" and user_is_authenticated(token, connection, SECRET_KEY_CONFIG['token_secret_key']):
            try:
                response = request.get_json()
                identifier = response["identifier"]
                editedRecord = response["editedRecord"]
                originalRecord = response["originalRecord"]
                # Actualizar registro en la tabla por identificador
                sendData = update_record_table_by_id(token, editedRecord, originalRecord, connection, identifier, view, SECRET_KEY_CONFIG['token_secret_key'])
                return jsonify(sendData)
            except Exception as e:
                print(f"Error: {e}")
                return jsonify({"type": "error", "message": "Error en el servidor"})
        else:
            print("No se encuentra autenticado")
            return jsonify({"type": "error", "message": "No se encuentra autenticado"})

    except mysql.connector.Error as err:
        print(f"Error de conexion: {err}")
        return jsonify({"type": "error", "message": "Error en la conexión"})

# Ruta para eliminar un registro de una tabla
@app.route("/dashboard/<view>/<token>", methods=["DELETE"])
def deleteRecordTable(view, token):
    try:
        # conexión a la base de datos
        connection = mysql.connector.connect(**DB_CONFIG)
        print("Conexion exitosa")

        # verificamos si el usuario cuenta con autenticación
        if token != "" and user_is_authenticated(token, connection, SECRET_KEY_CONFIG['token_secret_key']):
            try:
                response = request.get_json()
                record_id = response["recordIdentifier"]
                identifier = response["identifier"]
                # eliminamos cierto registro de la tabla
                sendData = delete_record_table_by_id(token, record_id, connection, identifier, view, SECRET_KEY_CONFIG['token_secret_key'])
                return jsonify(sendData)
            except Exception as e:
                print(f"Error: {e}")
                return jsonify({"type": "error", "message": "Error en el servidor"})
        else:
            print("No se encuentra autenticado")
            return jsonify({"type": "error", "message": "No se encuentra autenticado"})

    except mysql.connector.Error as err:
        print(f"Error de conexion: {err}")
        return jsonify({"type": "error", "message": "Error en la conexión"})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3005, debug=True)