from bs4 import BeautifulSoup
from bs4.element import Tag
import httpx
from dataclasses import dataclass, field
from decimal import Decimal
from dotenv import load_dotenv
import json
from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, Time, Boolean, UniqueConstraint, \
    Engine, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func
from datetime import datetime, time
from typing import Tuple, Dict, List, Union
import requests

import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
path2root = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(path2root)
data_dir = os.path.join(path2root, "data")
sys.path.append(data_dir)

from data.data_helpers import Base, create_tables, db_connection

#   Loads env db constants
from precios_mg_config import PRODUCCION_MYSQL_USER, PRODUCCION_MYSQL_PASS, PRODUCCION_MYSQL_HOST, PRODUCCION_MYSQL_PORT, PRODUCCION_DB, \
    TEST_MYSQL_USER, TEST_MYSQL_PASS, TEST_MYSQL_HOST, TEST_MYSQL_PORT, TEST_DB
from sqlalchemy.orm import relationship


#   Tablas con info de MG para database inea

class ItemMG(Base):
    """Objeto que representa un item de la tabla productos_mg de la base de datos inea
    """

    __tablename__ = "productos_mg"

    #item_id = Column(Integer, primary_key=True, autoincrement=True)
    #sku = Column(String (100), index=True, unique=True, nullable=False)
    sku = Column(String (100), primary_key=True, index=True)
    item_date = Column(DateTime, default=func.now(), nullable=False)
    nombre = Column(String (250))
    marca = Column(String (100))
    categoria = Column(String (100))
    cod_cat = Column(String (100))
    iva = Column(DECIMAL(precision=12, scale=3))
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

    # Define the one-to-many relationship
    costos = relationship("CostoMG", back_populates="itemmg")

    disponibilidad_stock = relationship("DisponibilidadStock", back_populates="itemmg")

    def __repr__(self) -> str:
        return f'{self.sku} {self.iva} {self.marca} {self.nombre}'
    
    def __str__(self) -> str:
        return f'{self.sku} {self.marca} {self.nombre}'
    

class CostoMG(Base):
    """Objeto que representa un item de la tabla costos_mg de la base de datos inea
    """

    __tablename__ = "costos_mg"

    costo_id = Column(Integer, primary_key=True, autoincrement=True)
    costo_date = Column(DateTime, default=func.now(), nullable=False)
    sku = Column(String (100), ForeignKey("productos_mg.sku"), nullable=False)
    costo = Column(DECIMAL(precision=12, scale=2))

    # Establish the back-reference from CostoMG to ItemMG
    itemmg = relationship("ItemMG", back_populates="costos")    

    def __init__(self, costo_date, sku, costo):
        self.costo_date = costo_date
        self.sku = sku
        self.costo = costo

    def __repr__(self) -> str:
        return f'{self.costo_id} {self.costo_date} {self.sku} {self.costo}'
    
    def __str__(self):
        return f'{self.costo_date} {self.sku} {self.costo}'



class DisponibilidadStock(Base):

    __tablename__ = "disponibilidad_stock_mg"

    disponibilidad_id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=func.now(), nullable=False)
    sku = Column(String (100), ForeignKey("productos_mg.sku", name="fk_disponibilidad_stock_sku"), nullable=False)
    stock_disponible = Column(Integer)

    itemmg = relationship("ItemMG", back_populates="disponibilidad_stock")

    def __init__(self, timestamp: datetime, sku: str, stock_disponible: int):

        # Valida presencia de valores de entrada:
        if None in [timestamp, sku, stock_disponible]:
            raise ValueError("timestamp, sku y stock_disponible son requeridos")

        # Valida tipos de valores de entrada:
        #   timestamp: datetime
        #   sku: str
        #   stock_disponible: int
        if not isinstance(timestamp, datetime):
            raise TypeError("timestamp tiene que ser datetime")
        if not isinstance(sku, str):
            raise TypeError("sku tiene que ser string")
        if not isinstance(stock_disponible, int):
            raise TypeError("stock_disponible tiene que ser int")  

        self.timestamp = timestamp
        self.sku = sku
        self.stock_disponible = stock_disponible

    def __repr__(self) -> str:
        return f'{self.sku} {self.stock_disponible}'
    
    def is_available(self) -> bool:
        """Confirma si el sku (objeto DisponibilidadStock) tiene stock disponible
        """
        if self.stock_disponible > 0:
            return True
        return False

