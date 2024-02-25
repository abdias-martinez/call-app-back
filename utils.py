import mysql.connector
import json
import jwt
from config import TB_NAMES

def json_to_dict(json_string: str) -> dict:
    try:
        dictionary = json.loads(json_string)
        return dictionary

    except json.JSONDecodeError as e:
        print(f"Error al decodificar JSON: {e}")
        return {}

def insert_records_table(data_dict: dict, connection: mysql.connector.connection.MySQLConnection, table_name: str) -> None:
    try:
        cursor = connection.cursor()

        columns = ', '.join(data_dict.keys())
        placeholders = ', '.join(['%s'] * len(data_dict))
        sql_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        values = tuple(data_dict.values())

        cursor.execute(sql_query, values)

        connection.commit()

        print(f"Datos registrados exitosamente en la tabla {table_name}!")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        cursor.close()
        
def get_records_table(connection: mysql.connector.connection.MySQLConnection, sources:str, table_name: str) -> str:
    try:
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute(f"SHOW COLUMNS FROM {table_name}")
        columns = [column['Field'] for column in cursor.fetchall()]
        #print(f"columns: {columns}")
        
        #print(f"result: {TB_NAMES[sources]['public']}")
        
        if TB_NAMES[sources]['public']:
            columns_except_id = [column for column in columns if column.lower() != 'id']
            columns_str = ', '.join(columns_except_id) 
        else:
            columns_str = ', '.join(columns) 
            
        #print(f"columns_str: {columns_str}")

        sql_query = f"SELECT {columns_str} FROM {table_name}"
        #print(f"sql_selector: {sql_query}")
        cursor.execute(sql_query)

        records = cursor.fetchall()
        #print(f"records: {records}")

        json_result = json.dumps(records, indent=2)

        return json_result

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return "{}"

    finally:
        cursor.close()
        
def update_record_table_by_id(id: int, data_dict: dict, connection: mysql.connector.connection.MySQLConnection, table_name: str) -> None:
    try:
        cursor = connection.cursor()

        set_clause = ', '.join([f"{key} = %s" for key in data_dict.keys()])
        
        values = tuple(data_dict.values())

        sql_query = f"UPDATE {table_name} SET {set_clause} WHERE id = %s"
        values += (id,)

        cursor.execute(sql_query, values)

        connection.commit()

        print(f"Usuario con ID {id} actualizado exitosamente en la tabla {table_name}!")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        cursor.close()
        
def delete_record_table_by_id(id: int, connection: mysql.connector.connection.MySQLConnection, table_name: str) -> None:
    try:
        cursor = connection.cursor()
        
        sql_query = f"DELETE FROM {table_name} WHERE id = %s"

        cursor.execute(sql_query, (id,))

        connection.commit()

        print(f"Record con ID {id} eliminado exitosamente en la tabla {table_name}!")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

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


    