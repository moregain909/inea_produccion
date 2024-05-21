#   Updates bbpseveraltables database table based on GBP spreadsheet

from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
import logging

import os, sys
path2root = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(path2root)

#from gbp_helpers import 
from data.data_helpers import create_tables, db_connection
from data.data_helpers import Database, GbpSeveralTables_DbItem
from gbp_helpers import ExcelListasPreciosGbp


if __name__ == "__main__":
    
    database = Database(db_location = "desarrollo")

    #   Create database session
    Session = sessionmaker(bind=database.engine)
    session = Session()    


    # ! Descomentar para crear tablas nuevas que se hayan definido
    #create_tables(database.engine) 


    # Retrieves listasprecios from spreadsheet
    listas_precios_gbp = ExcelListasPreciosGbp()
    listas_precios_gbp.get_data(filename = "gbp_listasprecios.xlsx")

    # Inserts into gbp_several_tables table the listas_precios the items that aren't present already
    for lista_gbp in listas_precios_gbp.items:
        lista_db = GbpSeveralTables_DbItem()
        lista_db.get_data_from_gbp_item(lista_gbp)

        if not lista_db.is_on_db(session):
            logging.info(f'Insertando en la base de datos {lista_db.gbp_table} | {lista_db.gbp_id} | {lista_db.name}')
            lista_db.insert_into_db(session)
    
        
    database.connection.close()