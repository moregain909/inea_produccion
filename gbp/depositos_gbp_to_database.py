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
from gbp_helpers import ExcelDepositosGbp


if __name__ == "__main__":
    
    database = Database(db_location = "desarrollo")

    #   Create database session
    Session = sessionmaker(bind=database.engine)
    session = Session()    


    # ! Descomentar para crear tablas nuevas que se hayan definido
    #create_tables(database.engine) 


    # Retrieves listasprecios from spreadsheet
    depositos_gbp = ExcelDepositosGbp()
    depositos_gbp.get_data(filename = "gbp_depositos.xlsx")

    # Inserts into gbp_several_tables table the listas_precios the items that aren't present already
    for deposito_gbp in depositos_gbp.items:
        deposito_db = GbpSeveralTables_DbItem()
        deposito_db.get_data_from_gbp_item(deposito_gbp)
        #logging.debug(f'deposito_db: {deposito_db}')

        if not deposito_db.is_on_db(session):
            logging.info(f'Insertando en la base de datos {deposito_db.gbp_table} | {deposito_db.gbp_id} | {deposito_db.name}')
            deposito_db.insert_into_db(session)
    
        
    database.connection.close()