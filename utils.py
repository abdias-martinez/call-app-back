import mysql.connector
import json
import jwt
from datetime import datetime
from config import DB_INFO

# función para formatear la fecha y hora
def format_datetime(value):
    if isinstance(value, datetime):
        return value.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return value
    
# función para verificar si un registro único ya existe   
def check_existing_record(cursor: mysql.connector.cursor.MySQLCursor, table_name: str, field: str, value: str) -> bool:
    query = f"SELECT COUNT(*) FROM {table_name} WHERE {field} = %s"
    cursor.execute(query, (value,))
    return cursor.fetchone()[0] > 0


# función para insertar registros en una tabla
def insert_records_table(token: str, data_dict: dict, connection: mysql.connector.connection.MySQLConnection, view: str, secret_key: str) -> dict:
    decoded_token = jwt.decode(token, secret_key, algorithms='HS256')
    user_rol = decoded_token["user_rol"]

    if view in DB_INFO['CAE'].keys():
        table_name = DB_INFO['CAE'][view]['name']

        # verificamos los permisos del usuario para acceder a la vista
        if user_rol in DB_INFO['CAE'][view]['accessed_by']:
            try:
                cursor = connection.cursor()

                # verificamos si el registro único ya existe en la tabla 'Usuarios'
                if table_name == 'Usuarios' and check_existing_record(cursor, table_name, 'Usuario', data_dict['Usuario']):
                    return {'type': 'error', 'message': 'Usuario ya existe'}

                # verificamos si el registro único ya existe en la tabla 'Registro_Poste'
                if table_name == 'Registro_Poste' and check_existing_record(cursor, table_name, 'num_poste', data_dict['num_poste']):
                    return {'type': 'error', 'message': 'Poste ya existe'}
                
                # verificamos si el registro único ya existe en la tabla 'Tipos_Evento'
                if table_name == 'Tipos_Evento' and check_existing_record(cursor, table_name, 'evento', data_dict['evento']):
                    return {'type': 'error', 'message': 'Evento ya existe'}
                
                # verificamos si el registro único ya existe en la tabla 'Tipos_Derivado'
                if table_name == 'Tipos_Derivado' and check_existing_record(cursor, table_name, 'derivado', data_dict['derivado']):
                    return {'type': 'error', 'message': 'Derivado ya existe'}
                
                # verificamos si el registro único ya existe en la tabla 'Tipos_Vehiculo'
                if table_name == 'Tipos_Vehiculo' and check_existing_record(cursor, table_name, 'vehiculo', data_dict['vehiculo']):
                    return {'type': 'error', 'message': 'Vehículo ya existe'}

                columns = ', '.join(data_dict.keys())
                placeholders = ', '.join(['%s'] * len(data_dict))
                sql_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                values = tuple(data_dict.values())

                cursor.execute(sql_query, values)
                connection.commit()

                return {'type': 'success', 'message': 'Registro insertado'}

            except mysql.connector.Error as err:
                return {'type': 'error', 'message': 'Error en la inserción'}

            finally:
                cursor.close()
        else: 
            return {"type": "error", "message": "No cuenta con permisos para realizar esta acción"}
    else:
        return {"type": "error", "message": "Vista de origen no existe"}

# función para obtener registros de una tabla
def get_records_table(token: str, connection: mysql.connector.connection.MySQLConnection, view: str, secret_key: str) -> str:
    decoded_token = jwt.decode(token, secret_key, algorithms='HS256')
    user_rol = decoded_token["user_rol"]

    if view in DB_INFO['CAE'].keys():
        table_name = DB_INFO['CAE'][view]['name']

        # verificamos los permisos del usuario para acceder a la vista
        if user_rol in DB_INFO['CAE'][view]['accessed_by']:
            try:
                cursor = connection.cursor(dictionary=True)

                # Obtenemos los nombres de las columnas de la tabla
                cursor.execute(f"SHOW COLUMNS FROM {table_name}")
                columns = [column['Field'] for column in cursor.fetchall()]
                columns_except_id = [column for column in columns if column.lower() != 'id']
                columns_str = ', '.join(columns_except_id)

                # ejecutamos la consulta SQL para obtener registros
                sql_query = f"SELECT {columns_str} FROM {table_name}"
                cursor.execute(sql_query)
                records = cursor.fetchall()

                # formateamos los registros antes de convertirlos a JSON
                formatted_records = [{key: format_datetime(value) for key, value in record.items()} for record in records]
                json_result = json.dumps(formatted_records, indent=2)

                return json_result

            except mysql.connector.Error as err:
                print(f"Error: {err}")
                return "{}"

            finally:
                cursor.close()
        else:
            return {"type": "error", "message": "No cuenta con permisos para realizar esta acción"}
    else:
        return {"type": "error", "message": "Vista de origen no existe"}

