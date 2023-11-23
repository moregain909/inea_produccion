#   COPIA REGISTROS DE LA TABLA DE COSTOS MG LOCAL A LA TABLA DEL SERVER REMOTO

from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError
from typing import List

import os, sys
path2root = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(path2root)

#from precios_mg_helpers import mg_get_prices, productomg2costomg, insert_costo_mg, latest_price_mg
from precios_mg_helpers import CostoMG
from data.data_helpers import db_connection
#   Loads env db constants
from precios_mg_config import MYSQL_USER, MYSQL_PASS, MYSQL_HOST, MYSQL_PORT, DB, \
    LOCAL_MYSQL_USER, LOCAL_MYSQL_PASS, LOCAL_MYSQL_HOST, LOCAL_MYSQL_PORT, LOCAL_DB


def get_local_prices(local_session: Session) -> List:
    """
    Obtiene todos los productos de la base de datos local
    """
    return local_session.query(CostoMG).all()

def copy_cost(price: CostoMG) -> CostoMG:
    return CostoMG(costo_date=price.costo_date, sku=price.sku, costo=price.costo)

if __name__ == "__main__":

    #   Connects to LOCAL DB and start a local session
    local_ce = db_connection(LOCAL_MYSQL_USER, LOCAL_MYSQL_PASS, LOCAL_MYSQL_HOST, LOCAL_MYSQL_PORT, LOCAL_DB)
    local_connection = local_ce[0]
    local_engine = local_ce[1]

    Local_Session = sessionmaker(bind=local_engine)
    local_session = Local_Session()

    #   Connects to REMOTE DB and defines a remote session object
    remote_ce = db_connection(MYSQL_USER, MYSQL_PASS, MYSQL_HOST, MYSQL_PORT, DB)
    remote_connection = remote_ce[0]
    remote_engine = remote_ce[1]

    Remote_Session = sessionmaker(bind=remote_engine)

    #   Get prices from local database
    local_prices = get_local_prices(local_session)

    #   Copy prices to remote database
    for price in local_prices:
        remote_session = Remote_Session()
        remote_price = copy_cost(price)
        try:
            remote_session.add(remote_price)
            print(f'Insertando {remote_price}')
            remote_session.commit()
            
        except IntegrityError as e:
            print(f'Registro duplicado: {price}')
            remote_session.rollback()
            
        except Exception as e:
            print(f'Error.. {e}')
            remote_session.rollback()
            
    #   Close sessions
    remote_session.close()
    local_session.close()