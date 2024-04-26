from flask import Flask

import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))


from gbp.publis_ml_to_gbp_flask_blueprint import publis_ml_to_gbp_blueprint
from notion.tarifarios_envios_notion_blueprint import tarifarios_envios_notion_blueprint
from precios_mg.consulta_sku_al_ws_bp import sku_en_mg_blueprint
from ml.redirect_uri_bp import callbacks_ml
from ml.bp_gestion_publicaciones import gestion_publicaciones_blueprint

app = Flask(__name__)
app.secret_key = "cantina"
app.register_blueprint(publis_ml_to_gbp_blueprint)
app.register_blueprint(tarifarios_envios_notion_blueprint)
app.register_blueprint(sku_en_mg_blueprint)
app.register_blueprint(callbacks_ml)
app.register_blueprint(gestion_publicaciones_blueprint)



if __name__ == "__main__":
    
    app.run(debug= True)