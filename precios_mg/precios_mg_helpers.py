from bs4 import BeautifulSoup
from dataclasses import dataclass, field
from dotenv import load_dotenv
from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, Time, Boolean, UniqueConstraint, create_engine, Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func
from datetime import datetime, time
from typing import Tuple, Dict, List, Union
import requests

import os, sys
path2root = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(path2root)

from data.data_helpers import Base, create_tables, db_connection

#   Loads env db constants
from precios_mg_config import MYSQL_USER, MYSQL_PASS, MYSQL_HOST, MYSQL_PORT, DB, \
    LOCAL_MYSQL_USER, LOCAL_MYSQL_PASS, LOCAL_MYSQL_HOST, LOCAL_MYSQL_PORT, LOCAL_DB


class CostoMG(Base):
    """Objeto que representa un item de la tabla costos_mg de la base de datos inea
    """

    __tablename__ = "costos_mg"

    costo_id = Column(Integer, primary_key=True, autoincrement=True)
    costo_date = Column(DateTime, default=func.now(), nullable=False)
    sku = Column(String (100), nullable=False)
    costo = Column(DECIMAL(precision=12, scale=2))
    

    def __init__(self, costo_date, sku, costo):
        self.costo_date = costo_date
        self.sku = sku
        self.costo = costo

    def __repr__(self) -> str:
        return f'{self.costo_date} {self.sku} {self.costo}'
    
    def __str__(self):
        return f'{self.costo_date} {self.sku} {self.costo}'

@dataclass
class ProductoMG:
    """Objeto para representar un item traído del catálogo de Microglobal
    """
    timestamp: datetime = field(repr=True, default=None)    
    sku: str = field(repr=True, default=None)
    nombre: str = field(repr=True, default=None)
    marca: str = field(repr=True, default=None)
    categoria: str = field(repr=True, default=None)
    cod_cat: str = field(repr=True, default=None)
    costo: float = field(repr=True, default=None)
    stock: int = field(repr=True, default=None)
    iva: float = field(repr=True, default=None)
    ean: str = field(repr=True, default=None)


def productomg2costomg(producto: ProductoMG) -> CostoMG:
    """Crea un objeto CostoMG a partir de un objeto ProductoMG
    """
    return CostoMG(producto.timestamp, producto.sku, producto.costo)

def latest_price_mg(session: Session, sku: str) -> CostoMG:
    """Trae el último precio de un producto de Microglobal
    """
    return session.query(CostoMG)\
        .filter(CostoMG.sku == sku)\
            .order_by(CostoMG.costo_date.desc())\
                .first()

def insert_costo_mg(session: Session, costo: CostoMG) -> bool:
    """Inserta un precio en la base de datos
    """
    try:
        session.add(costo)
        session.commit()
        print(f'Se insertó el costo {costo}')
        return True
    except IntegrityError as e:
        print(f'Error al insertar el costo {costo}: {e}')
        return False

def mg_cat_xml() -> Union[str, bool]:
    """Trae el xml con el catálogo de Microglobal
    """
    # Carga variables de entorno
    load_dotenv()

    MG_CLIENTE = os.getenv("MG_CLIENTE")
    MG_USUARIO = os.getenv("MG_USUARIO")
    MG_PASSWORD = os.getenv("MG_PASSWORD")

    url = "https://ecommerce.microglobal.com.ar/WSMG/WSMG.asmx"

    payload = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<soap:Envelope xmlns:soap=\"http://schemas.xmlsoap.org/soap/envelope/\">\n  <soap:Body>\n    <GetCatalog xmlns=\"http://tempuri.org/\">\n      <cliente>906992</cliente>\n      <usuario>juan</usuario>\n      <password>Jose1974</password>\n    </GetCatalog>\n  </soap:Body>\n</soap:Envelope>\n"
    headers = {
      'Content-Type': 'text/xml; charset=utf-8',
      'SOAPAction': 'http://tempuri.org/GetCatalog',
      'cliente': MG_CLIENTE,
      'usuario': MG_USUARIO,
      'password': MG_PASSWORD
    }
    try:
        # Conecta a Microglobal y trae el catálogo de productos
        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code != 200:
            print(response.status_code, response.text)
            return False
        else:
            return response.text
    except requests.exceptions.SSLError as e:
        print(f'SSL Error (Certificado SSL expirado?) conectando a {url}\n{e}')
        #   notificar por telegram
        mensaje = f'🔴   Problemas para conectar con MICROGLOBAL.\n\nSSL Error (Certificado SSL expirado?)\n\n{type(e)}'
        #mandar_mensaje_telegram("iojan", chat_telegram("ineabots"), mensaje)
        return False

    except requests.exceptions.RequestException as e:
        print(f'Error conectando a {url}\n{e}')
        mensaje = f'🔴   Problemas para conectar con MICROGLOBAL.\n\nRequest Error\n\n{type(e)}'
        #mandar_mensaje_telegram("iojan", chat_telegram("ineabots"), mensaje)
        #return handle_exception_and_notify(e, mensaje)
        return False
    except Exception as e:
        print(f'{type(e)} Error inesperado\n{e}')
        mensaje = f'🔴   Error inesperado\n\n{type(e)}'
        #mandar_mensaje_telegram("iojan", chat_telegram("ineabots"), mensaje)
        return False    