# TODO: Crear clase FacturasMG para manejar la tabla facturas_mg de la base de datos inea
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

    string_fields = ["sku", "nombre", "marca", "categoria", "cod_cat", "ean"]
    float_fields = ["costo", "iva"]

    def __post_init__(self):

        # Valida tipos de entrada
        if self.timestamp is not None and not isinstance(self.timestamp, datetime):
            raise TypeError(f'timestamp tiene que ser datetime o None y no {type(self.timestamp)}')
        for string_field in self.string_fields:
            if getattr(self, string_field) is not None and not isinstance(getattr(self, string_field), str):
                raise TypeError(f'{string_field} tiene que ser str o None, no {type(getattr(self, string_field))}')
        for float_field in self.float_fields:
            if getattr(self, float_field) is not None and not isinstance(getattr(self, float_field), float):
                raise TypeError(f'{float_field} tiene que ser float o None no {type(getattr(self, float_field))}')


    def is_available(self) -> bool:
        """Confirma si el ProductoMG tiene stock disponible
        """
        if self.stock > 0:
            return True
        return False

#   Funciones relacionadas con la base de datos de MG

def productomg2costomg(producto: ProductoMG) -> CostoMG:
    """Crea un objeto CostoMG a partir de un objeto ProductoMG
    """
    return CostoMG(producto.timestamp, producto.sku, producto.costo)

def productomg2itemmg(producto: ProductoMG) -> ItemMG:
    """Crea un objto ItemMG a partir de un objeto ProductoMG
    """
    return ItemMG(producto.timestamp, producto.sku, producto.nombre, producto.marca, producto.categoria, producto.cod_cat, producto.iva, producto.ean)

def productomg2disponibilidadstock(producto: ProductoMG) -> DisponibilidadStock:
    """Crea un objeto DisponibilidadStock a partir de un objeto ProductoMG
    """
    return DisponibilidadStock(producto.timestamp, producto.sku, producto.stock)

def db_get_disponibilidad_stock(session: Session, sku: str) -> Union[DisponibilidadStock, None]:
    """Trae el último registro de stock disponible de un producto
    """
    return session.query(DisponibilidadStock)\
        .filter(DisponibilidadStock.sku == sku)\
            .order_by(DisponibilidadStock.timestamp.desc())\
                .first()

def latest_price_mg(session: Session, sku: str) -> CostoMG:
    """Trae el último precio de un producto de Microglobal
    """
    return session.query(CostoMG)\
        .filter(CostoMG.sku == sku)\
            .order_by(CostoMG.costo_date.desc())\
                .first()

# TODO: Estas tres funciones insert podrían ser una sola

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

def insert_item_mg(session: Session, item: ItemMG) -> bool:
    """Inserta un producto en la base de datos
    """
    try:
        session.add(item)
        session.commit()
        print(f'Se insertó el producto {item}')
        return True
    except IntegrityError as e:
        print(f'Error al insertar el producto {item}: {e}')
        return False

def insert_disponibilidad_stock(session: Session, disponibilidad_stock: DisponibilidadStock) -> bool:
    """Inserta un registro DisponibilidadStocken la base de datos
    """
    try:
        session.add(disponibilidad_stock)
        session.commit()
        #print(f'Se insertó el registro de stock disponible {disponibilidad_stock}')
        if disponibilidad_stock.stock_disponible > 0:
            print(f'  🟢  {disponibilidad_stock.sku} tiene stock disponible')
        else:
            print(f'  🔴  {disponibilidad_stock.sku} deja de estar disponible')
        return True
    except IntegrityError as e:
        print(f'Error al insertar el registro de stock disponible {disponibilidad_stock}: {e}')
        return False

def update_item_mg(session: Session, item: ItemMG) -> bool:
    """Actualiza un producto en la base de datos
    """
    try:
        session.query(ItemMG)\
            .filter(ItemMG.sku == item.sku)\
                .update({ItemMG.nombre: item.nombre, ItemMG.marca: item.marca, ItemMG.categoria: item.categoria, ItemMG.cod_cat: item.cod_cat, ItemMG.iva: item.iva, ItemMG.ean: item.ean})
        session.commit()
        print(f'Se actualizó el producto {item}')
        return True
    except IntegrityError as e:
        print(f'Integrity Error al actualizar el producto {item}: {e}')
        return False
    except Exception as e:
        print(f'Exeption Error al actualizar el producto {item}: {e}')
    return False

