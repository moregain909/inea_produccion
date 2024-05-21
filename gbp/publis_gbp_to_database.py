#   Updates GBP database tables based on GBP spreadsheets

from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
import logging

import os, sys
path2root = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(path2root)

#from gbp_helpers import 
from data.data_helpers import create_tables, db_connection
from data.data_helpers import Database, GbpSkuMlItem
from gbp_helpers import ExcelPublisGbp


if __name__ == "__main__":
    
    database = Database(db_location = "desarrollo")

    #   Create database session
    Session = sessionmaker(bind=database.engine)
    session = Session()    


    # ! Descomentar para crear tablas nuevas que se hayan definido
    #create_tables(database.engine) 


    # Retrieves publis ML from spreadsheet
    publis_gbp = ExcelPublisGbp()
    publis_gbp.get_data(filename = "Publis_GBP.xlsx")
    

    # Inserts into gbp_sku_ml_item database table the items that aren't present already
    for publi_gbp in publis_gbp.items:
        publi_db = GbpSkuMlItem()
        publi_db.get_data_from_gbp_item(publi_gbp)
        
        if not publi_db.is_on_db(session):
            logging.info(f'Insertando en la base de datos {publi_db}')
            publi_db.insert_into_db(session)


    # Inserts into gbp_ml_items database table the items that aren't present already
        
        
    database.connection.close()