
# BUSCA PUBLICACIONES INACTIVAS EN ML

# DE LAS QUE NO ESTÁN EN GBP:
#   MUESTRA TITULO Y PRECIO
#   PERMITE SELECCIONAR PARA BORRAR

# DE LAS QUE ESTAN EN GBP:
#   MUESTRA TITULO, PRECIO Y PROVEEDOR
#   PERMITE SELECCIONAR PARA BORRAR

from dataclasses import dataclass
from flask import Flask, render_template, request, flash, send_file, Blueprint
import logging
from typing import List, Dict, Tuple

import os, sys
path2root = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(path2root)

from auth import MlSession
from ml.ml_helpers_api_resources import set_all_resource_items, MlSellerItems, MlSellerCatalog, get_all_seller_item_details, MlItem
from ml.config_gestion_publicaciones import head_filters, head_gbp_filters, head_fields, HtmlRequestFilter, HtmlRequestFilterOption, HtmlRequestControlGroup


logging.basicConfig(level=logging.DEBUG)

def get_filters_from_requestform(request_form, filter) -> List[str]:

    form_keys = list(request_form.keys())
    #print(f'{form_keys}')
    # Detecta qué filtros están presentes en el form
    request_filters = []
    for key in form_keys:
        splitted_key = key.split("_", 1)     # detecta si la key del form tiene prefijo de filtro (requestfilter)
        if splitted_key[0] == filter:
            
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


def get_checked_options(option_name: str) -> List[str]:
    """ Get checked options from request form.
    :param option_name: name of the form field
    :return: list of checked options
    """

    checked_options = request.form.getlist(option_name)
    if 'item_ml_id' in checked_options:
        checked_options.remove("item_ml_id")        # remueve el ID que ya lo trae por default
    
    return checked_options


def check_options(filter: HtmlRequestFilter, checked_options: List[str]):
    """ stores checked options to retrieve them in html
    """
    for option in filter.options:
        if option.input_option_id in checked_options:
            option.input_state = "checked"
        #elif option.input_state != "disabled" or option.input_option_id != "item_ml_id":
        elif option.input_state != "disabled" and option.input_option_id != "item_ml_id":
            option.input_state = ""
    return True    
    

def request_attributes_to_column_names(request_fields: HtmlRequestFilter, attributes: List[str]) -> Tuple:

    column_names = ['#', 'ID ML']
    for attribute in attributes:
        for field in request_fields.options:
            if field.input_option_id == attribute:
                column_names.append(field.name)
    column_names_tuple = tuple(column_names)
    # print(f'column_names_tuple = {column_names_tuple}')
    return column_names_tuple


def item_list_to_item_row_list(item_list: List[MlItem], attributes: List[str]) -> Tuple:
    """ Convert a list of MlItems to a list of MlItemRows for html
    """

    row_list = []
    for index, item in enumerate(item_list):
        row_field_list = []
        row_field_list.append(index + 1)

        # ML Item ID con link a la edición del item en ML
        ml_id_link = f'https://www.mercadolibre.com.ar/syi/core/modify?itemId={item.ml_id}'
        ml_id_row = f'<a href="{ml_id_link}" target="_blank">{item.ml_id}</a>'
        row_field_list.append(ml_id_row)

        for attribute in attributes:
            ml_link = ''
            
            # Procesa thumbnail
            if attribute == 'thumbnail':
                thumb_link = getattr(item, attribute, "")
                attribute_value = f'<img src="{thumb_link}" alt="..." class="img-thumbnail">'
            
            # Procesa permalink
            elif attribute == 'permalink':
                ml_link = getattr(item, attribute, "")
                attribute_value = f'<a href="{ml_link}" target="_blank">ver</a>'

            # Procesa precio
            elif attribute == 'price':
                price = getattr(item, attribute, "")
                attribute_value = f'$ {price:,.2f}'

            # Procesa channels
            elif attribute == 'channels':
                channels_catalog = {'marketplace': 'ml', 'mshops': 'ms'}
                channels = getattr(item, attribute, "")
                attribute_value = ''
                for channel in channels:
                    attribute_value += f'<small>{channels_catalog[channel]}</small><br>'

            # Procesa listing type
            elif attribute == 'listing_type_id':
                listing_type_catalog = {'gold_special': 'clásica', 'gold_pro': 'premium'}
                listing_type = getattr(item, attribute, "")
                attribute_value = listing_type_catalog[listing_type]

            # Procesa variations
            elif attribute == 'variations':
                variations = getattr(item, attribute, "")
                attribute_value = ''
                for variation in variations:
                    # Arma string con nombre y valor del attributo 
                    combinations = ''.join([f'{combination.name} {combination.value}' for combination in variation.attribute_combinations])
                    
                    # Arma string para html incluyendo stock positivo de variaciones si hay más de una variación
                    if len(variations) > 1 and variation.available_quantity is not None:
                        attribute_value += f'<small>{variation.variation_id} - {combinations} cant. {variation.available_quantity}</small><br>'
                    else:
                        attribute_value += f'<small>{variation.variation_id} - {combinations}</small><br>'

            else:
                attribute_value = getattr(item, attribute, "")
            row_field_list.append(attribute_value)
        row_field_tuple = tuple(row_field_list)
        row_list.append(row_field_tuple)
        # print(f'convirtiendo item a row tuple: {row_field_tuple}')
    return row_list



