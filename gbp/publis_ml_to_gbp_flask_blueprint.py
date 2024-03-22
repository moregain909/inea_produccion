
#   Genera una planilla de publicaciones ML para para importar en GBP

#TODO: DETECTAR VARIACIONES Y APLICARLO A LA PLANILLA
from dataclasses import dataclass
from flask import Flask, render_template, request, flash, send_file, Blueprint

import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

# Define el path al directorio raíz del proyecto.
path2root = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(path2root)

# Define el path al directorio data del proyecto.
data_dir = os.path.join(path2root, "data")
sys.path.append(data_dir)

from gbp_helpers import create_excel, get_list_id_from_desc, get_warehouse_id_from_name
from gbp_helpers import ImportPublisGBP, GbpMlItem
from gbp_helpers import listas_de_precios_gbp, depositos_gbp, tiendas_gbp


#app = Flask(__name__)
#app.secret_key = "cantina"

publis_ml_to_gbp_blueprint = Blueprint('publis_ml_to_gbp_flask_blueprint', __name__, template_folder="templates")


submited_items = []

@publis_ml_to_gbp_blueprint.route("/publis2gbp", methods=['GET', 'POST'])
def publis2gbp():
    
    # Muestra la página inicial
    if request.method == "GET":

        return render_template("publis2gbp01.html", 
                               tiendas = tiendas_gbp, 
                               listas_de_precios = listas_de_precios_gbp,
                               depositos = depositos_gbp, 
                               export = False
                               )

    # Agrega datos del formulario y exporta la planilla
    if request.method == "POST":

        # AGREGA ITEMS A LA LISTA DE ITEMS A EXPORTAR
        if "add" in request.form:

            # Valida que se ingresen los datos del item requeridos en el formulario
            if not request.form["item_id"] or not request.form["sku"]:
                flash("Para agregar una publicación se deben ingresar todos los datos requeridos (ID Publicación, SKU)")
                return render_template("publis2gbp01.html",
                                       tiendas = tiendas_gbp,
                                       listas_de_precios = listas_de_precios_gbp,
                                       depositos = depositos_gbp,
                                       items = submited_items, 
                                       export = False
                                       )

            # Crea un nuevo item para agregarlo a la lista de items a exportar
            new_item = GbpMlItem(ml_item_id=request.form["item_id"])
            new_item.sku = request.form["sku"]
            new_item.variation_id = request.form["variation_id"]
            new_item.store = request.form["tienda"]
            # Convierte  price_list_desc y warehouse_name a price_list_id y warehouse_id
            new_item.price_list = request.form["lista_precios"]
            new_item.price_list_id = get_list_id_from_desc(listas_de_precios_gbp, new_item.price_list)
            warehouse = request.form["deposito"]
            new_item.warehouse_id = get_warehouse_id_from_name(depositos_gbp, warehouse)
            
            # Valida formato de ITEM ID (agrega prefijo MLA si no lo tiene)
            new_item.format_ml_item_id()

            # Agrega el nuevo item a la lista de items a exportar
            submited_items.append(new_item)

            return render_template("publis2gbp01.html", 
                                   tiendas = tiendas_gbp, 
                                   listas_de_precios = listas_de_precios_gbp, 
                                   depositos = depositos_gbp, 
                                   items = submited_items, 
                                   export = False                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
                                   )
        
        # EXPORTA ITEMS A PLANILLA
        elif "export" in request.form:
            
            # Genera planilla
            create_excel(submited_items, spreadsheet_type = ImportPublisGBP, path_to_data_dir=data_dir)

            return send_file("../data/import_publis_gbp.xlsx", download_name="import_publis_gbp.xlsx", as_attachment=True)
        

        # BORRA ITEMS DE LA LISTA DE ITEMS A EXPORTAR
        elif "delete" in request.form:
            item_id = request.form["delete"]
            
            for item in submited_items:
                if item.ml_item_id == item_id:
                    submited_items.remove(item)
                    break
            
            return render_template("publis2gbp01.html", 
                                   tiendas = tiendas_gbp, 
                                   listas_de_precios = listas_de_precios_gbp, 
                                   depositos = depositos_gbp, 
                                   items = submited_items, 
                                   export = False                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
                                   )

        # BOTON DE TEST
        elif "test" in request.form:
            return "test"


if __name__ == "__main__":
    
    #app.run(debug= True)
    pass