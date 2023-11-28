import requests 
import json
from decouple import config


from dataclasses import dataclass

class NotionPage:
    pass

class NotionProperty:
    pass

class NotionDB:
    pass

@dataclass
class TarifarioNotion:
    pass

def notion_token(integracion = "pruebas api"):
    # PRUEBA_01_NOTION_TOKEN
    int = integracion.lower()
    token = ""
    if int == "pruebas api":            
        token = config("PRUEBA_01_NOTION_TOKEN")
    elif int == "qatar":
        token = config("QATAR_NOTION_TOKEN")
    return token 

def check_notificacion_script(script):

    paginas = [{"script": "Precios MSHOPS", "page_id": "912523826be2457da40f2ff428c83946"}, \
               {"script": "Publis Faltantes en GBP", "page_id": "6b61bb35-b52f-4d2b-abe6-637bb6ff0829"}, \
                {"script": "Resultados Ventas", "page_id": "b12ad3d2-eb5c-44d7-8af3-cb2b91b4abf4"}, \
                    {"script": "Stock MG ML", "page_id": "eac48b7d-1113-4a24-bc77-7e4f3c605e8c"}, \
                        {"script": "item de prueba desde Postman", "page_id": "f647dd2a-3ae7-4be2-a2a3-2210a2952b32"}, \
                            {"script": "Retiro en persona", "page_id": "9ac271ab-f3d7-4209-945f-4a81ac046c6a"}, \
                                {"script": "Garantias ML", "page_id": "4e54343f-5182-4776-8de8-df2e0b15339c"}, \
                                    {"script": "Flex ML", "page_id": "db911620-2531-4c2c-bc7d-81e8e9123e29"}, \
                                        {"script": "Control Precios MG", "page_id": "aa30029d-3a81-4e8d-9856-4ecd2960c716"}, \
                                            {"script": "Database Costos MG", "page_id": "c15803b7-95c6-4ba1-a510-385bb4ecfa5c"}]

#   

    for x in range(0, len(paginas)):
        if paginas[x]["script"] == script:
            page_id = paginas[x]["page_id"]

            url = "https://api.notion.com/v1/pages/"+page_id

            payload = json.dumps({
              "properties": {
                "Check": {
                  "checkbox": True
                }
              }
            })
            headers = {
              'Authorization': notion_token("pruebas api"),
              'Content-Type': 'application/json',
              'Notion-Version': '2022-06-28',
              'Cookie': '__cf_bm=bou0GgSsqJbETNVsb0Sm9J9q8rzl99ayDjv8QjX3LL4-1675105804-0-AUhhnYyTrY6euRdIqIoPF5Raed3JV6mFQTdv9monCtG5y7nMb08Hmyl/fgojmUe2frxnJMO0+PCDMFpmk2qcPqY='
            }

            response = requests.request("PATCH", url, headers=headers, data=payload)

            if response.status_code == 200:
                print("Listo Notion")
            else:
                print("OJO! Respuesta al intentar actualizar database de notificaciones en Notion:")
                print("  Status Code:", response.status_code)
                print()
                print(response.text)
                print()
            break

if __name__ == "__main__":
    check_notificacion_script("Database Costos MG")