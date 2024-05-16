from dataclasses import dataclass
from typing import List, Dict, Tuple

import os, sys
path2root = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(path2root)



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

    HtmlRequestFilter(name="Publicación de Catálogo", option_name="requestfilter_catalog_listing", 
        options=[HtmlRequestFilterOption(input_option_id="true", input_value="true", 
                                         input_state="", label_for="true", name="Es"), 
                HtmlRequestFilterOption(input_option_id="false", input_value="false", 
                                         input_state="", label_for="false", name="No es")
                                         ]),  

    HtmlRequestFilter(name="Elegible para Catálogo", option_name="requestfilter_tags", 
        options=[HtmlRequestFilterOption(input_option_id="catalog_listing_eligible", input_value="catalog_listing_eligible", 
                                         input_state="", label_for="catalog_listing_eligible", name="Sí")
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
                                         ])
                                        ])


head_gbp_filters = HtmlRequestControlGroup(name="Filtros GBP", filters=[
    HtmlRequestFilter(name="Está en GBP", option_name="gbpfilter_isingbp", 
        options=[HtmlRequestFilterOption(input_option_id="in_gbp", input_value="in_gbp", 
                                         input_state="checked", label_for="in_gbp", name="Sí"), 
                 HtmlRequestFilterOption(input_option_id="not_in_gbp", input_value="not_in_gbp", 
                                         input_state="checked", label_for="not_in_gbp", name="No")]), 

    HtmlRequestFilter(name="Proveedor", option_name="gbpfilter_suppliers", 
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
