from flask import Flask

import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))


from gbp.publis_ml_to_gbp_flask_blueprint import publis_ml_to_gbp_blueprint
from notion.tarifarios_envios_notion_blueprint import tarifarios_envios_notion_blueprint

app = Flask(__name__)
app.secret_key = "cantina"
app.register_blueprint(publis_ml_to_gbp_blueprint)
app.register_blueprint(tarifarios_envios_notion_blueprint)
#app.register_blueprint(blueprint_example)


if __name__ == "__main__":
    
    app.run(debug= True)