# función para obtener registros de todas las tablas
def get_all_tables_records(token: str, connection_1: mysql.connector.connection.MySQLConnection, secret_key: str) -> str:
    decoded_token = jwt.decode(token, secret_key, algorithms='HS256')
    user_rol = decoded_token["user_rol"]
    all_tables_data = {}
    
    # Conexión 1
    cursor_1 = connection_1.cursor(dictionary=True)
    cursor_1.execute("SHOW TABLES")
    db_name_1 = 'CAE'
    tables_1 = [table['Tables_in_' + db_name_1] for table in cursor_1.fetchall()]
    
    # eliminamos las tablas para las que el usuario no tiene permisos
    for tb in DB_INFO[db_name_1].values():
        if user_rol not in tb['accessed_by']:
            tables_1.remove(tb['name'])
            
    db_data_1 = {}
    
    for table_name in tables_1:
        cursor_1.execute(f"SHOW COLUMNS FROM {table_name}")
        columns_info = cursor_1.fetchall()
        columns = [column['Field'] for column in columns_info]
        columns_except_id = [column for column in columns if column.lower() != 'id']
        columns_str = ', '.join(columns_except_id)
        sql_query = f"SELECT {columns_str} FROM {table_name}"
        cursor_1.execute(sql_query)
        records = cursor_1.fetchall()
        # formateamos los registros antes de agregarlos al resultado final
        formatted_records = [{key: format_datetime(value) for key, value in record.items()} for record in records]
        table_data = {
            "table_name": table_name,
            "records": formatted_records
        }
        db_data_1[table_name] = table_data
        
    all_tables_data[db_name_1] = db_data_1
    
    
    json_result = json.dumps(all_tables_data, default=str, indent=2)
    
    return json_result

    cursor_1.close()

# función para actualizar un registro en una tabla por identificador
def update_record_table_by_id(token: str, new_data_dict: dict, original_data_dict: dict, connection: mysql.connector.connection.MySQLConnection, identifier: str, view: str, secret_key: str) -> dict:
    decoded_token = jwt.decode(token, secret_key, algorithms='HS256')
    user_rol = decoded_token["user_rol"]

    if view in DB_INFO['CAE'].keys():
        table_name = DB_INFO['CAE'][view]['name']

        # verificamos los permisos del usuario para acceder a la vista
        if user_rol in DB_INFO['CAE'][view]["accessed_by"]:
            try:
                cursor = connection.cursor()

                # construimos la cláusula SET para la actualización
                set_clause = ', '.join([f"{key} = %s" for key in new_data_dict.keys()])
                where_condition = f"{identifier} = %s"

                # construimos y ejecutamos la consulta SQL
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
        else:
            return {"type": "error", "message": "No cuenta con permisos para realizar esta acción"}
    else:
        return {"type": "error", "message": "Vista de origen no existe"}

# función para mos las un registro de una tabla por identificador
def delete_record_table_by_id(token: str, id: str, connection: mysql.connector.connection.MySQLConnection, identifier: str, view: str, secret_key: str) -> dict:
    decoded_token = jwt.decode(token, secret_key, algorithms='HS256')
    user_rol = decoded_token["user_rol"]

    if view in DB_INFO['CAE'].keys():
        table_name = DB_INFO['CAE'][view]['name']

        # verificamos los permisos del usuario para acceder a la vista
        if user_rol in DB_INFO['CAE'][view]["accessed_by"]:
            try:
                cursor = connection.cursor()

                where_condition = f"{identifier} = %s"

                # construimos y ejecutamos la consulta SQL
                sql_query = f"DELETE FROM {table_name} WHERE {where_condition}"
                values = tuple([id])

                cursor.execute(sql_query, values)
                connection.commit()

                return {'type': 'success', 'message': 'Registro eliminado'}

            except mysql.connector.Error as err:
                print(f"Error: {err}")
                return {'type': 'error', 'message': 'Error en la eliminación'}

            finally:
                cursor.close()
        else:
            return {"type": "error", "message": "No cuenta con permisos para realizar esta acción"}
    else:
        return {"type": "error", "message": "Vista de origen no existe"}

# función para verificamos si un usuario está autenticado
def user_is_authenticated(token: str, connection: mysql.connector.connection.MySQLConnection, secret_key: str) -> bool:
    decoded_token = jwt.decode(token, secret_key, algorithms='HS256')
    user_name = decoded_token["user_name"]
    user_id = decoded_token["user_id"]
    user_rol = decoded_token["user_rol"]

    try:
        cursor = connection.cursor(dictionary=True) 
        sql_query = "SELECT Id, Perfil FROM Usuarios WHERE Usuario = %s"
        cursor.execute(sql_query, (user_name,))

        record = cursor.fetchone()

        # verificamos si el usuario existe en la base de datos y si los datos coinciden
        if record and user_id == record['Id'] and user_rol == record['Perfil']:
            return True

        return False

    except Exception:
        return False

# función para autenticar a un usuario
def auth_user(user_name: str, connection: mysql.connector.connection.MySQLConnection, password: str, secret_key: str) -> str:
    try:
        cursor = connection.cursor(dictionary=True)
        sql_query = "SELECT Usuario, Contraseña, Id, Perfil FROM Usuarios WHERE Usuario = %s"
        cursor.execute(sql_query, (user_name,))

        record = cursor.fetchone()

        # verificamos si el usuario existe y si la contraseña coincide
        if record and record['Contraseña'] == password:
            user_id = record['Id']
            user_rol = record['Perfil']
            print(f"Usaurio {user_name} autenticado exitosamente!")

            # generamos un token de autenticación
            token = jwt.encode({'user_id': user_id, 'user_name': user_name, 'user_rol': user_rol}, secret_key, algorithm='HS256')
            return token

        else:
            print(f"Autenticacion fallida para el usuario {user_name}")
            return None

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

    finally:
        cursor.close()