#   Actualiza database de catálogo de productos MicroGlobal

#from dotenv import load_dotenv
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

import os, sys
path2root = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(path2root)

#from precios_mg_helpers import insert_costo_mg, latest_price_mg
from precios_mg_helpers import mg_get_products, mg_cat_xml, productomg2itemmg, \
    insert_item_mg, update_item_mg, is_in_table, same_as_in_table
from data.data_helpers import db_connection
#   Loads env db constants
from precios_mg_config import PRODUCCION_MYSQL_USER, PRODUCCION_MYSQL_PASS, PRODUCCION_MYSQL_HOST, PRODUCCION_MYSQL_PORT, PRODUCCION_DB, \
    TEST_MYSQL_USER, TEST_MYSQL_PASS, TEST_MYSQL_HOST, TEST_MYSQL_PORT, TEST_DB


if __name__ == "__main__":

<<<<<<< HEAD
    DATABASE = "NO_local"
=======
    DATABASE = "local"
>>>>>>> 007c6631436270590ec033db6e53206ea9d99a80

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
    #   Makes lists with products to add and to update

    items_to_update = []
    items_to_add = []
    for mg_product in mg_products:
        if not is_in_table(session, mg_product.sku):
            items_to_add.append(mg_product)
        else:
            if not same_as_in_table(session, mg_product):
                items_to_update.append(mg_product)


    #   If a product is not in the database, it is added. 
    added = 0
    for item in items_to_add:
        #print(f'No existe el producto {item.sku} en la db. Se agrega.')
        new_db_item  = productomg2itemmg(item)
        if insert_item_mg(session, new_db_item):
            added += 1
    
    add_errors = len(items_to_add) - added
    print(f'Insertados {added} productos de MG')
    if add_errors > 0:
        print(f'No se pudieron insertar {len(add_errors)} productos de MG')
    

    #   If a product is different from the one in the database, it is updated.
    modified = 0
    for item in items_to_update:
        #print(f'Existe el producto {item.sku} en la db. Se actualiza.')
        new_db_item = productomg2itemmg(item)
        if update_item_mg(session, new_db_item):
            modified += 1

    modified_errors = len(items_to_update) - modified
    print(f'Actualizados {modified} productos de MG')
    if modified_errors > 0:
        print(f'No se pudieron actualizar {len(modified_errors)} productos de MG')

    #   Closes database connection
    connection.close()