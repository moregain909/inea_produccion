
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


@dataclass
class HtmlRequestFilterOption:

    input_option_id: str        
    input_value: str
    input_state: str      # checked, disabled, etc
    label_for: str      
    name: str
    input_class: str = 'form-check-input'     # class="form-check-input"
    input_type: str = 'checkbox'              # radio, checkbox, etc
    label_class: str = 'form-check-label'     # class="form-check-label"

    pass

@dataclass
class HtmlRequestFilter:

    name: str
    option_name: str
    options: List[HtmlRequestFilterOption]
    pass

@dataclass
class HtmlRequestControlGroup:
    
    name: str
    filters: List[HtmlRequestFilter]



head_filters = HtmlRequestControlGroup(name="Filtros", filters=[
    HtmlRequestFilter(name="Tienda", option_name="request_config_seller", 
        options=[HtmlRequestFilterOption(input_option_id="tecnorium", input_value="tecnorium", 
                                          input_state="", label_for="tecnorium", name="Tecnorium"), 
                 HtmlRequestFilterOption(input_option_id="celestron", input_value="celestron", 
                                          input_state="", label_for="celestron", name="Celestron"), 
                 HtmlRequestFilterOption(input_option_id="lenovo", input_value="lenovo", 
                                          input_state="checked", label_for="lenovo", name="Lenovo")
                                          ]),
    HtmlRequestFilter(name="Estado", option_name="requestfilter_status", 
        options=[HtmlRequestFilterOption(input_option_id="active", input_value="active", 
                                         input_state="checked", label_for="active", name="Activas"), 
                 HtmlRequestFilterOption(input_option_id="paused", input_value="paused", 
                                         input_state="", label_for="paused", name="Pausadas"),
                 HtmlRequestFilterOption(input_option_id="closed", input_value="closed", 
                                         input_state="", label_for="closed", name="Inactivas")
                                         ]),
    HtmlRequestFilter(name="Tipo", option_name="requestfilter_listing_type_id", 
        options=[HtmlRequestFilterOption(input_option_id="gold_pro", input_value="gold_pro", 
                                         input_state="checked", label_for="gold_pro", name="Premium"), 
                 HtmlRequestFilterOption(input_option_id="gold_special", input_value="gold_special", 
                                         input_state="checked", label_for="gold_special", name="Clásica")
                                         ]),
    HtmlRequestFilter(name="Flex", option_name="requestfilter_shipping_tags", 
        options=[HtmlRequestFilterOption(input_option_id="self_service_in", input_value="self_service_in", 
                                         input_state="", label_for="self_service_in", name="Tiene"), 
                 HtmlRequestFilterOption(input_option_id="self_service_out", input_value="self_service_out", 
                                         input_state="", label_for="self_service_out", name="No Tiene")
                                         ]),
    HtmlRequestFilter(name="Mercado Envíos", option_name="requestfilter_labels", 
        options=[HtmlRequestFilterOption(input_option_id="with_mercadolibre_envios", input_value="with_mercadolibre_envios", 
                                         input_state="", label_for="with_mercadolibre_envios", name="Tiene"), 
                 HtmlRequestFilterOption(input_option_id="without_mercadolibre_envios", input_value="without_mercadolibre_envios", 
                                         input_state="", label_for="without_mercadolibre_envios", name="No Tiene")
                                         ]), 
    HtmlRequestFilter(name="Envío Gratis", option_name="requestfilter_labels", 
        options=[HtmlRequestFilterOption(input_option_id="with_free_shipping", input_value="with_free_shipping", 
                                         input_state="", label_for="with_free_shipping", name="Tiene"), 
                 HtmlRequestFilterOption(input_option_id="without_free_shipping", input_value="without_free_shipping", 
                                         input_state="", label_for="without_free_shipping", name="No Tiene")
                                         ]),                                         

    HtmlRequestFilter(name="Sin Mercado Envíos", option_name="requestfilter_shipping_tags", 
        options=[HtmlRequestFilterOption(input_option_id="is_flammable", input_value="is_flammable", 
                                         input_state="", label_for="is_flammable", name="Inflamable"), 
                HtmlRequestFilterOption(input_option_id="lost_me2_by_dimensions", input_value="lost_me2_by_dimensions", 
                                         input_state="", label_for="lost_me2_by_dimensions", name="Dimensiones excedidas")
                                         ]),      

    HtmlRequestFilter(name="Control de Calidad", option_name="requestfilter_labels", 
        options=[HtmlRequestFilterOption(input_option_id="with_low_quality_image", input_value="with_low_quality_image", 
                                         input_state="", label_for="with_low_quality_image", name="Foto de baja calidad"), 
                 HtmlRequestFilterOption(input_option_id="being_reviewed", input_value="being_reviewed", 
                                         input_state="", label_for="being_reviewed", name="Bajo revisión"), 
                 HtmlRequestFilterOption(input_option_id="fix_required", input_value="fix_required", 
                                         input_state="", label_for="fix_required", name="Requiere corrección"), 
                 HtmlRequestFilterOption(input_option_id="incomplete_technical_specs", input_value="incomplete_technical_specs", 
                                         input_state="", label_for="incomplete_technical_specs", name="Ficha técnica incompleta"), 
                 HtmlRequestFilterOption(input_option_id="suspended", input_value="suspended", 
                                         input_state="", label_for="suspended", name="Suspendida"), 
                 HtmlRequestFilterOption(input_option_id="cancelled", input_value="cancelled", 
                                         input_state="", label_for="cancelled", name="Cancelada")                                         
                                         ]),

    HtmlRequestFilter(name="Ventas", option_name="requestfilter_labels", 
        options=[HtmlRequestFilterOption(input_option_id="with_bids", input_value="with_bids", 
                                         input_state="", label_for="with_bids", name="Con ventas"), 
                 HtmlRequestFilterOption(input_option_id="without_bids", input_value="without_bids", 
                                         input_state="", label_for="without_bids", name="Sin ventas")
                                        ]),

    HtmlRequestFilter(name="Stock", option_name="requestfilter_labels", 
        options=[HtmlRequestFilterOption(input_option_id="few_available", input_value="few_available", 
                                         input_state="", label_for="few_available", name="Poco stock"), 
                 HtmlRequestFilterOption(input_option_id="without_stock", input_value="without_stock", 
                                         input_state="", label_for="without_stock", name="Sin stock")                                         
                                         ]),

    HtmlRequestFilter(name="Está en GBP", option_name="queryConfigIsInGbp", 
        options=[HtmlRequestFilterOption(input_option_id="in_gbp", input_value="in_gbp", 
                                         input_state="checked", label_for="in_gbp", name="Sí"), 
                 HtmlRequestFilterOption(input_option_id="not_in_gbp", input_value="not_in_gbp", 
                                         input_state="checked", label_for="not_in_gbp", name="No")]), 

    HtmlRequestFilter(name="Proveedor", option_name="queryConfigSuppliers", 
        options=[HtmlRequestFilterOption(input_option_id="microglobal", input_value="microglobal", 
                                         input_state="checked", label_for="microglobal", name="Microglobal"), 
                 HtmlRequestFilterOption(input_option_id="goldmund", input_value="goldmund", 
                                         input_state="", label_for="goldmund", name="Goldmund"), 
                 HtmlRequestFilterOption(input_option_id="liliana", input_value="liliana", 
                                           input_state="", label_for="liliana", name="Liliana"),
                 HtmlRequestFilterOption(input_option_id="goris", input_value="goris", 
                                           input_state="", label_for="goris", name="Goris"),
                 HtmlRequestFilterOption(input_option_id="bowie", input_value="bowie", 
                                           input_state="", label_for="bowie", name="Bowie")
                                           ])
                                           ])

