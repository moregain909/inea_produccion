#   CONFIGURATION AND CONSTANTS FOR COSTOS_ENVIO

#from dataclasses import dataclass, field, asdict
#import os
#import copy
from typing import List, Dict, Union
#from decouple import AutoConfig, config, UndefinedValueError
from dotenv import *
#import httpx
#from openpyxl import load_workbook, Workbook

from envio_helpers import Publicacion, get_items_ids

from auth import Tienda

#   CONFIGURA EN QUÉ TIENDAS BUSCA TIPOS DE ENVÍO
LISTA_TIENDAS = ["tecnorium", "lenovo"]

#   CONFIGURA QUÉ PROVEEDORES TIENEN COSTO CON ENVIO EN GBP
ALIAS_PROVEEDORES_CON_COSTO_ENVIO = ["microglobal", "bowie"]

#   CONFIGURA MAPA DE PROVEEDORES CON COSTOS DE ENVIO EN GBP Y UMBRALES
MAP_PROVEEDORES =  {"microglobal":  {"name": "MICROGLOBAL ARGENTINA SOCIEDAD",  "pid": "16", "umbrales":   {90000: 1, \
                                                                                                            1200000: 0.5}}, \
                    "bowie":        {"name": "Bowie SRL",                       "pid": "79", "umbrales":   {90000: 1, \
                                                                                                            1200000: 0.5}}}

  
#CONFIGURA DIRECTORIO DE DATA
DATA_DIR_REL_PATH = ".."
DATA_DIR_NAME = "data"

#   CONFIGURA ARCHIVO CON PUBLIS_GBP
PUBLIS_GBP_SOURCE_FILE = "Publis_GBP.xlsx"

#   CONFIGURA ARCHIVO ARTICULOS GBP EXTENDIDA
ARTICULOS_GBP_EXTENDIDA = "Articulos_GBP_extendida.xlsx"


#   CONFIGURA COEFICIENTE CALCULO ENVIO MS RESPECTO ENVIO ML
MS_SHIPMENT_MULTIPLIER  = 2


# CONFIG GBP_UPDATER_FILE

GBP_UPDATER_FILE = "actualizador_publis_gbp.xlsx"
GBP_UPDATER_FILE_TITLE_CELLS = {"A1": "ID de Publicación", "B1": "Costo de Envío"}
GBP_UPDATER_FILE_SHEET_TITLE = "Publicaciones"
GBP_UPDATER_FILE_COLUMNS_WIDTH = 18


# CONFIGURA CATALOGO DE TIPOS DE ENVIO DE ML CON SUS PRIORIDADES PARA CALCULAR EL COSTO DE ENVIO DE REFERENCIA
# Con priority >= 50 se toma directamente el costo de envío, con menos, se promedia el costo de todas las prioridades => 0
SHIPMENT_TYPES_CATALOG =    {510645: {'name': 'Estándar a domicilio',                'shipping_method_type': 'three_days',   'priority': -10}, \
                             510945: {'name': 'Estándar a sucursal de correo',       'shipping_method_type': 'three_days',   'priority': 0}, \
                             511546: {'name': 'Estándar a sucursal de correo',       'shipping_method_type': 'four_days',    'priority': 0}, \
                             504345: {'name': 'Estándar a sucursal de correo',       'shipping_method_type': 'standard',     'priority': 0}, \
                              73330: {'name': 'Express a domicilio',                 'shipping_method_type': 'express',      'priority': 100}, \
                             510545: {'name': 'Express a domicilio',                 'shipping_method_type': 'two_days',     'priority': 90}, \
                             510845: {'name': 'Express a sucursal de correo',        'shipping_method_type': 'two_days',     'priority': 0}, \
                             502845: {'name': 'Express a sucursal de correo',        'shipping_method_type': 'express',      'priority': 0}, \
                             510445: {'name': 'Prioritario a domicilio',             'shipping_method_type': 'next_day',     'priority': -10}, \
                             510745: {'name': 'Prioritario a sucursal de correo',    'shipping_method_type': 'next_day',     'priority': 0}, \
                             514245: {'name': 'Prioritario',                         'shipping_method_type': 'five_days',    'priority': -10}, \
                              73328: {'name': 'Estándar a domicilio',                'shipping_method_type': 'standard',     'priority': 60}, \
                             514345: {'name': 'Prioritario',                         'shipping_method_type': 'six_days',     'priority': 60}, \
                             514245: {'name': 'Prioritario',                         'shipping_method_type': 'five_days',    'priority': -10}, \
                              73328: {'name': 'Estándar a domicilio',                'shipping_method_type': 'standard',     'priority': 60}, \
                             514345: {'name': 'Prioritario',                         'shipping_method_type': 'six_days',     'priority': 60}, \
                             511545: {'name': 'Estándar a domicilio',                'shipping_method_type': 'four_days',    'priority': -10} }


if __name__ == '__main__':


    pass