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
import requests

import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
path2root = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(path2root)

from auth import Credentials, ml_aut, tienda_publi
from ml.ml_helpers_objects import MLItem

# ! Clases para trabajar con órdenes de venta de ML



#@dataclass
#class MLItem:
#    pass

@dataclass
class MLPayment:
    pass

@dataclass
class MLBuyer:
    pass

@dataclass
class MLShippingItem:
    
    # Endpoint: /shipments/$_SHIPMENT_ID/items

    item_id: str        # publicación
    variation_id: str   # variación de la publicación (si no hay variación es null)
    description: str    # título publicación
    order_id: str       # orden de venta
    quantity: int   
    sender_id: int      # vendedor

@dataclass
class MLShipping:
    shipment_id: str
    items: List[MLShippingItem] # https://api.mercadolibre.com/shipments/$_SHIPMENT_ID/items
    pass

@dataclass
class MLOrder:
    order_id: str
    seller_id: int
    pack_order: bool
    pack_id: int
    shipping: MLShipping
    pass



# ! Funciones para obtener ordenes de venta recientes de ML

def get_orders_json(store:str="tecnorium", token:str=None, client:httpx.Client=None, order_option:Union[str, None]=None, \
                    order_status:str="paid", offset:int=0, limit:int=50, *args:List) -> Dict:



    if order_option in ["recent", "reciente", "recientes"]:
        order_option_path = "/recent"       #   Órdenes en los que la fecha actual es anterior a la expiration_date y aún no han sido calificadas por ambas partes
    elif order_option in ["pending", "pendiente", "pendientes"]:
        order_option_path = "/pending"      #   Órdenes en estado “pendiente” omitiendo las canceladas automáticamente
    elif order_option in ["archived", "archivada", "archivadas"]:
        order_option_path = "/archived"     #   Órdenes con expiration_date posterior a la fecha actual o que fue calificada por ambas partes
    else:
        order_option_path = ""              #   Todas las órdenes creadas hasta 12 meses para atrás

    if order_status in ["paid", "confirmed", "payment_required", "payment_in_process", "partially_paid", "partially_refunded", "pendin_cancel", "cancelld"]:
        order_status = f'&order.status={order_status}'
    else:
        order_status = ""
        if order_status not in [None, "all", "todas"]:
            print(f'Error en el parámetro order_status: {order_status}. Se traen las órdenes con pago acreditado.')
        

    if not client:
        client = httpx.Client()
    else:
        client = client

    if not token:
        token = ml_aut(store, client=client)

    if not args:
        args = ["&sort=date_desc"]
        args = "&".join(args)


    store_id = Credentials(store=store).user_id
    headers = {
        'Authorization': token
    }

    
    url = f'https://api.mercadolibre.com/orders/search{order_option_path}?seller={store_id}{order_status}&offset={offset}&limit={limit}&{args}'

    #payload={}
    headers = {
      'Authorization': token
    }

    try:
        response = client.get(url, headers=headers)
    except Exception as e:
        print(f'Error al hacer la llamada: {e}')
        return None
    
    if response.status_code != 200:
        print(f'Error en la respuesta a la llamada: Status Code {response.status_code}\n{response.text}')
        return None
    
    orders_json = response.json()
    return orders_json
    
def parse_orders_json(orders_json:Dict) -> List:
    orders = []
    for order in orders_json["results"]:
        orders.append(order)
    return orders

def get_orders(store="tecnorium", token=None, client=None, status="active", offset=0, limit=50, max=None, *args):
    # TODO: Implementar función para obtener todos los jsons de las ventas recientes de ML
    # Cada json lo traigo con get_recent_orders_json y lo guardo en una lista
    pass

# ! Funciones para obtener información de envíos de ML

def get_shipment_json(shipment_id:str, token:Union[None, str]=None, store:str="tecnorium", client:Union[None, httpx.Client]=None, option:Union[None, str]=None) -> Union[List, Dict, bool]:

    """ 
    Get shipment info from ML API.

    Args: 
        shipment_id (str): ID of the shipment to get.
        token (str): Token to use for authentication. If not present, will generate one for the store.
        store (str): Store for wich to generate the token if not token provided.
        client (httpx.Client): Client to use for making the request. If None, it will create a new client.
        option (str): Defaults to None. 
            If None, returns json with general shipment info.
            If "items", returns json with items in the shipment.
            If "costs", returns json with 
            If "payments", returns json with 
            If "lead_time", returns json with 
            If "delays", returns json with 
            If "history", returns json with 
            If "carrier", returns json with transport info.

    Returns:
        Union[List, Dict, bool]: If shipment_id not present, returns Fale.
            Else, depending on option argument, returns json containing shipping info and details.

    Raises:
        TypeError: If any of the input arguments is of an invalid type.
    """

    # Validate input provided
    if not shipment_id:
        print("shipment_id cannot be empty")
        return False
    
    # Validate input types
    if not isinstance(shipment_id, str):
        raise TypeError("shipment_id must be a string")
    if not isinstance(token, (type(None), str)):
        raise TypeError("token must be a string or None")
    if not isinstance(client, (type(None), httpx.Client)):
        raise TypeError("client must be a httpx.Client or None")
    if not isinstance(option, (type(None), str)):
        raise TypeError("option must be a string or None")

    # Checks wheter client and token are present 
    if not client:
        client = httpx.Client()
    else:
        client = client
    if not token:
        token = ml_aut(store, client=client)

    headers = {
        'Authorization': token, 
        'x-format-new': 'true'
    }

    # Select the endpoint based on show:items argument:
    # /shipments/$_SHIPMENT_ID/items for list of shipment items
    # /shipments/$_SHIPMENT_ID for general shipment info
    if option in ["items", "costs", "payments", "lead_time", "delays", "history", "carrier"]:
        url = f'https://api.mercadolibre.com/shipments/{shipment_id}/{option}'
    else:
        url = f'https://api.mercadolibre.com/shipments/{shipment_id}'
        if option:
            print(f'No se reconoce la opción {option}, se trae info general del envío {shipment_id}')

    try:
        response = client.get(url, headers=headers)
    except Exception as e:
        print(f'Error al hacer la llamada: {e}')
        return None
    
    if response.status_code != 200:
        print(f'Error en la respuesta a la llamada: Status Code {response.status_code}\n{response.text}')
        return None
    
    shipment_items_json = response.json()
    return shipment_items_json

def parse_shipment_json(shipment_json:Union[Dict, List]):

    pass

def get_statuses_definitions(token:str, client:httpx.Client) -> Union[None, Dict]:

    """Gets definitions for each ML shipment status and substatus.

    Args:
        token (str):
        client (http.Client):
    Returns:
        Union[None, Dict]:
    """

    # Checks whether client and token are present 
    if not client:
        client = httpx.Client()
    else:
        client = client
    if not token:
        token = ml_aut(store, client=client)

    url = "https://api.mercadolibre.com/shipment_statuses"

    headers = {
        'Authorization': token
        }
    
    try:
        response = client.get(url, headers=headers)
    except Exception as e:
        print(f'Error al hacer la llamada: {e}')
        return None

    if response.status_code != 200:
        print(f'Error en la respuesta a la llamada: Status Code {response.status_code}\n{response.text}')
        return None
    
    statuses_definitions = response.json()
    return statuses_definitions

if __name__ == "__main__":

    #   response = get_recent_orders_json(store="tecnorium", limit=4, offset=6), indent=4)
    response = get_shipment_json("41908933856")
    print(json.dumps(response, indent=4))
    
    pass