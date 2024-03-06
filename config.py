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
    },
    "POSTES": {
        "states_reports_posts": {"name": "POSTES_REPORTES_ESTADO", "accessed_by": ["administrador", "operador"]},
        "sms_posts": {"name": "POSTES_SMS", "accessed_by": []},
        "event_sabre": {"name": "SABRE_EVENTO", "accessed_by": []}
    },
}

USER_ROLES = {"operador": {"admin": False}, "administrador": {"admin": True}}

SECRET_KEY_CONFIG = {
    "token_secret_key": ".`l]CAeA=ej|Q&Z:D{*CB}+,<;u8=d_$YUdaRYGe?Ld^_;?Pi1|q}a~>YN+bT^3"
}
