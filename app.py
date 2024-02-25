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
            print(f"")
            name_table = response["nameTable"]
            record = response["insertRecord"]
            print(f"response: {response}, name_table: {name_table}, record: {record}, sources: {sources}")
            print("-- INSERTANDO REGISTRO A LA BASE DE DATOS --")
            if name_table == TB_NAMES[sources]['name']:
                insert_records_table(record, connection, name_table)
                return jsonify({"message": "Registro insertado exitosamente!"})
            else:
                return jsonify({"message": "ERROR: El registro no fue insertado!"})

        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"error": "Error interno del servidor"}), 500
    except mysql.connector.Error as err:
        print(f"Error de conexion: {err}")
        exit(1)

@app.route("/dashboard/<sources>", methods=["GET"])
def obtainRecordsTable(sources):
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        print("Conexion exitosa")
        try:
            response = request.get_json()
            name_table = response["nameTable"]
            #print(f"response: {response}, name_table: {name_table}, sources: {sources}")
            print(f"-- OBTENIENDO LOS REGISTROS DE '{name_table}' DE LA BD --")
            #print(f"rsult: {TB_NAMES[sources]['name']}")
            data = get_records_table(connection, sources, name_table) if name_table == TB_NAMES[sources]['name'] else {}
            #print(data)
            print(f"-- ENVIANDO LOS REGISTROS DE '{name_table}' AL FRONTEND --")
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
            id = response["recordId"]
            record = response["editedRecord"]
            name_table = response["nameTable"]
            print(f"id: {id}, record: {record}, name_table: {name_table}")
            print(f"-- RECIBIENDO DATOS PARA ACTUALIZAR LA TABLA ${name_table}--")

            if name_table == TB_NAMES[sources]['name']:
                update_record_table_by_id(id, record, connection, name_table)
                return jsonify({"message": f"R con ID {id} actualizado correctamente"})
            else:
                return jsonify({"message": "ERROR: El id del registro no fue encontrado!"})

        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"error": "Error interno del servidor"}), 500
    except mysql.connector.Error as err:
        print(f"Error de conexion: {err}")
        exit(1)
    
@app.route("/dashboard/<sources>", methods=["DELETE"])
def deleteRecordTable(sources):
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        print("Conexion exitosa")
        try:
            response = request.get_json()
            id = response["recordId"]
            name_table = response["nameTable"]
            print(f"id: {id}, name_table: {name_table}")
            print(f"-- RECIBIENDO DATOS PARA ELIMINAR REGISTRO DE LA TABLA ${name_table}--")

            if name_table == TB_NAMES[sources]['name']:
                delete_record_table_by_id(id, connection, name_table)
                return jsonify({"message": f"R con ID {id} actualizado correctamente"})
            else:
                return jsonify({"message": "ERROR: El id del registro no fue encontrado!"})

        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"error": "Error interno del servidor"}), 500
    except mysql.connector.Error as err:
        print(f"Error de conexion: {err}")
        exit(1)
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3005, debug=True)
