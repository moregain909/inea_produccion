
# Clases que representan recursos de la API de ML
import json
import logging
from typing import List, Union, Dict

import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
path2root = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(path2root)
data_dir = os.path.join(path2root, "data")
sys.path.append(data_dir)

from auth import Credentials, ml_aut, MlSession
from ml_helpers_objects import MlItem, MlPrice, MlItemVariation
#import channels

# Set the logging level for httpx to WARNING
logging.getLogger('httpx').setLevel(logging.ERROR)

class MlSellerCatalog():
    tecnorium = "77581040"
    celestron = "146367667"
    lenovo = "301181249"

# Clases que representan recursos de la API de ML

class MlApiResource():

    base_url = ""
    #cls = type(self)

    def set_seller_name(self):
        if self.seller_id:
            for store in dir(MlSellerCatalog()):
                if getattr(MlSellerCatalog(), store, None) == self.seller_id:
                    self.seller_name = store
                    return store
            print(f'La tienda con id {self.seller_id} no está catalogada en MlSellerCatalog.')

        else:
            print(f'Se requiere seller_id para asignar seller_name.')
            return None


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


    def __init__(self, seller_id, filters=[], sort=None):
        
        self.seller_id = seller_id
        self.set_seller_name()

        # Agrega sort a la URL
        if sort:
            url_attrs_quantity = 1
            self.sort = f'?orders={sort}'
        else:
            url_attrs_quantity = 0
            self.sort = f'?orders=price_asc'

        self.url = f"{self.base_url}/{self.seller_id}/items/search{self.sort}"
         
        # Agrega filters a la URL 
        if len(filters) > 0:
            filter_joint = "".join(f'&{filter}' for filter in filters)
            self.url += filter_joint

        self.items: List[MlItem] = []


    def parse_json(self, json):

        count = 0
        for result in json['results']:
            item = MlItem()
            item.ml_id = result
            self.items.append(item)
            count += 1
        #print(f'Se han cargado {count} items.')
        
        return True
        

    def print(self):
        for item in self.items:
            print(item.ml_id)


class MlItemsDetails(MlApiResource):

    # Obtiene un listado de ítems de ML detallados
    # Acepta hasta 20 items como argumento de entrada


    base_url = "https://api.mercadolibre.com/items"


    def __init__(self, seller_id: int, items: List[Union[str, MlItem]] =[], attributes:List[str] =[]):

        self.seller_id = seller_id
    
        # Crea lista de items (MlItem) y agrega items al string de la URL
        self.items = []
        items_to_add_to_url = ""
        
        for item in items:

            if not isinstance(item, MlItem):
                item = MlItem(ml_id=item)
                #self.items.append(MlItem(ml_id=item, seller_id=self.seller_id))
                #items_to_add_to_url += f'{item},'
            item.seller_id = self.seller_id
            self.set_seller_name()
            item.seller_name = self.seller_name
            self.items.append(item)
            items_to_add_to_url += f'{item.ml_id},'

        items_to_add_to_url = items_to_add_to_url[:-1]

        cls = type(self)
        self.url = f'{cls.base_url}?ids={items_to_add_to_url}'

        # Agrega a la URL los attributes especificados
        if len(attributes) > 0:
            self.attributes_to_get = attributes

            # Valida que estén presentes los atributos id y channels
            if "channels" not in attributes:
                self.attributes_to_get.append("channels")
            if "id" not in attributes:
                self.attributes_to_get.append("id")     # si se especifican atributos en la llamada, hay que incluir id para que lo traiga


            attributes_to_add = "".join(f'{attribute},' for attribute in attributes)
            attributes_to_add = attributes_to_add[:-1]
            self.url += f'&attributes={attributes_to_add}'
            #print()
            #print(self.url)
            #print()

    def parse_json(self, json, channel_filter=['marketplace', 'mshops']):

    #! NOT CHANNELS 'mp-merchants', 'mp-link'
        
        # quita el id para no duplicarlo (ya está como self.ml_id)
        if "attributes_to_get" in dir(self):
            if "id" in self.attributes_to_get:
                self.attributes_to_get.remove("id")     
        for result in json:

            # Valida que la respuesta para el item sea exitosa. Si no, continúa con el siguiente item.
            if result["code"] != 200:
                print(f'Error {result["code"]} al obtener el detalle del item {result["body"]["id"]}\n Error: {result["body"]["error"]}.\n {result["body"]["message"]}')
                continue
 


            json_item = result["body"]  # formato de respuesta cuando se especifican atributos

            json_item_id = json_item["id"]

            for item in self.items[:]:
            
                if item.ml_id == json_item_id:
            
                    # Valida que el item esté publicado en alguno de los canales que especificamos en el channel_filter
                    # Si no, elimina el item de la lista de items a parsear y continúa con el siguiente.
                    in_channel_filter = False
                    for channel in channel_filter:
                        if channel in json_item['channels']:
                            in_channel_filter = True
                            break
                    if not in_channel_filter:
                        self.items.remove(item)
                        print(f'El item {item.ml_id} no está publicado en ninguno de los canales especificados. {channel_filter}')
                        continue

                    # Agrega los atributos del item a la lista de items a parsear si los hay.

                    if "attributes_to_get" in dir(self):
                        for attribute in self.attributes_to_get:

                            if attribute != "variations":
                                setattr(item, attribute, json_item[attribute])

                            # Procesa variaciones
                            else:
                                variations = []
                                for variation_json in json_item["variations"]:
                                    variation = MlItemVariation(variation_id=variation_json["id"])
                                    variation.parse_json(variation_json)
                                    variation.parse_picture_urls()
                                    variations.append(variation)
                                setattr(item, attribute, variations)

                    else:
                        # Atributos por default (si no se especifican en la llamada)
                        item.title = json_item["title"]
                        item.available_quantity = json_item["available_quantity"]
                        item.listing_type_id = json_item["listing_type_id"]
                        item.permalink = json_item["permalink"]
                        item.channels = json_item["channels"]
                        item.status = json_item["status"]
                        item.catalog_listing = json_item["catalog_listing"]
                        item.price = json_item["price"]

                        if len(json_item["variations"]) > 0: 
                            pass
                            #TODO: AGREGAR VARIACIONES
                        
                        for attribute in json_item["attributes"]:
                            if attribute["id"] == "SELLER_SKU":
                                item.sku = attribute["value_name"]
                                break
                            elif attribute["id"] == "SELLER_CUSTOM_FIELD":
                                item.sku = attribute["value_name"]
                                break


                        logging.info(f'Item {item.ml_id} parsed - {item.available_quantity} {item.title}')
            #print(f'Termina de parsear ItemsDetails y quedan {len(self.items)} items')
        pass

    def print_items(self, attributes=None):
        for item in self.items:
            if not attributes:
                attrs = [{attr: getattr(item, attr, None)} for attr in dir(item) \
                         if not attr.startswith("_") and not callable(getattr(item, attr))]
                print(attrs)
            else:
                for attr in attributes:
                    attrs_to_print = {attr: getattr(item, attr, None)}
                print(attrs_to_print)


