from flask import Flask, jsonify, request
from utils import *
from config import *
import mysql.connector
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app)
    
@app.route("/login", methods=["POST"])
def login():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        print("Conexion exitosa")
        try:
            data = request.get_json()
            username = data.get("username")
            password = data.get("password")

            print(f"username: {username}, password: {password}")
            if not username or not password:
                return jsonify({"error": "Usuario y contraseña son requeridos"}), 400
            token = authUser(username, connection, password, SECRET_KEY_CONFIG['jwt_secret_key'])
            if token:
                return jsonify({"token": token})
            else:
                return jsonify({"error": "Autenticacion fallida"}), 401

        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"error": "Error interno del servidor"}), 500
    
    except mysql.connector.Error as err:
        print(f"Error de conexion: {err}")
        exit(1)
        
@app.route("/dashboard/<sources>", methods=["POST"])
def insertRecordTable(sources):
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        print("Conexion exitosa")
        try:
            print("-- RECIBIENDO DATOS DEL FRONTEND --")
            response = request.get_json()
            name_table = TB_NAMES[sources]['name']
            record = response["insertRecord"]
            print(f"response: {response}, name_table: {name_table}, record: {record}, sources: {sources}")
            print("-- INSERTANDO REGISTRO A LA BASE DE DATOS --")
            if name_table:
                sendData = insert_records_table(record, connection, name_table)
                return jsonify(sendData)
            else:
                return jsonify({"type": "error", "message": "Tabla no encontrada"})

        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"type":"error", "message": "Error interno del servidor"})
    except mysql.connector.Error as err:
        return jsonify({"type":"error", "message": "Falló la conexión con la base de datos"})
        exit(1)

@app.route("/dashboard/<sources>", methods=["GET"])
def obtainRecordsTable(sources):
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        print("Conexion exitosa")
        try:
            name_table = TB_NAMES[sources]['name']

            print(f"-- OBTENIENDO LOS REGISTROS DE '{name_table}' DE LA BD --")

            data = get_records_table(connection, sources, name_table)

            print(f"-- ENVIANDO LOS REGISTROS DE '{name_table}' AL FRONTEND --")
            print(f"sendData: {data}")
            return jsonify(data)

        except KeyError:
            return jsonify({"error": f"La tabla '{sources}' no está definida en TB_NAMES"}), 400

        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"error": "Error interno del servidor"}), 500

    except mysql.connector.Error as err:
        print(f"Error de conexion: {err}")
        exit(1)
        
@app.route("/dashboard/home", methods=["GET"])
def obtainAllTablesRecords():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        print("Conexion exitosa")
        try:
            data = get_all_tables_records(connection)
            print(f"-- ENVIANDO TODAS LAS TABLAS AL FRONTEND --")
            print(f"sendData: {data}")
            return jsonify(data) 
        
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"error": "Error interno del servidor"}), 500

    except mysql.connector.Error as err:
        print(f"Error de conexion: {err}")
        exit(1)

@app.route("/dashboard/<sources>", methods=["PUT"])
def updateRecordTable(sources):
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        print("Conexion exitosa")
        try:
            response = request.get_json()
            identifier = response["identifier"]
            editedRecord = response["editedRecord"]
            originalRecord = response["originalRecord"]
            name_table = TB_NAMES[sources]['name']
            print(f"id: {identifier}, editedRecord: {editedRecord}, originalRecord: {originalRecord}, name_table: {name_table}")
            print(f"-- RECIBIENDO DATOS PARA ACTUALIZAR LA TABLA {name_table}--")

            if name_table:
                sendData = update_record_table_by_id(editedRecord, originalRecord, connection, identifier, name_table)
                return jsonify(sendData)
            else:
                return jsonify({'type': 'error', 'message': 'Tabña no encontrada'})

        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"type":"error", "message": "Error en el servidor"})
    except mysql.connector.Error as err:
        return jsonify({"type":"error", "message": "Error en la conexión"})
        exit(1)
    
@app.route("/dashboard/<sources>", methods=["DELETE"])
def deleteRecordTable(sources):
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        print("Conexion exitosa")
        try:
            response = request.get_json()
            record_id = response["recordIdentifier"]
            identifier = response["identifier"]
            name_table = TB_NAMES[sources]['name']
            print(f"id: {record_id}, identifier:{identifier}, name_table: {name_table}")
            print(f"-- RECIBIENDO DATOS PARA ELIMINAR REGISTRO DE LA TABLA ${name_table}--")

            if name_table:
                sendData = delete_record_table_by_id(record_id, connection, identifier, name_table)
                return jsonify(sendData)
            else:
                return jsonify({'type': 'error', 'message': 'Tabla no encontrada'})

        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"type":"error", "message": "Error en el servidor"})
    except mysql.connector.Error as err:
        return jsonify({"type":"error", "message": "Error en la conexión"})
        exit(1)
        
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3005, debug=True)