def parse_mgcat(xml_response: str, **kwargs: Dict[str, Union[bool, int, float]]) -> List[ProductoMG]:
    """
    Parsea el catálogo de producto de Microglobal.

    Argumentos:
        xml_response (str): xml con el catálogo de productos de Microglobal.
        **kwargs (dict): filtra argumentos de salida.
            timestamp (bool): incluye fecha y hora de la actualización. Default=False.
            sku (bool): incluye SKU. Default=True.
            nombre (bool): incluye nombre. Default=True.
            marca (bool): incluye marca. Default=True.
            categoria (bool): incluye categoría. Default=True.
            cod_cat (bool): incluye código de categoría. Default=True.
            costo (bool): incluye costo. Default=True.
            stock (bool): incluye stock. Default=True.
            iva (bool): incluye iva. Default=True.
            ean (bool): incluye EAN. Default=True.
    
    Devolución:
        List[ProductoMG]
    """
    # define default arguments
    timestamp = kwargs.get("timestamp", False)
    sku = kwargs.get("sku", True)
    nombre = kwargs.get("nombre", True)
    marca = kwargs.get("marca", True)
    categoria = kwargs.get("categoria", True)
    cod_cat = kwargs.get("cod_cat", True)
    costo = kwargs.get("costo", True)
    stock = kwargs.get("stock", True)
    iva = kwargs.get("iva", True)
    ean = kwargs.get("ean", True)

    # parsea response del xml en un objeto soup y crea una lista para cada campo

    soup = BeautifulSoup(xml_response, 'xml')

    skus = soup.find_all("partNumber")
    nombres = soup.find_all("descripcion")
    marcas = soup.find_all("codMarca")
    categorias = soup.find_all("categoria")
    cod_cats = soup.find_all("codCategoria")
    costos = soup.find_all("precio")
    stocks = soup.find_all("stock")
    ivas = soup.find_all("iva_pct")
    upcs = soup.find_all("upc")

    # crea lista con el catálogo de todos los productos MG a partir del objeto soup
    cat_mg = []
    timestamp = datetime.now()
    
    for i in range(0, len(skus)):
                
        item_args = {
            "timestamp": timestamp,
            "sku": skus[i].text, 
            "nombre": nombres[i].text, 
            "marca": marcas[i].text, 
            "categoria": categorias[i].text, 
            "cod_cat": cod_cats[i].text, 
            "costo": float(costos[i].text), 
            "stock": int(stocks[i].text), 
            "iva": float(ivas[i].text), 
            "ean": str(upcs[i].text)
        }

        # Filtra argumentos (en **kawrgs) con valor verdadero
        filtered_args = {key: value for key, value in item_args.items() if kwargs.get(key, False)}

        item = ProductoMG(**filtered_args)
        cat_mg.append(item)

    return cat_mg

def mg_get_prices():
    """
    Trae lista con precios del catálogo de productos de Microglobal.

    Argumentos:
        No requiere    
    Devolución:
        List[PrecioMG]
    """
    xml = mg_cat_xml()
    prices = parse_mgcat(xml, timestamp=True, sku=True, costo=True, nombre=False, marca=False, \
                                           categoria=False, cod_cat=False, stock=False, \
                                            iva=False, ean=False)
    return prices




if __name__ == "__main__":



    #   Connect to db and start a session
    ce = db_connection(MYSQL_USER, MYSQL_PASS, MYSQL_HOST, MYSQL_PORT, DB)
    connection = ce[0]
    engine = ce[1]

    #   Create database session
    Session = sessionmaker(bind=engine)
    session = Session()    

    db_connection
    #create_tables(engine)

    pass
