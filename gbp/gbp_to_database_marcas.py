#   Updates gbpseveraltables table based on GBP spreadsheet

from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
import logging

import os, sys
path2root = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(path2root)

#from gbp_helpers import 
from data.data_helpers import create_tables, db_connection
from data.data_helpers import Database, GbpSeveralTables_DbItem
from gbp_helpers import ExcelMarcasGbp


if __name__ == "__main__":
    
    database = Database(db_location = "desarrollo")

    #   Create database session
    Session = sessionmaker(bind=database.engine)
    session = Session()    


    # ! Descomentar para crear tablas nuevas que se hayan definido
    #create_tables(database.engine) 


    # Retrieves listasprecios from spreadsheet
    marcas_gbp = ExcelMarcasGbp()
    marcas_gbp.get_data(filename = "gbp_marcas.xlsx")

    # Inserts into gbp_several_tables table the listas_precios the items that aren't present already
    for marca_gbp in marcas_gbp.items:
        marca_db = GbpSeveralTables_DbItem()
        marca_db.get_data_from_gbp_item(marca_gbp)
        logging.debug(f'marca_db: {marca_db}')

        if not marca_db.is_on_db(session):
            logging.info(f'Insertando en la base de datos {marca_db.gbp_table} | {marca_db.gbp_id} | {marca_db.name}')
            marca_db.insert_into_db(session)
    
        
    database.connection.close()