def is_in_table(session: Session, sku: str) -> bool:
    """Comprueba si un producto está en la base de datos
    """
    return session.query(ItemMG).filter(ItemMG.sku == sku).count() > 0


def same_as_in_table(session: Session, mg_product: ProductoMG) -> bool:
    """Comprueba si un producto es el mismo que está en la base de datos
    """
    db_product = session.query(ItemMG).filter(ItemMG.sku == mg_product.sku).first()

    #   Convierto los valores de iva a Decimal para poder compararlos (originalmente sería float vs DECIMAL)
    mg_iva = Decimal(f"{mg_product.iva:.3f}")
    db_iva = Decimal(db_product.iva)

    if db_product.sku == mg_product.sku and db_product.nombre ==  mg_product.nombre and db_product.categoria == mg_product.categoria \
        and db_product.ean == mg_product.ean and db_product.cod_cat == mg_product.cod_cat \
            and db_product.marca == mg_product.marca and db_iva == mg_iva:
        return True
    else:
        return False

#   Funciones relacionadas con el Web Service de MG

def mg_cat_xml() -> Union[str, bool]:
    """Trae el xml con el catálogo de Microglobal
    """
    # Carga variables de entorno
    load_dotenv()

    MG_CLIENTE = os.getenv("MG_CLIENTE")
    MG_USUARIO = os.getenv("MG_USUARIO")
    MG_PASSWORD = os.getenv("MG_PASSWORD")

    url = "https://ecommerce.microglobal.com.ar/WSMG/WSMG.asmx"

    payload = f'<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<soap:Envelope xmlns:soap=\"http://schemas.xmlsoap.org/soap/envelope/\">\n  <soap:Body>\n    <GetCatalog xmlns=\"http://tempuri.org/\">\n\
        <cliente>{MG_CLIENTE}</cliente>\n      <usuario>{MG_USUARIO}</usuario>\n      <password>{MG_PASSWORD}</password>\n    </GetCatalog>\n  </soap:Body>\n</soap:Envelope>\n'

    headers = {
      'Content-Type': 'text/xml; charset=utf-8',
      'SOAPAction': 'http://tempuri.org/GetCatalog'
    }
    try:
        # Conecta a Microglobal y trae el catálogo de productos
        response = httpx.post(url, headers=headers, data=payload)
        response.raise_for_status()     # if response code != 2xx raises an exception
        return response.text
    
    except httpx.HTTPStatusError as e:
        print(f'Status Error conectando a {url}\n{e}')
        return False
    
    except httpx.HTTPError as e:
        print(f'HTTP Error conectando a {url}\n{e}')
        return False    
    
    #except requests.exceptions.SSLError as e:
    #    print(f'SSL Error (Certificado SSL expirado?) conectando a {url}\n{e}')
    #    #   notificar por telegram
    #    mensaje = f'🔴   Problemas para conectar con MICROGLOBAL.\n\nSSL Error (Certificado SSL expirado?)\n\n{type(e)}'
    #    #mandar_mensaje_telegram("iojan", chat_telegram("ineabots"), mensaje)
    #    return False

    #except requests.exceptions.RequestException as e:
    #    print(f'Error conectando a {url}\n{e}')
    #    mensaje = f'🔴   Problemas para conectar con MICROGLOBAL.\n\nRequest Error\n\n{type(e)}'
    #    #mandar_mensaje_telegram("iojan", chat_telegram("ineabots"), mensaje)
    #    #return handle_exception_and_notify(e, mensaje)
    #    return False
    
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

    #   Comprueba si hay errores en la respuesta del servidor MG
    server_result = soup.find("result").text
    if mg_get_response_error(server_result) != None:
        print(f'Error conectando a MG: {mg_get_response_error(server_result)}')
        return None
        
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
            "timestamp": datetime.now() if kwargs.get("timestamp", False) else None,
            "sku": skus[i].text if kwargs.get("sku", False) else None,
            "nombre": nombres[i].text if kwargs.get("nombre", False) else None,
            "marca": marcas[i].text if kwargs.get("marca", False) else None,
            "categoria": categorias[i].text if kwargs.get("categoria", False) else None,
            "cod_cat": cod_cats[i].text if kwargs.get("cod_cat", False) else None,
            "costo": float(costos[i].text) if kwargs.get("costo", False) else None,
            "stock": int(stocks[i].text) if kwargs.get("stock", False) else None,
            "iva": float(ivas[i].text) if kwargs.get("iva", False) else None,
            "ean": str(upcs[i].text) if kwargs.get("ean", False) else None
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

