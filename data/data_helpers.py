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

#from precios_mg.precios_mg_helpers import ProductoMG


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


    
if __name__ == "__main__":


    pass