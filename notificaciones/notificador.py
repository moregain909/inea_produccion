#   Defines classes and methods for Oberver Pattern
#   main(): Notifier script that accepts command line arguments

import argparse
from typing import Union, Dict, List, Tuple

import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
path2root = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(path2root)

from notion.notion_helpers import check_notificacion_script, notion_token
from telegram.telegram_helpers import mandar_mensaje_telegram, chat_telegram

#   Observer Pattern - Objects setup

def create_class_instance(class_name, variables):
    """ Creates a class instance from its name and variables. 
    Allows to create a class instance from iteration using variables for name and instance variables. 
    Args:
        class_name (str): Class name
        variables (dict): Class variables
    
    Returns:
        class_instance (class): Class instance
    
    Raises:
        NameError: If class name is not found in globals()
        TypeError: If class variables are not valid for the class instance
    """
    class_ = globals()[class_name]
    if variables != None:
        try:
            class_instance = class_(**variables)
        except TypeError as e:
            print(f'Error al crear la instancia de {class_name}. Variable no esperada\n{e}')
            return False
            
    else:
        class_instance = class_()
    return class_instance


# Generic Class used for unit test
class TestClass:
    def __init__(self, var1=None, var2=None):
        self.var1 = var1
        self.var2 = var2

# Observer parent class
class Observer:
    
    def notify(self, **kwargs):
        pass

    def notify_up(self, **kwargs):
        pass

    def notify_down(self, **kwargs):
        pass

    #def __repr__(self) -> str:
    #    print(self.__name__)


# Notifier class
class StatusNotifier:
    
    def __init__(self):
        self.observers = []

    def attach(self, observer):
        self.observers.append(observer)

    def attach_all(self, observers: Union[str, Dict, Observer]):
        """ 
        Args:
            Acepta lista con nombres o dicts (con nombre y variables) de observers.
            Ej: ["TelegramObserver", "ConsoleObserver", \
                {"NotionObserver": {"notion_script": "Web Service MG"}}]

        """
        for o in observers:
            #print(o, type(o))
            if isinstance(o, Observer):   # manages an instance of Observer's subclass as input
                instance = o
            else:
                if type(o) not in (str, dict):
                    print(f'No se puede agregar Observer {o}. Tipo incorrecto.')
                    pass
                
                else:
                    # Setup class name and class variables based on observer item type
                    if type(o) == dict:
                        observer_class_name = list(o.keys())[0]
                        observer_class_variables = o[observer_class_name]
                    else:
                        observer_class_name = o
                        observer_class_variables = {}
                    
                    ## Create the observer instance
                    instance = create_class_instance(observer_class_name, observer_class_variables)
            self.attach(instance)
            #print(f'Se agregó {instance.__class__.__name__} a la lista de observadores')

        if len(self.observers) > 0:
            return True
        else:
            print(f'No se agregó ningún Observer')
            return False

    def show_observers(self):
        for observer in self.observers:
            print(f"{observer}")

    def detach(self, observer):
        self.observers.remove(observer)

    def notify(self, **kwargs):
        """ Notifica a través de todos los suscriptores.
        Kwargs: 
            message (str): Notificación a enviar. Usado por ConsoleObserver, TelegramObserver.
            notion_script (str): Nombre del script para notificar ejecución en Notion. Usado por NotionObserver.
            chat_alias (str): Alias del chat de Telegram. Usado por TelegramObserver. 
            nombre_bot (str): Alias del bot de Telegram. Usado por TelegramObserver.

        """
        for observer in self.observers:
            observer.notify(**kwargs)

    def notify_up(self, **kwargs):
        for observer in self.observers:
            observer.notify_up(**kwargs)

    def notify_down(self, **kwargs):
        for observer in self.observers:
            observer.notify_down(**kwargs)


# Observer classes
class NotionObserver(Observer):
    
    def __init__(self, integracion = "pruebas api", notion_script = None):
        self.integracion = integracion
        self.token = notion_token(self.integracion)
        self.script = notion_script

    def notify_up(self, **kwargs):

        if kwargs.get("notion_script"):
            script = kwargs.get("notion_script")
        else:
            if self.script:
                script = self.script
            else:
                print("No se especificó el script a notificar")
                return False

        try:
            check_notificacion_script(script)
            print(f"Ejecución notificada en Notion: {script}")
            return True
        except Exception as e:
            print(f"Error al registrar ejecución en Notion: {e}")
            return False
            
          
    def notify_down(self, **kwargs):
        pass

    def notify(self, **kwargs):

        if kwargs.get("notion_script"):
            script = kwargs.get("notion_script")
        else:
            if self.script:
                script = self.script
            else:
                print("No se especificó el script a notificar")
                return False

        try:
            check_notificacion_script(script)
            print(f"Ejecución notificada en Notion: {script}")
            return True
        except Exception as e:
            print(f"Error al registrar ejecución en Notion: {e}")
            return False


