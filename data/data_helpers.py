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

def create_tables(engine: Engine, checkfirst_=True) -> bool:
    # Crea las tablas definidas en Base
    try:
        Base.metadata.create_all(engine, checkfirst=checkfirst_)
        print(f'Se crearon las tablas definidas')
        return True
    except Exception as e:
        print(f'Error al crear las tablas: {e}')
        return False
    
# Base = declarative_base()
class Base(DeclarativeBase):

    def get_data_from_gbp_item(self, gbp_item):
        
        class_table = self.__table__
        attributes = class_table.columns.keys()
        
        for attribute in attributes:
            if attribute in gbp_item.__dict__.keys():
                setattr(self, attribute, getattr(gbp_item, attribute))


    def insert_into_db(self, session):
        
        try:
            session.add(self)
            session.commit()
            print(f'Item {self.name} insertado correctamente.')
            session.close()
            return True
        
        except IntegrityError as e:
            print(f'Error al insertar el producto {self}: {e}')
            return False            
        
        except Exception as e:
            print(f'Error al insertar el producto {self}: {e}')
            return False


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