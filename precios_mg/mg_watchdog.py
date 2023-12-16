#   Testea la conexión al web service de Microglobal

import argparse

import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
path2root = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(path2root)

from precios_mg_helpers import mg_get_brands_xml
from notificaciones.notificador import StatusNotifier

if __name__ == "__main__":

    channels = ["TelegramObserver", "ConsoleObserver", \
                {"NotionObserver": {"notion_script": "Web Service MG"}}]

    #   Configures Notifier and Observers
    mg_status_notifier = StatusNotifier()
    mg_status_notifier.attach_all(channels)

    #   Testea la conexión al web service de Microglobal
    if mg_get_brands_xml():
        message = f'WS MG up'
        mg_status_notifier.notify_up(message=message)
    else:
        message = f' 🔴 🔴 Atención! El web service MG NO RESPONDE!'
        mg_status_notifier.notify_down(message=message)
