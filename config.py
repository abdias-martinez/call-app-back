DB_CONFIG = [
    {
        "host": "34.66.90.121",
        "port": "3306",
        "user": "cae",
        "password": "123456789",
        "database": "CAE",
    },
    {
        "host": "34.66.90.121",
        "port": "3306",
        "user": "cae",
        "password": "123456789",
        "database": "POSTES",
    },
]

DB_INFO = {
    "CAE": {
        "users": {"name": "Usuarios", "accessed_by": ["administrador"]},
        "events": {"name": "Eventos", "accessed_by": ["administrador", "operador"]},
        "notifications": {"name": "Notificaciones", "accessed_by": ["administrador", "operador"]},
        "events_options": {"name": "Opciones_Eventos", "accessed_by": ["administrador", "operador"]},
        "post_register": {"name": "Registro_Poste", "accessed_by": ["administrador", "operador"]},
        "post_actual_report": {"name": "Reporte_actual_postes", "accessed_by": ["administrador", "operador"]},
        "calls_report": {"name": "Reporte_llamadas", "accessed_by": ["administrador", "operador"]},
        "posts_report": {"name": "Reporte_postes", "accessed_by": ["administrador", "operador"]},
    }
}

USER_ROLES = {"operador": {"admin": False}, "administrador": {"admin": True}}

SECRET_KEY_CONFIG = {
    "token_secret_key": ".`l]CAeA=ej|Q&Z:D{*CB}+,<;u8=d_$YUdaRYGe?Ld^_;?Pi1|q}a~>YN+bT^3"
}