class MlApiPrices(MlApiResource):

    """Representa los recursos /prices y /sale_price de un item de ML en la API de ML.

    """

    base_url = f'https://api.mercadolibre.com/items/'
    

    def __init__(self, item_id: str, channels: List[str] =[], loyalty_level: str =None, resource="prices"):
        self.item_id = item_id
        self.channels: List[str] = channels
        self.loyalty_level: str = loyalty_level
        self.resource: str = resource
        self.items = []        
        
        cls = type(self)
        if resource in ["prices", "sale_price"]:
            self.url = f'{cls.base_url}{self.item_id}/{resource}'
        else:
            raise ValueError(f'Resource {resource} no aceptado en la url del recurso prices de la API')

        # Agrega contexto a la url si se llama al recurso sale_price
        if resource == "sale_price":
            context = 0
            if channels:
                context += 1
                channels_str = "".join(f'{channel},' for channel in channels)
            else:
                channels_str = ""

            if loyalty_level:
                context += 1
            else:
                loyalty_level = ""
            
            if context > 0:
                context_separator = ""
            if context >1:
                context_separator = "&"
                self.url += f'?context={channels_str}{context_separator}{loyalty_level}'
        


    def parse_json(self, json):

        # Parsea json de sale_price
        # Agrega 1 item a la lista de self.items (precios)
        if self.resource == "sale_price":
            item = MlItem(ml_id=self.item_id, item_id=self.item_id)
            item.context_restrictions = []
            if self.channels:
                item.context_restrictions.extend(channels)
            if self.loyalty_level:
                item.context_restrictions.append(self.loyalty_level)
            item.price_id = json["price_id"]
            item.amount = json["amount"]
            item.regular_amount = json["regular_amount"]
            item.currency_id = json["currency_id"]
            item.reference_date = json["reference_date"]
            item.metadata = json["metadata"]

            self.items.append(item)

        # Parsea json de prices
        # Agrega 1 o varios items a la lista de self.items (precios)
        else:
            for price in json["prices"]:
                item = MlItem(ml_id=self.item_id, item_id=self.item_id)
                item.type = price["type"]
                item.amount = price["amount"]
                item.regular_amount = price["regular_amount"]
                item.currency_id = price["currency_id"]
                item.last_updated = price["last_updated"]
                item.context_restrictions = price["conditions"]["context_restrictions"]
                item.start_time = price["conditions"]["start_time"]
                item.end_time = price["conditions"]["end_time"]

                self.items.append(item)




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



# Funciones que actúan sobre los recursos de la API de ML o los objetos que los representan

