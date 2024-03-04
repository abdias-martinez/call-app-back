DB_CONFIG = {
    'host': '34.66.90.121',
    'port': '3306',
    'user': 'cae',
    'password': '123456789',
    'database': 'CAE'
}

TB_NAMES = {
    'users': {
        'name': 'Usuarios',
        'public': False
    },
    'events': {
        'name': 'Eventos',
        'public': False
    },
}

USER_ROLES = {
    'operador': {
        'admin': False
    },
    'administrador': {
        'admin': True
    }
}

SECRET_KEY_CONFIG = {
    'jwt_secret_key': '.`l]CAeA=ej|Q&Z:D{*CB}+,<;u8=d_$YUdaRYGe?Ld^_;?Pi1|q}a~>YN+bT^3'
}