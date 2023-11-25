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
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
path2root = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(path2root)

from data.data_helpers import Base, create_tables, db_connection

#   Loads env db constants
from precios_mg_config import PRODUCCION_MYSQL_USER, PRODUCCION_MYSQL_PASS, PRODUCCION_MYSQL_HOST, PRODUCCION_MYSQL_PORT, PRODUCCION_DB, \
    TEST_MYSQL_USER, TEST_MYSQL_PASS, TEST_MYSQL_HOST, TEST_MYSQL_PORT, TEST_DB


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
        return f'{self.costo_id} {self.costo_date} {self.sku} {self.costo}'
    
    def __str__(self):
        return f'{self.costo_date} {self.sku} {self.costo}'

class ItemMG(Base):
    """Objeto que representa un item de la tabla productos_mg de la base de datos inea
    """

    __tablename__ = "productos_mg"

    item_id = Column(Integer, primary_key=True, autoincrement=True)
    item_date = Column(DateTime, default=func.now(), nullable=False)
    sku = Column(String (100), nullable=False)
    nombre = Column(String (250))
    marca = Column(String (100))
    categoria = Column(String (100))
    cod_cat = Column(String (100))
    iva = Column(DECIMAL(precision=12, scale=2))
    ean = Column(String (100))

    def __init__(self, item_date, sku, nombre, marca, categoria, cod_cat, iva, ean):
        self.item_date = item_date
        self.sku = sku
        self.nombre = nombre
        self.marca = marca
        self.categoria = categoria
        self.cod_cat = cod_cat
        self.iva = iva
        self.ean = ean

    def __repr__(self) -> str:
        return f'{self.sku} {self.iva} {self.marca} {self.nombre}'
    
    def __str__(self) -> str:
        return f'{self.sku} {self.marca} {self.nombre}'

class DisponibilidadStock(Base):

    __tablename__ = "disponibilidad_stock_mg"

    disponibilidad_id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=func.now(), nullable=False)
    sku = Column(String (100), nullable=False)
    disponible = Column(Integer)

    def __init__(self, timestamp, sku, disponible):
        self.timestamp = timestamp
        self.sku = sku
        self.disponible = disponible

    def __repr__(self) -> str:
        return f'{self.sku} {self.stock}'
    
    def __str__(self) -> str:
        return f'{self.sku} {self.stock}'

#class FacturasMG(Base):
#    pass

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

def productomg2itemmg(producto: ProductoMG) -> ItemMG:
    """Crea un objto ItemMG a partir de un objto ProductoMG
    """
    return ItemMG(producto.timestamp, producto.sku, producto.nombre, producto.marca, producto.categoria, producto.cod_cat, producto.iva, producto.ean)


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


def parse_mgcat(xml_response: str, **kwargs: Dict[str, bool]) -> List[ProductoMG]:
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

    for i in range(0, len(skus)):
                
        item_args = {
            "timestamp": datetime.now() if kwargs.get("timestamp", False) else False,
            "sku": skus[i].text if kwargs.get("sku", False) else False,
            "nombre": nombres[i].text if kwargs.get("nombre", False) else False,
            "marca": marcas[i].text if kwargs.get("marca", False) else False,
            "categoria": categorias[i].text if kwargs.get("categoria", False) else False,
            "cod_cat": cod_cats[i].text if kwargs.get("cod_cat", False) else False,
            "costo": float(costos[i].text) if kwargs.get("costo", False) else False,
            "stock": int(stocks[i].text) if kwargs.get("stock", False) else False,
            "iva": float(ivas[i].text) if kwargs.get("iva", False) else False,
            "ean": str(upcs[i].text) if kwargs.get("ean", False) else False
        }

        item = ProductoMG(**item_args)
        cat_mg.append(item)

    return cat_mg

def mg_get_products(mg_cat_xml, format=None) -> List[ProductoMG]:
    """
    Trae lista con productos del catálogo de productos de Microglobal.

    Argumentos:
        format (str): Si es "prices" devuelve ProductoMG con atributos necesarios para CostoMG
        Si es "stock" devuelve ProductoMG con atributos necesarios para StockMG
        Si es None devuelve ProductoMG con atributos necesarios para ItemMG
    Devolución:
        List[ProductoMG]
    """
    
    if format == "prices":
        attrs = ("timestamp", "sku", "costo")
    elif format == "stock":
        attrs = ("timestamp", "sku", "stock")
    else:
        attrs = ("timestamp", "sku", "nombre", "marca", "categoria", \
                 "cod_cat", "costo", "stock", "iva", "ean")

    xml = mg_cat_xml
    kwargs = {attr: True for attr in attrs}
    products = parse_mgcat(xml, **kwargs)

    return products


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
