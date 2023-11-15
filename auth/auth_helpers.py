from dataclasses import dataclass, field, asdict
#import os
#import copy
from typing import List, Dict, Union
from decouple import AutoConfig, config, UndefinedValueError
from dotenv import *
import httpx
#from openpyxl import load_workbook, Workbook

#   AUTENTICACIÓN EN ML

#config = AutoConfig(' ')    # previene un bug the decouple que a veces no encuentra .env desde Jupyter

@dataclass
class Credentials:
    store: str = field(repr=True, default="tecnorium")
    app_id: str = field(repr=True, default=None) # también documentado o referenciado como CLIENT_ID
    client_secret = str, field(repr=True, default=None)
    refresh_token = str, field(repr=True, default=None)
    user_id: str = field(repr=True, default=None)

    def __post_init__(self) -> None:
        self.get_credentials()

    def get_credentials(self) -> bool:
        """Trae credenciales para ML de las variables de entorno.
        Argumento:
            store (str): Alias de la tienda. Tiene que estar mapeado en credentials_map.
        Devolución:
            Dict con credenciales (Ej. )
        """

        # Diccionario que mapea store a keys de credenciales de entorno
        credentials_map = {
            ("tecnorium", "tecnorrum"): ("TEC_CLIENT_ID", "TEC_CLIENT_SECRET", "TEC_REFRESH_TOKEN", "TEC_USER_ID"), \
            ("celestron",): ("CEL_CLIENT_ID", "CEL_CLIENT_SECRET", "CEL_REFRESH_TOKEN", "CEL_USER_ID"), \
            ("lenovo", ): ("LEN_CLIENT_ID", "LEN_CLIENT_SECRET", "LEN_REFRESH_TOKEN", "LEN_USER_ID"), \
            ("iojan", "iojann"): ("IOJAN_CLIENT_ID", "IOJAN_CLIENT_SECRET", "IOJAN_REFRESH_TOKEN", "IOJAN_TEC_USER_ID"), \
            ("test01" ,): ("IOJAN_CLIENT_ID", "IOJAN_CLIENT_SECRET", "TEST01_REFRESH_TOKEN", "TEST01_USER_ID")
        }

        # Trae las credenciales de .env con config
        store = self.store.lower()
        for s, c in credentials_map.items():
            if store in s:
                try:
                    self.app_id = config(c[0])
                    self.client_secret = config(c[1])
                    self.refresh_token = config(c[2])
                    self.user_id = config(c[3])
                    return True
                except UndefinedValueError as e:
                    print(f"{e}")
                    #print("Me está dando UndefinedValueError")
                except Exception as e:
                    print(type(e), e)
                    
                return False
        print(f"No se tienen credenciales de la tienda {store}\n") 
        return False
   
            
def ml_aut(tienda: str = "tecnorium", client: httpx.Client = None)-> Union[str, None]:
    """
    Autentica en ML
    Argumentos:
        tienda (str): Alias de una tienda ML de la que tengamos las credenciales en .env y figure mapeado en credentials_map de get_credentials(). Default=None.
        session (httpx.Client()): Cliente de httpx que puede compartirse con otras funciones. Default=None. Si no se declara, crea uno.
    Devolución:
        Entrega un token (str) para autenticar en ML. Si el server devuelve error, la función devuelve False.
    """
    if not client:
        client = httpx.Client()
    else:
        client = client

    c = Credentials(tienda)
    
    # autentica en ML

    url = "https://api.mercadolibre.com/oauth/token"
    payload=f'grant_type=refresh_token&client_id={c.app_id}&client_secret={c.client_secret}&refresh_token={c.refresh_token}'
    headers = {
      'accept': 'application/json',
      'content-type': 'application/x-www-form-urlencoded'
    }
    response = client.post(url, headers=headers, data=payload)
    j = response.json()
    #print(j)

    try:
        token = f'Bearer {j["access_token"]}'
    except KeyError as e:
        print(f'{tienda}: Token inválido. {e}')
        print(response.status_code, response.text)
        return None
    except Exception as e:
        print(tienda, type(e), e)
        print(response.status_code, response.text)
        return None
    
    if response.status_code == 401:
        print("Token inválido")
        return None
    elif response.status_code == 400:
        print(j["error"], j["error_description"])
        return None
    else:
        return(token)

def tienda_publi(item_id, client: httpx.Client):
    """Trae el nombre de la tienda de una publicación de ML.

    Args:
        item_id (_type_): _description_

    Returns:
        _type_: _description_
    """
    TIENDAS = ["tecnorium", "celestron", "lenovo"]
    tienda = ""

    if not client:
        client = httpx.Client()
    else:
        client = client


    for x in TIENDAS:
        token = ml_aut(x)        

        url = "https://api.mercadolibre.com/items/" + item_id

        payload = {}
        headers = {
          'Authorization': token
        }

        response = client.get(url, headers=headers)
        j = response.json()

        if response.status_code == 200:
            id_tienda = j["seller_id"]
            if id_tienda == 77581040:
                tienda = "Tecnorium"
            elif id_tienda == 146367667:
                tienda = "Celestron"
            elif id_tienda == 301181249:
                tienda = "Lenovo"
            
            # print("La tienda de la publicación {} es {}".format(item_id, tienda))
            return tienda
        
    if tienda == "":
        print("No se pudo conseguir la tienda de la publicación {}".format(item_id))
        print(response.status_code, response.text)

@dataclass
class Tienda:
    name: str = field(repr=True, default=None)
    token: str = field(repr=None, default=None)
    client: httpx.Client = field(repr=None, default=None)

    def __post_init__(self) -> None:
        self.get_token()
        self.get_client()

    def get_token(self) -> None:
        self.token = ml_aut(self.name)
        
    def get_client(self) -> None:
        self.client = httpx.Client()


def format_tienda(tienda):
#   formatea el string tienda de PUBLIS GBP
    split_tienda = tienda.split(" ", 1)
    return split_tienda[0].lower()


if __name__ == '__main__':
    
    ml_aut("lenovo")
    pass