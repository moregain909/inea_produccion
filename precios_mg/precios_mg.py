#   Actualiza base de costos de productos MicroGlobal

#from dotenv import load_dotenv
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

import os, sys
path2root = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(path2root)

from precios_mg_helpers import mg_get_products, productomg2costomg, insert_costo_mg, latest_price_mg, mg_cat_xml
from precios_mg_helpers import CostoMG
from data.data_helpers import db_connection
#   Loads env db constants
from precios_mg_config import PRODUCCION_MYSQL_USER, PRODUCCION_MYSQL_PASS, PRODUCCION_MYSQL_HOST, PRODUCCION_MYSQL_PORT, PRODUCCION_DB, \
    TEST_MYSQL_USER, TEST_MYSQL_PASS, TEST_MYSQL_HOST, TEST_MYSQL_PORT, TEST_DB
from notion.notion_helpers import check_notificacion_script

#DATABASE = "test"
DATABASE = "produccion"

if __name__ == "__main__":
    

    #   Connect to db and start a session
    if DATABASE == "local":
        #   local test database
        ce = db_connection(TEST_MYSQL_USER, TEST_MYSQL_PASS, TEST_MYSQL_HOST, TEST_MYSQL_PORT, TEST_DB)
    else:
        #   remote production database
        ce = db_connection(PRODUCCION_MYSQL_USER, PRODUCCION_MYSQL_PASS, PRODUCCION_MYSQL_HOST, PRODUCCION_MYSQL_PORT, PRODUCCION_DB)
    
    connection = ce[0]
    engine = ce[1]

    Session = sessionmaker(bind=engine)
    session = Session()

    #   Get prices from MicroGlobal web service
    mg_prices = mg_get_products(mg_cat_xml(), format="prices")

    #   Compare prices with database an
    items_to_update = []
    items_to_add = []
    for mg_price in mg_prices:    
        latest_price = latest_price_mg(session, mg_price.sku)
        if latest_price: 
            latest_price.costo = float(latest_price.costo)
            if latest_price.costo != mg_price.costo:
                items_to_update.append(mg_price)
        else:
            items_to_add.append(mg_price)
 
    #   Add updated prices to database
    updated_count = 1
    for item in items_to_update:
        print(f'El precio de {item.sku} ha cambiado por {item.costo}')
        new_db_price = productomg2costomg(item)
        insert_costo_mg(session, new_db_price)
        updated_count += 1

    #   Add new prices to database
    added_count = 1
    for item in items_to_add:
        print(f'No existe el producto {item.sku} en la db. Se agrega.')
        new_db_price = productomg2costomg(item)
        insert_costo_mg(session, new_db_price)
        added_count += 1

    print(f'Actualizados {len(items_to_update)} precios de MG')
    print(f'Insertados {len(items_to_add)} precios de MG')


    connection.close()


    # TODO: Notificar por telegram cuando haya precios actualizados

    # TODO: Marcar la ejecución en monitoreo de scripts en Notion
    check_notificacion_script("Database Costos MG")


