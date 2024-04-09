from bs4 import BeautifulSoup
from dataclasses import dataclass, field
from decimal import Decimal
from dotenv import load_dotenv
import httpx
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


import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
path2root = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(path2root)
data_dir = os.path.join(path2root, "data")
sys.path.append(data_dir)


from auth import Credentials, ml_aut, MlSession
from data.data_helpers import Base, create_tables, db_connection


# Clases que definen objetos de ML (items, variations, orders)

@dataclass
class MlItem:
    
    # Representa un item (publicación) de ML

    ml_id: str = field(repr=True, default=None)
    seller_id: str = field(repr=True, default=None)
    sku: str = field(repr=True, default=None)
    title: str = field(repr=True, default=None)
    price: int = field(repr=True, default=None)
    available_quantity: int = field(repr=True, default=None)
    link: str = field(repr=True, default=None)
    listing_type_id: str = field(repr=True, default=None)
    store: str = field(repr=True, default=None)
    channels: List[str] = field(repr=True, default=None)

    pass


@dataclass
class MlPrice:
    
    # Representa un precio de ML

    price_id: str = field(repr=True, default=None)              # price_id en /sale_price o id en /prices
    item_id: str = field(repr=True, default=None)               # id publicación
    amount: Decimal = field(repr=True, default=None)            # precio de venta actual
    regular_amount: Decimal = field(repr=True, default=None)    # precio original (en blanco si es igual al de venta actual)
    currency_id: str = field(repr=True, default=None)
    reference_date: str = field(repr=True, default=None)
    promotion_id: str = field(repr=True, default=None)          # id de promoción para consultar la oferta en /seller-promotions/offers 
    promotion_type: str = field(repr=True, default=None)

    pass


# Trae JSON con info detallada de una publicación de ML
#! DEPRECANDO
def get_ml_item_details_json(item_id=None, item_object=None, token=None, client=None, store=None):
    """Trae JSON con info detallada de una publicación de ML.

    Args:
        item_id (_type_): _description_
        item_object (MlItem): 
        token (_type_): _description_
        client (_type_): _description_
        store (_type_): _description_
        **fields

    Returns:
        Dict: JSON con info detallada de una publicación de ML.
    """


    # Valida item
    if not item_id and not item_object:        
        raise ValueError("Debe ingresar item_id o item_object")
    
    elif item_id and not item_object:
        item = MlItem(ml_id=item_id)

    elif not item_object.ml_id:
        item_object.ml_id = item_id
        item = item_object


    # Configura httpx client
    if not client:
        client = httpx.Client()
    else:
        client = client


    # Configura token
    if not token:
        if not store:
            raise ValueError("Debe ingresar token o nombre de tienda")
        
        token = ml_aut(store, client=client)


    # Configura url
    url = f'https://api.mercadolibre.com/items/{item.ml_id}'
    

    # Configura headers
    headers = {
        'Authorization': token
    }


    response = client.get(url, headers=headers)

    if response.status_code != 200:
        print(f'No se pudo traer json de la publicación {item_id} apuntando a {url}')
        print(response.status_code, response.text)
        return None

    j = response.json()

    return j

# Parsea JSON de publicación de ML y devuelve un objeto MlItem
#! DEPRECANDO
def parse_ml_item_details_json(item_json=None, store=None, **fields):
    pass

    item = MlItem()

    #TODO: Traer attrs de item
    attributes = []

    for field in fields:
        if field in attributes:
            setattr(item, field, fields[field])

    item["Publicación"] = j["id"]
    item["Título"] = j["title"]
    item["Precio"] = j["price"]
    item["Stock"] = j["available_quantity"]
    item["Link"] = j["permalink"]
    item["Tipo"] = j["listing_type_id"]
    item["Tienda"] = tienda
    item["Channels"] = j["channels"]

    # Trae SKU si la publicación lo tiene
    sku_found = False
    for attribute in j["attributes"]:
        if attribute["id"] == "SELLER_SKU":
            item["sku"] = attribute["value_name"]
            sku_found = True
            break
    # TODO: encontrar la forma de traer el SKU
    # Puede que el SKU tampoco esté en la variación
    # Misterio...
    #if not sku_found:
        
    
    return item

#! DEPRECANDO
def get_ml_item_details(item_id=None, item_object=None, token=None, client=None, store=None, **fields):

    json = get_ml_item_details_json(item_id=None, item_object=None, token=None, client=None, store=None)
    item = parse_ml_item_details_json(item_json=json, **fields)
    
    return item

if __name__ == "__main__":
    pass