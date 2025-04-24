# tests/conftest.py
import pytest
import mysql.connector
from app import create_app
from app.models.core import db as _db
from config import config

@pytest.fixture(scope='session')
def app():
    """Crear aplicación Flask configurada para pruebas"""
    app = create_app('testing')
    
    # Configuración para pruebas
    app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
    })
    
    # Crear contexto de aplicación
    with app.app_context():
        yield app

@pytest.fixture(scope='session')
def setup_test_db(app):
    """Configurar la base de datos de prueba"""
    # Conectar a MySQL para preparar la base de datos de prueba
    conn = mysql.connector.connect(
        host=app.config['DB_HOST'],
        user=app.config['DB_USER'],
        password=app.config['DB_PASSWORD']
    )
    cursor = conn.cursor()
    
    # Crear base de datos si no existe
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {app.config['DB_NAME']}")
    conn.commit()
    
    # Cerrar conexión inicial
    cursor.close()
    conn.close()
    
    # Conectar a la base de datos de prueba
    conn = mysql.connector.connect(
        host=app.config['DB_HOST'],
        user=app.config['DB_USER'],
        password=app.config['DB_PASSWORD'],
        database=app.config['DB_NAME']
    )
    cursor = conn.cursor()
    
    # # Importar el esquema de la base de datos
    # with open('app/db/sistema_incidencias.sql', 'r') as f:
    #     sql_script = f.read()
    #     # Dividir por ; y ejecutar cada comando
    #     for command in sql_script.split(';'):
    #         if command.strip():
    #             try:
    #                 cursor.execute(command)
    #             except mysql.connector.Error as e:
    #                 print(f"Error ejecutando SQL: {e}")
    #                 print(f"Comando: {command}")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    # Inicializar la base de datos con SQLAlchemy
    with app.app_context():
        _db.create_all()
        
        # Aquí podrías agregar datos iniciales si es necesario
        
        yield _db
        
        # No eliminar la base de datos al final de las pruebas para poder inspeccionarla
        # Si prefieres limpiarla, descomenta las siguientes líneas:
        # _db.session.remove()
        # _db.drop_all()

@pytest.fixture(scope='function')
def db_session(setup_test_db, app):
    """Proporcionar una sesión de base de datos limpia para cada prueba"""
    connection = setup_test_db.engine.connect()
    transaction = connection.begin()
    
    session = setup_test_db.create_scoped_session(
        options={"bind": connection, "binds": {}}
    )
    setup_test_db.session = session
    
    yield session
    
    # Rollback para dejar la base de datos como estaba
    transaction.rollback()
    connection.close()
    session.remove()

@pytest.fixture
def client(app):
    """Cliente de prueba Flask"""
    with app.test_client() as client:
        yield client