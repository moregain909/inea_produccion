import json
import requests
import time

# USUARIOS Y AUTENTICACION
TIENDAS_VAL = ["tecnorium", "celestron", "lenovo", "iojan", "iojann", "test01"]


def valida_tienda(tienda, tiendas_val):
    """
    Valida que tengamos las credenciales de la tienda que se usa como argumento
 
    """
    if tienda.lower() not in tiendas_val:
        return None
    else:
        return True
    
def checkea_retira(token, item_id):

    time.sleep(0.5)
    url = "https://api.mercadolibre.com/items/"+item_id

    payload={}
    headers = {
      'Authorization': token
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    j = response.json()

    pause = 10
    try:
        if j["shipping"]["local_pick_up"]:
            #print(item_id, "tiene RETIRA EN PERSONA")
            return True
        #else:
        #    #print(item_id, "NO tiene RETIRA EN PERSONA")
        #    return False
    except KeyError as e:
        print(f'\nError al chekear {item_id}\n{type(e)}: {e}')
        #print(f'Esperando {pause} segundos\n')
        #time.sleep(pause)
        return False
    except Exception as e:
        print(f'\nError al chekear {item_id}\n{type(e)}: {e}')
        #print(f'Esperando {pause} segundos\n')
        #time.sleep(10)        
        return False

def activa_retira(token, item_id):

    PAUSA = 30

    url = "https://api.mercadolibre.com/items/"+item_id

    payload = json.dumps({
      "shipping": {
        "local_pick_up": True
      }
    })
    headers = {
      'Authorization': token,
      'Content-Type': 'application/json'
    }

    response = requests.request("PUT", url, headers=headers, data=payload)

    if response.status_code != 200:
        print(f'{item_id} Error al intentar activar RETIRA\n{response.status_code} {response.reason}')
        if response.status_code == 401:
            print(f'Error 401: token no válido. Esperando {PAUSA} segundos para seguir...')
            time.sleep(PAUSA)
        return False
    else:
        print(item_id, "agregado RETIRA EN PERSONA")
        print()
        return True
    print()