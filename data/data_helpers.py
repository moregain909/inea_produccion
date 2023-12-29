from bs4 import BeautifulSoup
from dataclasses import dataclass, field
from dotenv import load_dotenv
from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, Time, Boolean, UniqueConstraint, create_engine, Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func
from datetime import datetime, time
from typing import Tuple
import requests

import os, sys
path2root = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(path2root)

#from precios_mg.precios_mg_helpers import CostoMG, DisponibilidadStock, ItemMG


load_dotenv()

# Database producción server INEA
PRODUCCION_MYSQL_USER = os.getenv('INEA_DB_MYSQL_USER')
PRODUCCION_MYSQL_PASS = os.getenv('INEA_DB_MYSQL_PASS')
PRODUCCION_MYSQL_HOST = os.getenv('INEA_DB_MYSQL_HOST')
PRODUCCION_MYSQL_PORT = os.getenv('INEA_DB_MYSQL_PORT')
PRODUCCION_DB = os.getenv('INEA_DB_DATABASE')

# Database de prueba local@local
TEST_MYSQL_USER = os.getenv('INEA_TEST_DB_MYSQL_USER')
TEST_MYSQL_PASS = os.getenv('INEA_TEST_DB_MYSQL_PASS')
TEST_MYSQL_HOST = os.getenv('INEA_TEST_DB_MYSQL_HOST')
TEST_MYSQL_PORT = os.getenv('INEA_TEST_DB_MYSQL_PORT')
TEST_DB = os.getenv('INEA_TEST_DB_DATABASE')


def db_connection(user: str, password: str, host: str, port: str, database: str, driver: str ="mysql+pymysql") -> Tuple:
    connection_string = f"{driver}://{user}:{password}@{host}:{port}/{database}"
    engine = create_engine(connection_string)
    connection = engine.connect()
    print(f'Database {database} on {host} connected')
    return (connection, engine)

def create_tables(engine: Engine) -> bool:
    # Crea las tablas definidas en Base
    try:
        Base.metadata.create_all(engine)
        print(f'Se crearon las tablas definidas')
        return True
    except Exception as e:
        print(f'Error al crear las tablas: {e}')
        return False
    
# Base = declarative_base()
class Base(DeclarativeBase):
    pass

class Database:
    """ Clase que permite crear y manejar una conection y un engine de una database"""

    def __init__(self, db_location):
        self.db_location = db_location
        
        #   Connect to db and start a session
        if self.db_location == "local" or self.db_location == "desarrollo":
            #   local test database
            ce = db_connection(TEST_MYSQL_USER, TEST_MYSQL_PASS, TEST_MYSQL_HOST, TEST_MYSQL_PORT, TEST_DB)
        else:
            #   remote production database
            ce = db_connection(PRODUCCION_MYSQL_USER, PRODUCCION_MYSQL_PASS, PRODUCCION_MYSQL_HOST, PRODUCCION_MYSQL_PORT, PRODUCCION_DB)
    
        self.connection = ce[0]
        self.engine = ce[1]




if __name__ == "__main__":


    pass