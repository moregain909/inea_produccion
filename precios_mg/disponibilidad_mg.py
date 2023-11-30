#   Actualiza database de disponibilidadde productos MicroGlobal

#from dotenv import load_dotenv
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

import os, sys
path2root = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(path2root)

#from precios_mg_helpers import insert_costo_mg, latest_price_mg
from precios_mg_helpers import mg_get_products, mg_cat_xml, is_in_table, \
    productomg2disponibilidadstock, db_get_disponibilidad_stock, insert_disponibilidad_stock, \
    productomg2itemmg, insert_item_mg
from data.data_helpers import db_connection
#   Loads env db constants
from precios_mg_config import PRODUCCION_MYSQL_USER, PRODUCCION_MYSQL_PASS, PRODUCCION_MYSQL_HOST, PRODUCCION_MYSQL_PORT, PRODUCCION_DB, \
    TEST_MYSQL_USER, TEST_MYSQL_PASS, TEST_MYSQL_HOST, TEST_MYSQL_PORT, TEST_DB
from notion.notion_helpers import check_notificacion_script

if __name__ == "__main__":

    DATABASE = "local"

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

    #   Get products from MicroGlobal web service
    xml = mg_cat_xml()
    mg_products = mg_get_products(xml, format=None)

    #   Compares MicroGlobal web service to database
    for mg_product in mg_products:
        update_db = False

        db_product = db_get_disponibilidad_stock(session, mg_product.sku)
        
        if db_product == None:
            update_db = True

            #   Check if sku exists in productos_mg
            if not is_in_table(session, mg_product.sku):
                itemmg = productomg2itemmg(mg_product)
                insert_item_mg(session, itemmg)
                print(f'El producto {mg_product.sku} no existe en la db de productos MG. Se agrega.')
                continue

        else:
            db_availability = db_product.is_available()
            mg_availability = mg_product.is_available()
            if db_availability != mg_availability:
                update_db = True
                
        if update_db:
            new_db_product = productomg2disponibilidadstock(mg_product)
            insert_disponibilidad_stock(session, new_db_product)

    #   Closes database connection
    connection.close()

    # TODO: Notificar por telegram cuando haya precios actualizados

    #   Registra ejecución en dashboard de monitoreo de Notion
    check_notificacion_script("Database Disponibilidad Stock MG")