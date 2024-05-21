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
import logging

import os, sys
path2root = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(path2root)

#from precios_mg.precios_mg_helpers import CostoMG, DisponibilidadStock, ItemMG

logging.basicConfig(level=logging.DEBUG)

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



class GbpSkuMlItem(Base):
    """ Clase que representa un registro de la tabla gbp_sku_ml_item, que almacena los skus que contiene cada publi ML
    """

    __tablename__ = "gbp_sku_ml_item"

    ml_item_id = Column(String (20), primary_key=True, index=True)
    sku = Column(String (100))

    def __init__(self, **kwargs):
        
        if kwargs:
            for k, v in kwargs.items():
                setattr(self, k, v)

    
    def __repr__(self):
        return f"id_ml: {self.ml_item_id}, sku: {self.sku}"
    

    def get_data_from_gbp_item(self, gbp_ml_item):
        
        class_table = self.__table__
        attributes = class_table.columns.keys()
        
        for attribute in attributes:
            if attribute in gbp_ml_item.__dict__.keys():
                setattr(self, attribute, getattr(gbp_ml_item, attribute))

        
    def is_on_db(self, session):
        
        sku_on_db = session.query(GbpSkuMlItem).filter(GbpSkuMlItem.ml_item_id == self.ml_item_id).first()
        
        if sku_on_db:
            return True
        return False
    
    def insert_into_db(self, session):
        
        try:
            session.add(self)
            session.commit()
            print(f'Producto {self.sku} insertado correctamente.')
            session.close()
            return True
        
        except IntegrityError as e:
            print(f'Error al insertar el producto {self}: {e}')
            return False            
        
        except Exception as e:
            print(f'Error al insertar el producto {self}: {e}')
            return False


class GbpSeveralTables_DbItem(Base):
    """ Clase que representa un registro de la tabla gbp_several_tables, que almacena data de distintas tablas de GBP:\n
    Lista de precios\n
    Lista de costos\n
    Depósitos\n
    Categorias\n
    Subcategorías\n
    Subcategoria Auxiliar\n
    Marcas\n
    Monedas\n
    Tiendas ML\n
    """

    __tablename__ = "gbp_several_tables"

    db_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    gbp_table = Column(String (50))
    gbp_id = Column(String (20))
    name = Column(String (100))
    extra = Column(String (100))

    def __init__(self, **kwargs):
        
        if kwargs:
            for k, v in kwargs.items():
                setattr(self, k, v)    

    def __repr__(self):
        return f"db_id: {self.db_id}, table: {self.gbp_table}, gbp_id: {self.gbp_id}, name: {self.name}, extra: {self.extra}"
    
    def is_on_db(self, session):
        
        item_on_db = session.query(GbpSeveralTables_DbItem).filter(GbpSeveralTables_DbItem.gbp_id == self.gbp_id, GbpSeveralTables_DbItem.gbp_table == self.gbp_table).first()
        
        if item_on_db:
            logging.debug(f'{self.name} gbp_id {self.gbp_id} in on db already')
            return True
        logging.debug(f'{self.name} gbp_id {self.gbp_id} not in on db')
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