def get_ml_json(ml_resource_object: MlApiResource, ml_session: MlSession, paging_str=None) -> Dict:
    """ Realiza la llamada al recurso de la API de ML y retorna el json.
    Si la llamada falla, retorna None.
    """

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

    """ Trae todas las páginas de un recurso de API de ML y las parsea en el ml_resource_object que lo representa.
    
    """
    # Trae json y lo parsea en el ml_resource_object

    #TODO: Scan + Hash pendiente de implementar:
    #TODO: Para obtener más de 1000 resultados (pag_total > 1000), se debe implementar Scan + Hash (search_type=scan + scroll_id)
    #TODO: Más info en https://developers.mercadolibre.com.ar/es_ar/items-y-busquedas#Modo-de-busqueda-por-encima-de-1000-registros


    paging = 0
    pag_total = 1

    while paging <= pag_total:
        paging_str = str(paging)
        #print(f'Paging: {paging_str}')

        # Trae JSON 
        json = get_ml_json(ml_resource_object, ml_session, paging_str)

        # Incorpora info al ml_resurce_object
        ml_resource_object.parse_json(json)

        pag_total = json['paging']['total']
        #print(f'Pag_total: {pag_total}')
        
        paging += 50

    return True


def get_all_seller_item_details(seller_items: MlSellerItems, session: MlSession = None, attributes: List[str] =[]) -> List:
    """ Trae detalles de todas las publicaciones listadas dentro de un MlSellerItems.
    """
    if not session:
        session = MlSession(store_name=seller_items.seller_name)

    # Genera un lista con MlItemsDetails con un máximo de 20 items cada uno
    items = seller_items.items
    max_idx = len(items) - 1
    max_idx_per_call = 20
    curr_idx = 0
    from_idx = 0
    to_idx = max_idx_per_call

    list_of_items_details = []

    while curr_idx <= max_idx:

        # Popula lista de hasta 20 items para crear un MlItemsDetails
        items_to_add = []
        for idx in range(from_idx,to_idx):
            if idx <= max_idx:
                items_to_add.append(items[idx])
                curr_idx += 1
                
        
        # Crea un MlItemsDetails con los hasta 20 items y lo agrega a la lista final
        item_details = MlItemsDetails(seller_items.seller_id, items_to_add, attributes=attributes)
        list_of_items_details.append(item_details)
        from_idx += 20
        to_idx += 20
    #print(f'Total de ItemsDetails: {len(list_of_items_details)}')
    
    #for item_detials in list_of_items_details:
    #    print(f'{item_detials.url}')

    
    # Genera un nuevo MlSellerItems con los detalles de cada item
    final_seller_items = seller_items   # copia el original
    final_seller_items.items = []       # vacía la lista de items original

    # Trae detalles para cada MlItemDetails
    count = 0
    for items in list_of_items_details:
        #print(f'-- Acá va a parsear {len(items.items)} items')
        json = get_ml_json(items, session)
        items.parse_json(json)
        #print(f'-- Acá termina de parsear {len(items.items)} items')
        count += len(items.items)
        # agrega items con detalles de cada MlItemDetails al MlSellerItems final
        final_seller_items.items.extend(items.items)   
    #print(f'--Total de items parseados: {count}')
    return final_seller_items.items
    
    

if __name__ == "__main__":

    session = MlSession(store_name="tecnorium")

    # trae todos los item_ids activos
    item_ids = MlSellerItems(session.credentials.user_id, filters=["status=active"])
    set_all_resource_items(item_ids, session)
    print(f'Total de IDs parseados: {len(item_ids.items)}')
    

    #set_all_resource_items(ml_resource_object=items, ml_session=session)
    list_of_detailed_items = get_all_seller_item_details(item_ids, session=session, attributes=["price", "available_quantity"])

    #for item in list_of_detailed_items:
    #    print(f'{item.ml_id} - precio: {item.price}, stock: {item.available_quantity}')

    #items.print()

    #details = MlItemsDetails(seller_id=session.credentials.seller_id, items=[items.items[100].ml_id], attributes=["id", "channels", "title", "price", "available_quantity"])
    #details = MlItemsDetails(seller_id=session.credentials.user_id, items=items.items)

    #print(f'{details.url}')
    #jason = get_ml_json(details, session)

    """
    #print(json.dumps(jason, indent=4))
    details.parse_json(jason)

    
    details.print_items()
    print(len(details.items))


    publis = get_MlSellerItemDetails(items, session=session, attributes=["price", "available_quantity"])


    for publi in publis:
        print(f'{publi.ml_id} - {publi.price} - {publi.available_quantity}')
    """

    print(f'Total de publicaciones sin parsear: {len(item_ids.items)}')
    print(f'Total de publicaciones parsear y con detalles: {len(list_of_detailed_items)}')
    