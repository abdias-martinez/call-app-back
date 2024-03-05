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
            else:
                token = auth_user(username, connection, password, SECRET_KEY_CONFIG['token_secret_key'])
                if token:
                    return jsonify({"token": token})
                else:
                    return jsonify({"error": "Autenticacion fallida"}), 401

        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"error": "Error interno del servidor"}), 500
    
    except mysql.connector.Error:
        return jsonify({"type":"error", "message": "Error en la conexión"})
        
@app.route("/dashboard/<view>/<token>", methods=["POST"])
def insertRecordTable(view, token):
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        print("Conexion exitosa")
        if token != "" and user_is_authenticated(token, connection, SECRET_KEY_CONFIG['token_secret_key']):
            try:
                response = request.get_json()
                record = response["insertRecord"]
                sendData = insert_records_table(token, record, connection, view, SECRET_KEY_CONFIG['token_secret_key'])
                return jsonify(sendData)
            except Exception:
                return jsonify({"type":"error", "message": "Error interno del servidor"})
        else:
            return jsonify({"type": "error", "message": "No se encuentra autenticado"})
    except mysql.connector.Error:
        return jsonify({"type":"error", "message": "Falló la conexión con la base de datos"})

@app.route("/dashboard/<view>/<token>", methods=["GET"])
def obtainRecordsTable(view, token):
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        
        print(f"token: {token}")
        
        print(f"result: {user_is_authenticated(token, connection, SECRET_KEY_CONFIG['token_secret_key'])}")
        
        if token != "" and user_is_authenticated(token, connection, SECRET_KEY_CONFIG['token_secret_key']): 
            try:
                data = get_records_table(token, connection, view, SECRET_KEY_CONFIG['token_secret_key'])
                print(f"data: {data}")
                return jsonify(data)

            except Exception:
                return jsonify({"error": "Error interno del servidor"}), 500
        else:
            return jsonify({"type": "error", "message": "No se encuentra autenticado"})
        
    except mysql.connector.Error:
        return jsonify({"type":"error", "message": "Error en la conexión"})
        
@app.route("/dashboard/home/<token>", methods=["GET"])
def obtainAllTablesRecords(token):
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if token != "" and user_is_authenticated(token, connection, SECRET_KEY_CONFIG['token_secret_key']): 
            try:
                data = get_all_tables_records(token, connection, SECRET_KEY_CONFIG['token_secret_key'])
                return jsonify(data)

            except Exception:
                return jsonify({"error": "Error interno del servidor"}), 500 
        else:
            return jsonify({"type": "error", "message": "No se encuentra autenticado"})
    except mysql.connector.Error:
        return jsonify({"type":"error", "message": "Error en la conexión"})

@app.route("/dashboard/<view>/<token>", methods=["PUT"])
def updateRecordTable(view, token):
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        print("Conexion exitosa")
        
        if token != "" and user_is_authenticated(token, connection, SECRET_KEY_CONFIG['token_secret_key']): 
            try:
                response = request.get_json()
                identifier = response["identifier"]
                editedRecord = response["editedRecord"]
                originalRecord = response["originalRecord"]
                sendData = update_record_table_by_id(token, editedRecord, originalRecord, connection, identifier, view, SECRET_KEY_CONFIG['token_secret_key'])
                return jsonify(sendData)
            except Exception:
                return jsonify({"type":"error", "message": "Error en el servidor"})
        else: 
            return jsonify({"type": "error", "message": "No se encuentra autenticado"})
        
    except mysql.connector.Error:
        return jsonify({"type":"error", "message": "Error en la conexión"})
    
@app.route("/dashboard/<view>/<token>", methods=["DELETE"])
def deleteRecordTable(view, token):
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        print("Conexion exitosa")
        
        if token != "" and user_is_authenticated(token, connection, SECRET_KEY_CONFIG['token_secret_key']):
            try:
                response = request.get_json()
                record_id = response["recordIdentifier"]
                identifier = response["identifier"]
                sendData = delete_record_table_by_id(token, record_id, connection, identifier, view, SECRET_KEY_CONFIG['token_secret_key'])
                return jsonify(sendData)
            except Exception:
                return jsonify({"type":"error", "message": "Error en el servidor"})
        else:
            return jsonify({"type": "error", "message": "No se encuentra autenticado"})
        
    except mysql.connector.Error:
        return jsonify({"type":"error", "message": "Error en la conexión"})
        
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3005, debug=True)
