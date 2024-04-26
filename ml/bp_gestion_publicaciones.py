
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

gestion_publicaciones_blueprint = Blueprint('gestion_publicaciones', __name__, template_folder="templates")

sessions: Dict = {}

items = None

@gestion_publicaciones_blueprint.route("/gestion_publicaciones.html", methods=['GET', 'POST'])
def gestion_publicaciones():
    if request.method == "GET":
        print(items)
        return render_template("gestion_publicaciones.html", items=items)
    
    elif request.method == "POST":
        
        # TODO: ALMACENAR CONFIGURACION DE FORM PARA PRESERVARLA EN EL RENDER DEL TEMPLATE

        # ASEGURA SESIONES PARA CADA STORE
        store_names = request.form.getlist("requestConfigSeller")
        
        for store_name in store_names:
            store_in_sessions = False
            for session_store in sessions.keys():
                if store_name == session_store:
                    store_in_sessions = True
                    break
            if not store_in_sessions:
                store_session = MlSession(store_name=store_name)
                sessions.update({"store_name": store_session})
            

        #   CONFIGURA REQUEST
        #   REQUEST ITEM ID: requestConfigState
        #
        print(request.form.to_dict(flat=False))
        print(request.form.keys())
        
        
        # PARA CADA STORE, ENVIA REQUEST
        # requestConfigSeller
        # requestConfigState
        # requestConfigFields

        # query
        # queryConfigIsInGbp
        # queryConfigSuppliers

        # levantar los parámetros del request
        # llamar a la api
        # generar lista de publicaciones
        return render_template("gestion_publicaciones.html", items=["item1"], form=request.form)
        


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