#   Otros posibles filtros: flex, retiro, garantía
#   Otros campos: variación (id, sku, atributos, costo envío promedio

gestion_publicaciones_blueprint = Blueprint('gestion_publicaciones', __name__, template_folder="templates")

sessions: Dict = {}

items = None

@gestion_publicaciones_blueprint.route("/gestion_publicaciones", methods=['GET', 'POST'])
def gestion_publicaciones():
    if request.method == "GET":

        return render_template("gestion_publicaciones.html", head_filters=head_filters, head_gbp_filters=head_gbp_filters, head_fields=head_fields)
    
    elif request.method == "POST":
        
        # ASEGURA SESIONES PARA CADA STORE #! ESTA ROMPIENDO CUANDO CADUCA EL TOKEN... SI RESETEO EL SERVER AUTENTICA BIEN
        store_names = request.form.getlist("request_config_seller")
        
        for store_name in store_names:
            store_in_sessions = False
            for session_store in sessions.keys():
                if store_name == session_store:
                    if sessions[store_name].is_active:
                        print()
                        print(f'TOKEN ACTIVO - self expiration: {sessions[store_name].expiration})')
                        print()
                        store_in_sessions = True
                        break
                    print(f'\nEL TOKEN NO VALIDÓ is_active.\nAcá debería gestionar un nuevo token? - Expiration {sessions[store_name].expiration}')
            if not store_in_sessions:
                store_session = MlSession(store_name=store_name, get_expiration=True)
                sessions.update({store_name: store_session})
            

        #   TRAE LISTADO DE ITEM IDS PARA CADA TIENDA

        #   CONFIGURA REQUEST A API DE ML
        
        #   Arma filtros
        request_filters = get_filters_from_requestform(request_form=request.form, filter='requestfilter')
        #print(f'\n\nREQUEST_FILTERS: {request_filters}\n\n')

        #Arma atributos a traer
        attributes = get_checked_options("requestattribute")

        #   LISTA DE ITEMS DE TODAS LAS TIENDAS
        items = []

        # PARA CADA STORE ENVIA REQUEST Y TRAE LA INFO DE LOS ITEMS
        request_stores = request.form.getlist("request_config_seller")      #   Lista de tiendas a consultar
        
        #print()
        #print(f'request_stores: {request_stores}')

        for store in request_stores:

            #   Crea un objeto MlSellerItems
            seller_items = MlSellerItems(seller_id=getattr(MlSellerCatalog, store), filters=request_filters)
            print()
            print(f'consultando {store}')
            print(seller_items.url)

            #   Trae todos los item ids del objeto MlSellerItems
            set_all_resource_items(seller_items, sessions[store])
            print(f'publicaciones {store}: {len(seller_items.items)}')

            #   Trae los detalles (atributos) de cada item en seller_items
            get_all_seller_item_details(seller_items, sessions[store], attributes)


            #   Agrega lista de items de la tienda a la lista general
            items.extend(seller_items.items)


        # PROCESA FILTROS GBP

        # Configura filtros GBP con selecciones hechas para próximos renders
        
        for filter in head_gbp_filters.filters:
            checked_gbp_filter_options = get_checked_options(filter.option_name)
        
            for option in filter.options:
                if option.input_option_id in checked_gbp_filter_options:
                    option.input_state = 'checked'
                elif option.input_state != 'disabled':
                    option.input_state = ''

        # FILTRA POR CONDICIONES DE GBP
        # Está en GBP, Proveedor, etc...

        #TODO: LEVANTA FILTROS GBP
        gbp_attributes_to_get = get_filters_from_requestform(request_form=request.form, filter='gbpfilter')
        print(f'\nGBP ATTRIBUTES TO GET: {gbp_attributes_to_get}\n')

        #TODO: HACE QUERY (a EXCEL o DATABASE)

        #   Arma lista de publicaciones en GBP
        publis_gbp = [] # Lista de GbpMlItem

        
        #TODO: FILTRA ITEMS POR CONDICIONES DE GBP
        

        # ARMA TABLA PARA HTML
        item_columns = request_attributes_to_column_names(head_fields, attributes)
        item_rows = item_list_to_item_row_list(items, attributes)

        # Configura filtros con selecciones hechas para próximos renders
        
        for filter in head_filters.filters:
            checked_filter_options = get_checked_options(filter.option_name)
        
            for option in filter.options:
                if option.input_option_id in checked_filter_options:
                    option.input_state = 'checked'
                elif option.input_state != 'disabled':
                    option.input_state = ''

        

        # Configura campos con selecciones hechas
        check_options(head_fields, attributes)

        return render_template("gestion_publicaciones.html", head_filters=head_filters, head_gbp_filters=head_gbp_filters, head_fields=head_fields, item_columns= item_columns, items=item_rows, items_len=len(items), form=request.form)
        


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