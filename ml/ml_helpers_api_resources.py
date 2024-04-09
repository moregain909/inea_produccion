
from typing import List

import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
path2root = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(path2root)
data_dir = os.path.join(path2root, "data")
sys.path.append(data_dir)

from auth import Credentials, ml_aut, MlSession
from ml_helpers_objects import MlItem, MlPrice


# Clases que definen recursos de la API de ML

class MlApiResource():

    base_url = ""
    pass


class MlItemsDetails(MlApiResource):

    # Obtiene un listado de ítems de ML detallados

    base_url = "https://api.mercadolibre.com/items"


    def __init__(self, cls, seller_id, items=[], attributes=[]):

        self.seller_id = seller_id
    
        # Crea lista de items (MlItem) y agrega items a la URL
        self.items = []
        items_to_add = ""
        for item in items:
            self.items.append(MlItem(ml_id=item, seller_id=seller_id))
            items_to_add += f'{item},'
        items_to_add = items_to_add[:-1]

        self.url = f'{cls.base_url}?ids={items_to_add}'

        # Agrega attributes a la URL

        if len(attributes) > 0:
            self.attributes_to_get = attributes
            attributes_to_add = "".join(f'{attribute},' for attribute in attributes)
            attributes_to_add = attributes_to_add[:-1]
            self.url += f'&attributes={attributes_to_add}'


    def parse_json(self, json):
        for result in json:
            if result["code"] != 200:
                print(f'Error al obtener el detalle del item \n {result}')
            else:
                json_item = result["body"]
                json_item_id = json_item["id"]
                for item in self.items:
                    if item.ml_id == json_item_id:
                        if self.attributes_to_get:
                            for attribute in self.attributes_to_get:
                                setattr(item, attribute, json_item[attribute])
                        else:
                            #TODO: Acá tengo que decidir qué info parsear por default
                            pass
                            item.title = json_item["title"]
                            item.available_quantity = json_item["available_quantity"]
                            #item.permalink = json_item["permalink"]
                            #item.listing_type_id = json_item["listing_type_id"]
                            #item.channels = json_item["channels"]
        pass

class MlPrices(MlApiResource):

    base_url = f'https://api.mercadolibre.com/items/'
    

    def __init__(self, cls, item_id, channels=[], loyalty_level=None):
        self.item_id = item_id
        self.url = f'{cls.base_url}{self.item_id}/sale_price'


    def parse_json(self, json):

        #"id"
        #"type"
        #"amount"
        #"regular_amount"
        #"currency_id"
        #"context_restrictions"
        #"promotion_id"
        #"promotion_type"
        #"start_time"
        #"end_time"
        pass


class MlQuestion(MlApiResource):

    """
    Ejemplo de respuesta de la API de ML:
    {
        "id": 12776462136,
        "seller_id": 77581040,
        "text": "Hola. Sirve para recetas sin harina de trigo? Sin tacc sería?",
        "tags": null,
        "status": "ANSWERED",
        "item_id": "MLA702754307",
        "date_created": "2023-07-12T20:57:13.831-04:00",
        "hold": false,
        "deleted_from_listing": true,
        "answer": {
            "text": "Hola. Si, sirve . Saludos",
            "status": "ACTIVE",
            "date_created": "2023-07-12T21:40:22.222-04:00"
        },
        "from": {
            "id": 237327599,
            "answered_questions": 0
        }
    }

    base_url = https://api.mercadolibre.com/questions/$_QUESTION_ID
    """
    pass

class MlSellerItems(MlApiResource):

    """Clase que representa un listado de IDs publicaciones de ML. \n
    Llama al recurso https://api.mercadolibre.com/users/$USER_ID/items/search. \n
    Some filters: \n
    by status=active/paused/closed/pending/not_yet_active/programmed, \n
    by SKU: sku=$SELLER_CUSTOM_FIELD / seller_sku=$SELLER_SKU, \n
    by Missing_product_identifiers=true/false (EAN), \n
    To get a list of all available filters in the response, include the filter include_filters=true \n    
    """


    # Obtiene un listado de los ítems publicados por determinado vendedor desde su cuenta
    base_url = "https://api.mercadolibre.com/users"


    def __init__(self, user_id, filters=[], sort=None):
        
        self.user_id = user_id

        # Agrega sort a la URL
        if sort:
            url_attrs_quantity = 1
            self.sort = f'?orders={sort}'
        else:
            url_attrs_quantity = 0
            self.sort = f'?orders=price_asc'

        self.url = f"{self.base_url}/{self.user_id}/items/search{self.sort}"
         
        # Agrega filters a la URL 
        if len(filters) > 0:
            filter_joint = "".join(f'&{filter}' for filter in filters)
            self.url += filter_joint

        self.items: List[MlItem] = []


    def parse_json(self, json):

        for result in json['results']:
            item = MlItem()
            item.ml_id = result
            self.items.append(item)
        
        return True
        


def get_ml_json(ml_resource_object: MlApiResource, ml_session: MlSession, paging_str=None):
    

    client = ml_session.client

    headers = {'Authorization': ml_session.token}

    url = ml_resource_object.url
    
    # Agrega offset de paginación a la URL
    if paging_str:
        url += f'&offset={paging_str}'

    response = client.get(url, headers=headers)

    if response.status_code != 200:
        print(f'No se pudo traer json del recurso {url} para {ml_session.store_name}')
        print(response.status_code, response.text)
        return None    

    j = response.json()           
            
    return j


def set_all_resource_items(ml_resource_object: MlApiResource, ml_session: MlSession):

    # Trae json y lo parsea en el ml_resource_object

    #TODO: Scan + Hash pendiente de implementar:
    #TODO: Para obtener más de 1000 resultados (pag_total > 1000), se debe implementar Scan + Hash (search_type=scan + scroll_id)
    #TODO: Más info en https://developers.mercadolibre.com.ar/es_ar/items-y-busquedas#Modo-de-busqueda-por-encima-de-1000-registros


    paging = 0
    pag_total = 1

    while paging <= pag_total:
        paging_str = str(paging)

        # Trae JSON 
        json = get_ml_json(ml_resource_object, ml_session, paging_str)

        # Incorpora info al ml_resurce_object
        ml_resource_object.parse_json(json)

        pag_total = json['paging']['total']
        paging += 50

    return True


if __name__ == "__main__":

    session = MlSession("tecnorium")

    items = MlSellerItems(user_id="12313", filters=[{"status":"active"}])
    set_all_resource_items(ml_resource_object=items, ml_session=session)
    print(items.items)

    pass