def mg_get_brands_xml() -> Union[str, bool]:
    """Trae el xml con las marcas de Microglobal
    """
    # Carga variables de entorno
    load_dotenv()

    MG_CLIENTE = os.getenv("MG_CLIENTE")
    MG_USUARIO = os.getenv("MG_USUARIO")
    MG_PASSWORD = os.getenv("MG_PASSWORD")

    url = "https://ecommerce.microglobal.com.ar/WSMG_back/WSMG.asmx"

    payload = f'<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<soap:Envelope xmlns:soap=\"http://schemas.xmlsoap.org/soap/envelope/\">\n  <soap:Body>\n    <GetBrands xmlns=\"http://tempuri.org/\">\n\
                    <cliente>{MG_CLIENTE}</cliente>\n      <usuario>{MG_USUARIO}</usuario>\n      <password>{MG_PASSWORD}</password>\n    </GetBrands>\n  </soap:Body>\n</soap:Envelope>\n'
    headers = {
        'Content-Type': 'text/xml; charset=utf-8',
        'SOAPAction': 'http://tempuri.org/GetBrands'
    }

    try:
        response = httpx.post(url, headers=headers, data=payload)

        # Conecta a Microglobal y trae el catálogo de marcas
        if response.status_code != 200:
            print(response.status_code, response.text)
            return False
        else:
            return response.text
        
    #except requests.exceptions.RequestException as e:
    #    print(f'Error conectando a {url}\n{e}')
    #    mensaje = f'🔴   Problemas para conectar con MICROGLOBAL.\n\nRequest Error\n\n{type(e)}'
    #    #mandar_mensaje_telegram("iojan", chat_telegram("ineabots"), mensaje)
    #    #return handle_exception_and_notify(e, mensaje)
    #    return False

    except Exception as e:
        print(f'{type(e)} Error inesperado\n{e}')
        mensaje = f'🔴   Problemas para conectar con MICROGLOBAL.\n\nRequest Error\n\n{type(e)}'
        #mandar_mensaje_telegram("iojan", chat_telegram("ineabots"), mensaje)
        return False    

#   Funciones que traen códigos de error de Microglobal y lo bajan a un archivo json

def mg_get_error_codes_xml():
    """ 
    Trae el xml con los códigos de error de Microglobal.
    Devolución:
        str con el xml de códigos de error. False si hay error.
    """


    # Carga variables de entorno
    load_dotenv()

    MG_CLIENTE = os.getenv("MG_CLIENTE")
    MG_USUARIO = os.getenv("MG_USUARIO")
    MG_PASSWORD = os.getenv("MG_PASSWORD")

    url = "https://ecommerce.microglobal.com.ar/WSMG_back/WSMG.asmx"

    payload = f'<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<soap:Envelope xmlns:soap=\"http://schemas.xmlsoap.org/soap/envelope/\">\n  <soap:Body>\n    <GetErrors xmlns=\"http://tempuri.org/\">\n      <cliente>{MG_CLIENTE}</cliente>\n      <usuario>{MG_USUARIO}</usuario>\n      <password>{MG_PASSWORD}</password>\n    </GetErrors>\n  </soap:Body>\n</soap:Envelope>\n'
    headers = {
        'Content-Type': 'text/xml; charset=utf-8',
        'SOAPAction': 'http://tempuri.org/GetErrors'
    }

    try:
        response = httpx.post(url, headers=headers, data=payload)
        response.raise_for_status()
        return response.text
    
    except httpx.HTTPStatusError as e:
        print(f'Status Error conectando a {url}\n{e}')
        #mensaje = f'🔴   Problemas para conectar con MICROGLOBAL.\n\Status Error\n\n{type(e)}'
        #mandar_mensaje_telegram("iojan", chat_telegram("ineabots"), mensaje)
        return False
    except httpx.HTTPError as e:
        print(f'HTTP Error conectando a {url}\n{e}')
        #mensaje = f'🔴   Problemas para conectar con MICROGLOBAL.\n\Status Error\n\n{type(e)}'
        #mandar_mensaje_telegram("iojan", chat_telegram("ineabots"), mensaje)
        return False    
    except Exception as e:
        print(f'{type(e)} Error inesperado\n{e}')
        mensaje = f'🔴   Problemas para conectar con MICROGLOBAL.\n\nRequest Error\n\n{type(e)}'
        #mandar_mensaje_telegram("iojan", chat_telegram("ineabots"), mensaje)
        return False    