class TelegramObserver(Observer):

    default_nombre_bot = "iojan"
    default_chat_alias = "ineabots"

    def __init__(self, nombre_bot=None, chat_alias=None) -> None:
        if nombre_bot:
            self.nombre_bot = nombre_bot
        else:
            self.nombre_bot = TelegramObserver.default_nombre_bot
        if chat_alias:
            self.chat_alias = chat_alias
        else:
            self.chat_alias = TelegramObserver.default_chat_alias
        self.chat_id = chat_telegram(chat_alias)
    
    def notify(self, **kwargs):
        if "chat_alias" in kwargs.keys():
            chat_alias = kwargs.get("chat_alias")
        else:
            chat_alias = "ineabots"
            #print("No se especificó el alias del chat a notificar, se usa ineabots por defecto en TelegramObserver.notify_up")
        chat_id = chat_telegram(chat_alias)
        
        if "message" in kwargs.keys():
            message = kwargs.get("message")
        else:
            message = "Faltó especificar el mensaje a enviar en TelegramObserver.notify_up"

        if "bot_name" in kwargs.keys():
            nombre_bot = kwargs.get("bot_name")
        else:
            nombre_bot = "iojan"
            #print("No se especificó el nombre del bot a usar, se usa iojan por defecto en TelegramObserver.notify_up")
        
        mandar_mensaje_telegram(nombre_bot, chat_id, message)
        return True

    def notify_up(self, **kwargs):
        pass

    def notify_down(self, **kwargs):
        if "chat_alias" in kwargs.keys():
            self.chat_alias = kwargs.get("chat_alias")
            self.chat_id = chat_telegram(self.chat_alias)
        else:
            self.chat_id = chat_telegram(TelegramObserver.default_chat_alias)
            print(f'No se especificó el alias del chat a notificar. Se usa default {TelegramObserver.default_chat_alias}.')
        
        if "message" in kwargs.keys():
            message = kwargs.get("message")
        else:
            message = "notify_down: Faltó especificar el mensaje a enviar."

        if "nombre_bot" in kwargs.keys():
            self.nombre_bot = kwargs.get("nombre_bot")
        else:
            print(f'No se especificó el nombre del bot a usar en TelegramObserver.notify_up. Se usa default {TelegramObserver.default_nombre_bot}.')
        
        #print(f'nombre_bot: {self.nombre_bot}, chat_id: {self.chat_id}, chat_alias: {self.chat_alias}')
        mandar_mensaje_telegram(self.nombre_bot, self.chat_id, message)
        return True


class ConsoleObserver(Observer):

    def notify(self, **kwargs):
        if "message" in kwargs.keys():
            message = kwargs.get("message")
        print(f'{message}')
        return True
    
    def notify_up(self, **kwargs):
        if "message" in kwargs.keys():
            message = kwargs.get("message")
        else: 
            message = "Service is Up"
        print(f'{message}')
        return True

    def notify_down(self, **kwargs):
        if kwargs.get("message"):
            message = kwargs.get("message")
        else:
            message = "Service is Down"
        print(message)
        return True


if __name__ == "__main__":

    # Command-line arguments configuration
    parser = argparse.ArgumentParser(description='Notificador')
    parser.add_argument('-m', '--message', dest='message', help='Mensage a notificar')
    parser.add_argument('-o', '--option', dest='option', help='Método a utilizar (options: "up" for notify_up (default), "down" for notify_down, "notify" for notify)')
    parser.add_argument('-c', '--channels', dest='channels', nargs='+', help='Canales de notificación (channels: "console" (default), "telegram", "notion")')
    parser.add_argument('-s', '--script', dest='script', help='Script a notificar su ejecución en Notion. Si se especifca un script, se incorpora notion a los channels aunque no se haya especificado con -c')


    # Maps Notifier methods
    NOTIFIER_METHODS_MAPPING = {"up": "notify_up", "down": "notify_down", "notify": "notify"}

    # Args setup
    args = parser.parse_args()
         
    if args.message:            # Notification message
        message = args.message
    else:
        message = None

    if not args.option:         # Notifier method
        method = "notify_up"
    else:
        if args.option not in NOTIFIER_METHODS_MAPPING.keys():
            print(f'No se reconoce el método {args.option}. Utilizando "notify_up" por defecto')
            method = "notify_up"
        else:
            method = NOTIFIER_METHODS_MAPPING[args.option]

    if not args.channels:       # Notificacion channels
        channels = ["console"]
    else:
        channels = args.channels

    if args.script:             # Notion script
        notion_script = args.script
        if "notion" not in channels:
            # Agrega Notion como channel aunque no esté especificado como -c
            channels.append("notion")   
    else:
        notion_script = None

    # Maps attributes for each Observer class
    OBSERVERS_VARS_MAPPING = {"NotionObserver": {"notion_script": notion_script}}

    # Formats channels with Observer classes' names
    channels = [c.title() + "Observer" for c in channels]

    # Configures Notifier and Observers
    mg_status_notifier = StatusNotifier()
    
    for c in channels:

        # Get the channel's classname
        channel_class = getattr(sys.modules[__name__], c)
        
        ## Instantiate the class with its variables
        if c in OBSERVERS_VARS_MAPPING:
            instance = create_class_instance(channel_class.__name__, OBSERVERS_VARS_MAPPING[c])
        else:
            instance = channel_class()

        # Attachs the instance to the StatusNotifier
        mg_status_notifier.attach(instance)

    # Configures Notifier method as an object
    notification_object = getattr(mg_status_notifier, method)
    
    #   Sends notification
    notification_object(message=message)

