
# BUSCA PUBLICACIONES INACTIVAS EN ML

# DE LAS QUE NO ESTÁN EN GBP:
#   MUESTRA TITULO Y PRECIO
#   PERMITE SELECCIONAR PARA BORRAR

# DE LAS QUE ESTAN EN GBP:
#   MUESTRA TITULO, PRECIO Y PROVEEDOR
#   PERMITE SELECCIONAR PARA BORRAR

from flask import Flask, render_template, request, flash, send_file, Blueprint
import logging
from typing import List, Dict

import os, sys
path2root = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(path2root)

from auth import MlSession
from ml.ml_helpers_api_resources import set_all_resource_items, MlSellerItems, MlSellerCatalog, get_all_seller_item_details, MlItem

logging.basicConfig(level=logging.DEBUG)

def get_apirequest_filters_from_requestform(request_form) -> List[str]:

    form_keys = list(request_form.keys())
    #print(f'{form_keys}')
    # Detecta qué filtros están presentes en el form
    request_filters = []
    for key in form_keys:
        splitted_key = key.split("_", 1)     # detecta si la key del form tiene prefijo de filtro (requestfilter)
        #print(f'splitted_key = {splitted_key}')
        if splitted_key[0] == "requestfilter":
            
            #print(f'acá encontró un requestfilter en key = {key}')
            filter_name = splitted_key[1]
            filter_values = request_form.getlist(key)
            #print(f'filter_values = {filter_values}')
            filter_string = f'{filter_name}={filter_values[0]}' if filter_values else ''
            if len(filter_values) > 1:
                more_filter_values = "".join([f',{value}' for value in filter_values][1:])
                filter_string = f'{filter_string}{more_filter_values}'
            request_filters.append(filter_string)
    
    return request_filters


def get_apirequest_attributes_from_requestform():
    # TODO
    pass

@dataclass
class MlItem_HtmlTableRow:

    pass

def mlitem_to_htmlrowobject(item: MlItem) -> MlItem_HtmlTableRow:
    pass

gestion_publicaciones_blueprint = Blueprint('gestion_publicaciones', __name__, template_folder="templates")

sessions: Dict = {}

items = None

@gestion_publicaciones_blueprint.route("/gestion_publicaciones.html", methods=['GET', 'POST'])
def gestion_publicaciones():
    if request.method == "GET":

        return render_template("gestion_publicaciones.html")
    
    elif request.method == "POST":
        
        # TODO: ALMACENAR CONFIGURACION DE FORM PARA PRESERVARLA EN EL RENDER DEL TEMPLATE

        # ASEGURA SESIONES PARA CADA STORE
        store_names = request.form.getlist("request_config_seller")
        
        for store_name in store_names:
            store_in_sessions = False
            for session_store in sessions.keys():
                if store_name == session_store:
                    store_in_sessions = True
                    break
            if not store_in_sessions:
                store_session = MlSession(store_name=store_name)
                sessions.update({store_name: store_session})
            
        #for store, session in sessions.items():
        #    print(store, session)


        #   TRAE LISTADO DE ITEM IDS PARA CADA TIENDA

        #   CONFIGURA REQUEST
        
        #   Arma filtros
        request_filters = get_apirequest_filters_from_requestform(request_form=request.form)
        #print(f'\n\nREQUEST_FILTERS: {request_filters}\n\n')

        #TODO   Arma atributos a traer
        #attributes = get_apirequest_attributes_from_requestform(reques_form=request.form)

        #   LISTA DE ITEMS DE TODAS LAS TIENDAS
        items = []

        # PARA CADA STORE ENVIA REQUEST Y TRAE LA INFO DE LOS ITEMS
        request_stores = request.form.getlist("request_config_seller")      #   Lista de tiendas a consultar
        
        print()
        print(f'request_stores: {request_stores}')

        for store in request_stores:

            #new_session = MlSession(store_name=store)
            #   Crea un objeto MlSellerItems
            seller_items = MlSellerItems(seller_id=getattr(MlSellerCatalog, store), filters=request_filters)
            print()
            print(f'consultando {store}')
            print(seller_items.url)

            #   Trae todos los item ids del objeto MlSellerItems
            set_all_resource_items(seller_items, sessions[store])
            print(f'publicaciones {store}: {len(seller_items.items)}')

            #TODO   Trae los detalles (atributos) de cada item
            #get_all_seller_item_details(seller_items, sessions[store], attributes)

            #TODO   Crear un objeto que represente una ROW en la tabla del html con un item

            #   Agrega lista de items de la tienda a la lista general
            items.extend(seller_items.items)

        
        print(f'\n\nTotal: {len(items)} publicaciones de {request_stores}\n\n')
        #   index items
        indexed_items = [(index + 1, item) for index, item in enumerate(items)]

        
        return render_template("gestion_publicaciones.html", items=indexed_items, items_len=len(items), form=request.form)
        


# traer_ID_publicaciones_inactivas_de_tienda
# traer detalles de publicaciones inactivas
# verificar si están en gbp
#   en base a filtro 2:
# Mostrar titulo y precio
# V1: BOTON BORRAR en cada una, y BOTON BORRAR TODAS
# V2: checkbox en cada una borrar
# Una vez que se borra, vuelve a mostrar el listado actualizado


if __name__ == "__main__":
    pass