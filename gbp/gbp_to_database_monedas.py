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
from gbp_helpers import ExcelMonedasGbp


if __name__ == "__main__":
    
    database = Database(db_location = "desarrollo")

    #   Create database session
    Session = sessionmaker(bind=database.engine)
    session = Session()    


    # ! Descomentar para crear tablas nuevas que se hayan definido
    #create_tables(database.engine) 


    # Retrieves listasprecios from spreadsheet
    monedas_gbp = ExcelMonedasGbp()
    monedas_gbp.get_data(filename = "gbp_monedas.xlsx")

    # Inserts into gbp_several_tables table the listas_precios the items that aren't present already
    for moneda_gbp in monedas_gbp.items:
        moneda_db = GbpSeveralTables_DbItem()
        moneda_db.get_data_from_gbp_item(moneda_gbp)
        logging.debug(f'moneda_db: {moneda_db}')

        if not moneda_db.is_on_db(session):
            logging.info(f'Insertando en la base de datos {moneda_db.gbp_table} | {moneda_db.gbp_id} | {moneda_db.name}')
            moneda_db.insert_into_db(session)
    
        
    database.connection.close()