def mg_parse_error_codes(xml):
    """ 
    Parsea el xml de códigos de error de Microglobal y lo guarda en un diccionario.
    Devolución:
        dict con los códigos de error.
    """


    soup = BeautifulSoup(xml, 'xml')

    errors = soup.find_all("Error")

    errors_dict = {}
    
    for e in errors:
        error_code = e.find("codError").text
        error_message = e.find("error").text
        errors_dict[error_code] = error_message
        #print(f'{error_code}: {error_message}')

    return errors_dict

def mg_write_error_codes_to_file(errors_dict: Dict, path=f'{data_dir}/mg_error_codes.json') -> Dict:
    """ 
    Guarda en un archivo json los códigos de error de Microglobal. 
    Si el archivo ya existe, lo sobreescribe. 
    Si no existe, lo crea. 
    Si hay error, devuelve False. 
    Si no hay error, devuelve el dict con los códigos de error. 
    Argumentos: 
        errors_dict (dict): Diccionario con los códigos de error. 
        Ejemplo: {2: "En mantenimiento - Intente nuevamente más tarde", 5: "El usuario no es válido"} 
    Ejemplo de uso: 
        errors_dict = mg_parse_error_codes(xml) 
        mg_write_error_codes_to_file(errors_dict) 
    Devolución:
        dict con los códigos de error.
    """

    # Converts dict to json
    errors_json = json.dumps(errors_dict, indent=4)
    print(errors_json)

    # Writes json to file
    with open(path, 'w') as f:
        f.write(errors_json)
    return errors_dict

def mg_load_error_codes_from_file(file_path: str=f'{data_dir}/mg_error_codes.json') -> Union[Dict, None]:
    """ 
    Carga los códigos de error de Microglobal desde un archivo json. 
    Si el archivo no existe, devuelve None. 
    Si no hay error, devuelve el dict con los códigos de error. 
    Argumentos: 
        file_path (str): Ruta del archivo json con los códigos de error. 
        Por defecto, usa el archivo mg_error_codes.json en la carpeta data. 
    Ejemplo de uso: 
        errors_dict = mg_load_error_codes_from_file() 
    Devolución:
        dict con los códigos de error.
    """

    if not os.path.exists(file_path):
        return None

    with open(file_path, 'r') as f:
        errors_dict = json.load(f)
        #print(errors_dict)
        return errors_dict

