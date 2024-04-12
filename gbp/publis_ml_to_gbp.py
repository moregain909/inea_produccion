
#   Genera una planilla de publicaciones ML para para importar en GBP

#TODO: DETECTAR VARIACIONES Y APLICARLO A LA PLANILLA

import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

path2root = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(path2root)

data_dir = os.path.join(path2root, "data")
sys.path.append(data_dir)

from gbp_helpers import create_excel
from gbp_helpers import ImportPublisGBP, GbpMlItem

if __name__ == "__main__":

    #   Referencia listas de precios GBP:
    #   Listas de precio = {"01- ML-CLASICA": 1,
    #                      "03- ML PREMIUM": 5, 
    #                       "MG Tecnorium - Clásica": 10,
    #                       "MG Tecnorium - Premium": 12,
    #                       "MG Lenovo - Clásica": 11,
    #                       "MG Lenovo - Premium": 13"}

    tecnorium_items = [\
        GbpMlItem(ml_item_id="880340924", sku="DS2208-SR7U2100SGW", variation_id="64723225935", price_list_id=10, warehouse_id=1), \
        GbpMlItem(ml_item_id="880339686", sku="LS2208-SR20007R-UR", variation_id="174361829507", price_list_id=5, warehouse_id=1)] \
        #GbpMlItem(ml_item_id="1701835556", sku="21061", variation_id="", price_list_id=5, warehouse_id=1), \
        #GbpMlItem(ml_item_id="1701797126", sku="21049", variation_id="", price_list_id=1, warehouse_id=1), \
        #GbpMlItem(ml_item_id="1701861314", sku="JL806A", variation_id="", price_list_id=10, warehouse_id=1), \
        #GbpMlItem(ml_item_id="1414382543", sku="22994", variation_id="", price_list_id=1, warehouse_id=1), \
        #GbpMlItem(ml_item_id="1701758288", sku="22976", variation_id="", price_list_id=1, warehouse_id=1), \
        #GbpMlItem(ml_item_id="1414382635", sku="22976", variation_id="", price_list_id=5, warehouse_id=1), \
        #GbpMlItem(ml_item_id="1701758400", sku="72373", variation_id="", price_list_id=10, warehouse_id=1), \
        #GbpMlItem(ml_item_id="1701823122", sku="CBS110-8T-D-NA", variation_id="", price_list_id=10, warehouse_id=1)] \
        #GbpMlItem(ml_item_id="1664701300", sku="AS9033PI", variation_id="", price_list_id=10, warehouse_id=1) \                                                                                        
    
                        
    
    lenovo_items = [GbpMlItem(ml_item_id="1708656186", sku="21HE0015AR", variation_id="", price_list_id=11, warehouse_id=1) \
                    #GbpMlItem(ml_item_id="1613175452", sku="21EE0001AC", variation_id="", price_list_id=11, warehouse_id=1), \
                    #GbpMlItem(ml_item_id="1691539830", sku="21HR000WAR", variation_id="", price_list_id=11, warehouse_id=1), \
                    #GbpMlItem(ml_item_id="1691487678", sku="21E70004AC", variation_id="", price_list_id=11, warehouse_id=1), \
                    #GbpMlItem(ml_item_id="1692077958", sku="21CG001VAR", variation_id="", price_list_id=11, warehouse_id=1), \
                    #GbpMlItem(ml_item_id="1692077992", sku="21E4001TAR", variation_id="", price_list_id=11, warehouse_id=1), \
                    #GbpMlItem(ml_item_id="1691474982", sku="21C6001SAR", variation_id="", price_list_id=11, warehouse_id=1), \
                    #GbpMlItem(ml_item_id="1691500996", sku="20VE00L4AR/2Y", variation_id="", price_list_id=11, warehouse_id=1), \
                    #GbpMlItem(ml_item_id="1691591696", sku="21E4001UAR", variation_id="", price_list_id=11, warehouse_id=1), \
                    #GbpMlItem(ml_item_id="1691526736", sku="21EE0000AC", variation_id="", price_list_id=11, warehouse_id=1), \
                    #GbpMlItem(ml_item_id="1691475168", sku="21ECS0PU00", variation_id="", price_list_id=11, warehouse_id=1), \
                    #GbpMlItem(ml_item_id="1691526784", sku="21H2000RAR", variation_id="", price_list_id=11, warehouse_id=1) \
                    ]
    
    celestron_items = [GbpMlItem(ml_item_id="1708628996", sku="21049", variation_id="", price_list_id=5, warehouse_id=1)] \
                       #GbpMlItem(ml_item_id="1613175452", sku="31036", variation_id="", price_list_id=5, warehouse_id=1)] \
                       #GbpMlItem(ml_item_id="1675643192", sku="22007", variation_id="", price_list_id=5, warehouse_id=1), \
                       #GbpMlItem(ml_item_id="1675656248", sku="21074", variation_id="", price_list_id=5, warehouse_id=1), \
                       # GbpMlItem(ml_item_id="1410806747", sku="21063", variation_id="", price_list_id=5, warehouse_id=1) \
    

    #! CONFIG TIENDA DE LAS PUBLIS A EXPORTAR 
    #!      IMPORTAR DE A UNA TIENDA POR VEZ 
    #TODO:  O ACTUALIZAR SCRIPT PARA QUE GENERE UN EXCEL POR CADA TIENDA

    item_list = tecnorium_items

    for item in item_list:
        item.format_ml_item_id()

    create_excel(item_list, spreadsheet_type = ImportPublisGBP, path_to_data_dir=data_dir)
