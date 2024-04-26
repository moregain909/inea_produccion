
# BUSCA PUBLICACIONES INACTIVAS EN ML

# DE LAS QUE NO ESTÁN EN GBP:
#   MUESTRA TITULO Y PRECIO
#   PERMITE SELECCIONAR PARA BORRAR

# DE LAS QUE ESTAN EN GBP:
#   MUESTRA TITULO, PRECIO Y PROVEEDOR
#   PERMITE SELECCIONAR PARA BORRAR

from flask import Flask, render_template, request, flash, send_file, Blueprint
import logging

import os, sys
path2root = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(path2root)

from auth import MlSession

gestion_publicaciones_blueprint = Blueprint('gestion_publicaciones', __name__, template_folder="templates")

tiendas = ["tecnorium", "lenovo"]

session = MlSession(store_name="tecnorium")

@gestion_publicaciones_blueprint.route("/gestion_publicaciones.html", methods=['GET', 'POST'])
def gestion_publicaciones():
    return render_template("gestion_publicaciones.html", items=["item1"])

# WEB: 
# Filtro: Selección de tienda
# Filtro: Estado publicaciones
# Filtro: Está en GBP / No está en GBP
# Filtro: Proveedor
# Otros posibles filtros: tipo publicación, flex, retiro, garantía
# Selección de campos a traer con checkbox
# Botón TRAER PUBLICACIONES


# traer_ID_publicaciones_inactivas_de_tienda
# traer detalles de publicaciones inactivas
# verificar si están en gbp
#   en base a filtro 2:
# Mostrar titulo y precio
# V1: BOTON BORRAR en cada una, y BOTON BORRAR TODAS
# V2: checkbox en cada una borrar
# Una vez que se borra, vuelve a mostrar el listado actualizado