def mg_get_response_error(mg_server_result_code: str) -> Union[str, None]:
    error_codes = {
        "50": "Mapeo IDs - Cliente nulo o vac\u00edo",
        "0": "OK",
        "1": "No pudo recuperarse Error",
        "2": "En mantenimiento - Intente nuevamente m\u00e1s tarde",
        "3": "Error interno",
        "4": "Contrase\u00f1a nula",
        "5": "El usuario no es v\u00e1lido",
        "6": "El usuario no est\u00e1 habilitado",
        "7": "Contrase\u00f1a incorrecta",
        "8": "No pudo validarse el cliente",
        "9": "No se han podido obtener los productos",
        "10": "No se han podido obtener los productos de stock y precio",
        "11": "Int\u00e9ntelo m\u00e1s tarde",
        "12": "No pudo realizarse la solicitud",
        "13": "No se han podido obtener las categor\u00edas",
        "14": "No se han podido obtener las marcas",
        "15": "Pedido recibido nulo",
        "16": "Pedido recibido - Tags nulo o cantidad inv\u00e1lida",
        "17": "Pedido recibido - IDs nulo o elementos inv\u00e1lidos",
        "18": "Pedido recibido - PaymentStatus nulo o vac\u00edo",
        "19": "Pedido recibido - DeliveryStatus nulo o vac\u00edo",
        "20": "Pedido recibido - DeliveryMethod nulo o vac\u00edo",
        "21": "Pedido recibido - Currency nulo o inv\u00e1lido",
        "22": "Pedido recibido - IsCanceled nulo o inv\u00e1lido",
        "23": "Pedido recibido - Date nulo o inv\u00e1lido",
        "24": "Pedido recibido - Products nulo o cantidad inv\u00e1lida",
        "25": "Pedido recibido - Payments nulo o cantidad inv\u00e1lida",
        "26": "Pedido recibido - Shipments nulo o cantidad inv\u00e1lida",
        "27": "Mapeo Pedido - PaymentStatus NO Aprobado",
        "28": "Mapeo Pedido - PaymentStatus nulo",
        "29": "Mapeo Pedido - Payments nulo",
        "30": "Mapeo Payments - Pagos inv\u00e1lidos",
        "31": "Mapeo Payments - \u00daltimo pago realizado es NO Aprobado",
        "32": "Mapeo Comprobante - No pudo mapearse comprobante",
        "33": "Mapeo Tags - Tags no v\u00e1lidos",
        "34": "Mapeo Tags - Tags nulo o vac\u00edo",
        "35": "Mapeo Tags - Tag obtenido no coincide ID Cliente",
        "36": "Mapeo Forma de Pago - No realizado",
        "37": "Mapeo Forma de Entrega - Courier nulo o vac\u00edo",
        "38": "Mapeo Datos Entrega - no pudo recuperarse datos seg\u00fan cliente y lugar de entrega provistos",
        "39": "Mapeo Datos Entrega - no pudo recuperarse datos seg\u00fan cliente",
        "40": "Mapeo IDs - ID nulo o vac\u00edo",
        "41": "Mapeo Detalle Ndp - Hay al menos un producto nulo o vac\u00edo",
        "42": "Mapeo Detalle Ndp - Hay al menos un producto con cantidad inv\u00e1lida.",
        "43": "Mapeo Detalle Ndp - El siguiente PartNumber no es v\u00e1lido",
        "44": "Mapeo Detalle Ndp - El siguiente PartNumber tiene bundle",
        "45": "Mapeo Detalle Ndp - No pudo obtenerse c\u00f3digo de art\u00edculo para este PartNumber",
        "46": "Mapeo Detalle Ndp - Hay PartNumbers repetidos",
        "47": "AltaDePedido - No pudo realizarse el Alta del Pedido",
        "48": "Mapeo Cliente - No pudo realizarse mapeo seg\u00fan ID Cliente y ID Tienda provistos",
        "49": "ExistenciaNdp - Existe Ndp con ID provisto"
    }

    
    if mg_server_result_code != "0":
        if mg_server_result_code in error_codes:
            error_message = error_codes[mg_server_result_code]
        else:
            error_message = f'No se pudo recuperar el código de error MG {mg_server_result_code}'

        #print(f'{error_message}')
        return error_message

    else:
        return None



if __name__ == "__main__":
    """
        #DATABASE = ""
    DATABASE = "local"

   #   Connect to db and start a session
    if DATABASE == "local":
        #   local test database
        ce = db_connection(TEST_MYSQL_USER, TEST_MYSQL_PASS, TEST_MYSQL_HOST, TEST_MYSQL_PORT, TEST_DB)
    else:
        #   remote production database
        ce = db_connection(PRODUCCION_MYSQL_USER, PRODUCCION_MYSQL_PASS, PRODUCCION_MYSQL_HOST, PRODUCCION_MYSQL_PORT, PRODUCCION_DB)
    
    connection = ce[0]
    engine = ce[1]

    #   Create database session
    Session = sessionmaker(bind=engine)
    session = Session()    

    # ! Descomentar para crear tablas nuevas que se hayan definido
    #create_tables(engine)

    connection.close()
    """
    
    print(parse_mgcat(mg_cat_xml()))

    #cat_response = mg_cat_xml()
    #mg_get_response_error("100")

    pass
