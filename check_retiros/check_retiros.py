import requests
import time

import os, sys
path2root = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(path2root)

from retiros_helpers import valida_tienda, checkea_retira, activa_retira, TIENDAS_VAL
from auth import ml_aut
from notion import *



tiendas = ["tecnorium", "celestron", "lenovo"]

for t in tiendas:

    tienda = t
    token = ml_aut(tienda)

    tiendal = tienda.lower()

    if not valida_tienda(tiendal, TIENDAS_VAL):
        print("No se tienen credenciales de la tienda", tienda.upper(), "para autenticar en ML")
    else:
        if tiendal == "tecnorium" :            
            USER_ID = config("TEC_USER_ID")
        elif tiendal == "celestron" :            
            USER_ID = config("CEL_USER_ID")
        elif tiendal == "lenovo" :            
            USER_ID = config("LEN_USER_ID")
        elif tiendal == "test01" :            
            USER_ID = config("TEST01_USER_ID")

    paging = 0
    pag_total = 1
    count = 0
    activados = 0

    print()
    print("Buscando publicaciones que no tengan Retiro en persona activado en", tienda.upper() +"...")
    print()
    while paging <= pag_total:
        paging_str = str(paging)
        url = "https://api.mercadolibre.com/users/"+USER_ID+"/items/search?status=active&offset="+paging_str

        payload={}
        headers = {
        'Authorization': token
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code != 200:
            print(response.status_code, response.text)
        else:
            j = response.json()
            for x in j["results"]:
                count += 1
                print(x, count)
                # time.sleep(1.5)

                if not checkea_retira(token, x):
                    retries = 0
                    MAX_RETRIES = 2
                    while retries < MAX_RETRIES:
                        retries += 1
                        print(f'reintentando...')
                        token = ml_aut(tienda)
                        if checkea_retira(token, x):
                           break 
                        # time.sleep(1.5)
                    print(f'{x} no tiene RETIRA activado')
                    print(f'Activando...')
                    if not activa_retira(token, x):
                        token = ml_aut(tienda)
                    activados += 1
                    

        pag_total = j["paging"]["total"]
        paging += 50

    if activados > 0:
        print("  Actualizadas", activados, "publicaciones con Retiro en persona en", tienda.upper() +".")
    else:
        print("  Todo en orden en", tienda.upper() +".")


print()
print("Confirmando esta ejecución en Notion...")
check_notificacion_script("Retiro en persona")

time.sleep(10)