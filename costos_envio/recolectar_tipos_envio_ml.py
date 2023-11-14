from typing import List, Dict, Union
#from decouple import AutoConfig, config, UndefinedValueError
from dotenv import *
#import httpx
#from openpyxl import load_workbook, Workbook

from envio_helpers import Publicacion, get_items_ids

from auth import Tienda
from auth import ml_aut

from envio_config import LISTA_TIENDAS, SHIPMENT_TYPES_CATALOG


def main():
    #   RECOLECTA NUEVOS TIPOS DE ENVIO DE ML QUE NO ESTÉN CATALOGADOS EN SHIPMENT_TYPES_CATALOG
    # SCRIPT PARA IDENTIFICAR TIPOS DE ENVIO DE ML
    # Los tipos de envío catalogados hasta el momento se configuran en SHIPMENT_TYPES_CATALOG. 
    # El script reporta los tipos de envío que no estén catalogados.

    new_shipment_types = {}

    #   GENERA TOKENS Y CLIENTS PARA CADA TIENDA
    #   convierte lista de tiendas en diccionario con credenciales con formato {tienda: Tienda()}
    tiendas = {t: Tienda(name=t) for t in LISTA_TIENDAS}
    
    #   releva opciones de envío de cada publicación de cada tienda
    for v in tiendas.values():

        #   trae listado de ids de publicaciones de la tienda
        publis_tienda = get_items_ids(store=v.name, token=v.token, client=v.client)

        #   trae opciones de envío de cada publicación de la tienda
        for pt in publis_tienda:
            print(v.name, pt)
            publi = Publicacion(item_id=pt)
            shipment_options_json = publi.get_item_shipment_options_json(token=v.token, client=v.client)
            publi.shipment_options = publi.get_item_free_shipment_options(shipment_options_json, include_prices=True, shipment_types_catalog=SHIPMENT_TYPES_CATALOG)

            precio_referencia = publi.reference_ml_shipment_cost()

            # Si la publicación tiene un tipo de envío no catalogado, compara su costo contra el costo de referencia para asignarle prioridad y lo agrega al dict new_shipment_types
            if publi.shipment_options:
                for so in publi.shipment_options:
                    if so.shipping_method_id not in SHIPMENT_TYPES_CATALOG.keys():
                        if so.shipping_method_id not in new_shipment_types.keys():
                            
                            if so.price == precio_referencia:
                                so.shipping_method_type_priority = 60
                            else:
                                so.shipping_method_type_priority = -10
                            new_shipment_types.update({so.shipping_method_id: {'name': so.name, 'shipping_method_type': so.shipping_method_type, 'priority': so.shipping_method_type_priority}})
                            print(f'Agregado este nuevo shipment type: {so.shipping_method_id} - {so.price} - {so.name} - {so.shipping_method_type} - {so.shipping_method_type_priority} / Precio referencia: {precio_referencia}')
                print()
                
        #   Si new_shipment_types tiene contenido, imprimirlo
    if new_shipment_types != {}:
        print(new_shipment_types)        

if __name__ == '__main__':
    main()