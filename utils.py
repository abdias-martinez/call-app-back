import mysql.connector
import json
import jwt
from datetime import datetime
from config import TB_NAMES

def json_to_dict(json_string: str) -> dict:
    try:
        dictionary = json.loads(json_string)
        return dictionary

    except json.JSONDecodeError as e:
        print(f"Error al decodificar JSON: {e}")
        return {}
    
def format_datetime(value):
    # Función para formatear una columna de tipo datetime
    if isinstance(value, datetime):
        return value.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return value

def insert_records_table(data_dict: dict, connection: mysql.connector.connection.MySQLConnection, table_name: str) -> dict:
    try:
        cursor = connection.cursor()

        if table_name == 'Usuarios':
            existing_user_query = f"SELECT COUNT(*) FROM {table_name} WHERE Usuario = %s"
            cursor.execute(existing_user_query, (data_dict['Usuario'],))
            user_count = cursor.fetchone()[0]
            print(f"user_count: {user_count}")

            if user_count > 0:
                return {'type': 'error', 'message': 'Usuario ya existe'}

        columns = ', '.join(data_dict.keys())
        print(f"columns: {columns}")
        placeholders = ', '.join(['%s'] * len(data_dict))
        print(f"placeholders: {placeholders}")
        sql_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        values = tuple(data_dict.values())
        print(f"query: {sql_query}, values to insert: {values}")

        cursor.execute(sql_query, values)

        connection.commit()

        print(f"Datos registrados exitosamente en la tabla {table_name}!")

        return {'type': 'success', 'message': 'Registro insertado'}

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return {'type': 'error', 'message': 'Error en la inserción'}

    finally:
        cursor.close()
        
        
def get_records_table(connection: mysql.connector.connection.MySQLConnection, sources:str, table_name: str) -> str:
    try:
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute(f"SHOW COLUMNS FROM {table_name}")
        columns = [column['Field'] for column in cursor.fetchall()]
        
        columns_except_id = [column for column in columns if column.lower() != 'id']
        columns_str = ', '.join(columns_except_id)
            
        sql_query = f"SELECT {columns_str} FROM {table_name}"
        cursor.execute(sql_query)

        records = cursor.fetchall()

        # Formatear columnas datetime como cadenas de texto
        formatted_records = []
        for record in records:
            formatted_record = {key: format_datetime(value) for key, value in record.items()}
            formatted_records.append(formatted_record)

        json_result = json.dumps(formatted_records, indent=2)

        return json_result

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return "{}"

    finally:
        cursor.close()

        
                
def get_all_tables_records(connection: mysql.connector.connection.MySQLConnection) -> str:
    try:
        cursor = connection.cursor(dictionary=True)

        print("Obteniendo la lista de tablas")
        cursor.execute("SHOW TABLES")
        tables = [table['Tables_in_CAE'] for table in cursor.fetchall()]

        print(f"tables: {tables}")

        all_tables_data = {}

        for table_name in tables:
            cursor.execute(f"SHOW COLUMNS FROM {table_name}")
            columns_info = cursor.fetchall()
            columns = [column['Field'] for column in columns_info]

            columns_except_id = [column for column in columns if column.lower() != 'id']
            #columns_except_id = [column for column in columns]

            columns_str = ', '.join(columns_except_id)

            sql_query = f"SELECT {columns_str} FROM {table_name}"
            cursor.execute(sql_query)

            records = cursor.fetchall()

            # Formatear columnas de tipo datetime en cada registro
            formatted_records = []
            for record in records:
                formatted_record = {key: format_datetime(value) for key, value in record.items()}
                formatted_records.append(formatted_record)

            # Agregar datos de la tabla al diccionario
            table_data = {
                "table_name": table_name,
                "records": formatted_records
            }

            all_tables_data[table_name] = table_data

        json_result = json.dumps(all_tables_data, default=str, indent=2)

        return json_result

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return "{}"

    finally:
        cursor.close()
        
import mysql.connector

def update_record_table_by_id(new_data_dict: dict, original_data_dict: dict, connection: mysql.connector.connection.MySQLConnection, identifier: str, table_name: str) -> dict:
    try:
        cursor = connection.cursor()

        set_clause = ', '.join([f"{key} = %s" for key in new_data_dict.keys()])
        where_condition = f"{identifier} = %s"

        sql_query = f"UPDATE {table_name} SET {set_clause} WHERE {where_condition}"
        values = tuple([new_data_dict[key] for key in new_data_dict.keys()] + [original_data_dict[identifier]])
        
        cursor.execute(sql_query, values)

        connection.commit()

        return {'type': 'success', 'message': 'Registro editado'}

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return {'type': 'error', 'message': 'Error en la edición'}

    finally:
        cursor.close()


def delete_record_table_by_id(id: str, connection: mysql.connector.connection.MySQLConnection, identifier: str, table_name: str) -> None:
    try:
        cursor = connection.cursor()
        
        where_condition = f"{identifier} = %s"
        
        sql_query = f"DELETE FROM {table_name} WHERE {where_condition}"
        values = tuple([id])

        print(f"sql_query: {sql_query}, values: {values}")        
        
        cursor.execute(sql_query, values)

        connection.commit()

        return {'type': 'success', 'message': 'Registro eliminado'}

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return {'type': 'error', 'message': 'Error en la eliminación'}

    finally:
        cursor.close()
        
        
def get_info_user(id: int, connection: mysql.connector.connection.MySQLConnection) -> str:
    try:
        cursor = connection.cursor(dictionary=True)

        sql_query = f"SELECT Perfil, Usuario FROM Usuarios WHERE Id = '{id}'"
        cursor.execute(sql_query)
        
        record = cursor.fetchone()
        
        data_dict = {
            'personal_data': {
                'userId': id,
                'name': record.Usuario,
                'userType': record.Perfil,
            }
        }
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return "{}"

    finally:
        cursor.close()


def authUser(username: str, connection: mysql.connector.connection.MySQLConnection, password: str, secret_key: str) -> str:
    try:
        cursor = connection.cursor(dictionary=True)
        sql_query = "SELECT Usuario, Contraseña, Id, Perfil FROM Usuarios WHERE Usuario = %s"
        cursor.execute(sql_query, (username,))

        record = cursor.fetchone()

        if record and record['Contraseña'] == password:
            user_id = record['Id']
            user_rol = record['Perfil']
            print(f"Usaurio {username} autenticado exitosamente!")

            token = jwt.encode({'user_id': user_id, 'user_name': username, 'user_rol': user_rol}, secret_key, algorithm='HS256')
            return token

        else:
            print(f"Autenticacion fallida para el usuario {username}")
            return None
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    finally:
        cursor.close()
        



    