head_fields = HtmlRequestFilter(name="Campos", option_name="requestattribute", 
        options=[HtmlRequestFilterOption(input_option_id="item_ml_id", input_value="item_ml_id", 
                                         input_state="checked", label_for="item_ml_id", name="ID ML"), 
                HtmlRequestFilterOption(input_option_id="thumbnail", input_value="thumbnail", 
                                         input_state="", label_for="thumbnail", name="Foto"),                                         
                 HtmlRequestFilterOption(input_option_id="sku", input_value="sku", 
                                         input_state="disabled", label_for="sku", name="SKU"),                                           
                 HtmlRequestFilterOption(input_option_id="available_quantity", input_value="available_quantity", 
                                         input_state="", label_for="available_quantity", name="Stock"),
                 HtmlRequestFilterOption(input_option_id="price", input_value="price", 
                                         input_state="", label_for="price", name="Precio"),
                 HtmlRequestFilterOption(input_option_id="listing_type_id", input_value="listing_type_id", 
                                         input_state="", label_for="listing_type_id", name="Tipo Publicación"),
                 HtmlRequestFilterOption(input_option_id="status", input_value="status", 
                                         input_state="", label_for="status", name="Estado"), 
                 HtmlRequestFilterOption(input_option_id="channels", input_value="channels", 
                                         input_state="", label_for="channels", name="Canales"),
                 HtmlRequestFilterOption(input_option_id="permalink", input_value="permalink", 
                                         input_state="", label_for="permalink", name="Link"),
                 HtmlRequestFilterOption(input_option_id="variations", input_value="variations", 
                                         input_state="", label_for="variations", name="Variaciones"), 
                 HtmlRequestFilterOption(input_option_id="title", input_value="title", 
                                         input_state="checked", label_for="title", name="Título")
                                         ])

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

        return render_template("gestion_publicaciones.html", head_filters=head_filters, head_fields=head_fields)
    
    elif request.method == "POST":
        
        # TODO: ALMACENAR CONFIGURACION DE FORM PARA PRESERVARLA EN EL RENDER DEL TEMPLATE

        # ASEGURA SESIONES PARA CADA STORE
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
            if not store_in_sessions:
                store_session = MlSession(store_name=store_name, get_expiration=True)
                sessions.update({store_name: store_session})
            

        #   TRAE LISTADO DE ITEM IDS PARA CADA TIENDA

        #   CONFIGURA REQUEST
        
        #   Arma filtros
        request_filters = get_apirequest_filters_from_requestform(request_form=request.form)
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

        
        print(f'\n\nTotal: {len(items)} publicaciones de {request_stores}\n\n')
        #   index items
        indexed_items = [(index + 1, item) for index, item in enumerate(items)]
        #attributes = get_checked_options("requestattribute")
        print(request.form.to_dict(flat=False))
        print()
        print(f'Acá traemos las opciones chekeadas: {attributes}')
        print()
        item_columns = request_attributes_to_column_names(head_fields, attributes)
        item_rows = item_list_to_item_row_list(items, attributes)

        # Configura filtros con selecciones hechas
        
        for filter in head_filters.filters:
            checked_filter_options = get_checked_options(filter.option_name)
        
            for option in filter.options:
                if option.input_option_id in checked_filter_options:
                    option.input_state = 'checked'
                elif option.input_state != 'disabled':
                    option.input_state = ''

        

        # Configura campos con selecciones hechas
        check_options(head_fields, attributes)

        return render_template("gestion_publicaciones.html", head_filters=head_filters, head_fields=head_fields, item_columns= item_columns, items=item_rows, items_len=len(items), form=request.form)
        


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