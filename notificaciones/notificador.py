#   Defines classes and methods for Oberver Pattern
#   main(): Notifier script that accepts command line arguments

import argparse
from typing import Union, Dict, List, Type

import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
path2root = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(path2root)

from notion.notion_helpers import check_notificacion_script, notion_token
from telegram.telegram_helpers import mandar_mensaje_telegram, chat_telegram
from utils.utils_helpers import create_class_instance
#   Observer Pattern - Objects setup 
 

#def create_class_instance(class_parameters: Union[str, Dict, Type]) -> Union[Type, bool]:
#    """ Creates a class instance from input.
#    Args:
#        class_parameters (str, dict): 
#            If argument is str, takes it as class name.
#            If argument is dict, takes it as class name (key) and it's variables (value)
#            If argument is class, returns it
#    
#    Returns:
#        class_instance (class): Class instance
#
#    """
#
#    if isinstance(class_parameters, str):     #   Gestiona la entrada str
#        class_name = class_parameters
#        class_variables = {}
#    elif isinstance(class_parameters, dict):    #   Gestiona la entrada dict
#        class_name = next(iter(class_parameters), None)
#        class_variables = class_parameters[class_name]
#    else:
#        print(f'Tipo incorrecto: No se puede crear instancia de {class_parameters} porque es {type(class_parameters)}. Sólo se acepta str o dict.')
#        return False
#
#    try:
#        class_ = globals()[class_name]
#    except KeyError as e:
#        print(f'Error al crear la instancia de {class_name}. Clase no encontrada\n{e}')
#        return False
#    except Exception as e:
#        print(f'Error al crear la instancia de {class_name}.\n{e}')
#        return False
#    
#    #print(f'creando {class_}')
#    if class_variables != None and class_variables != {}:
#        try:
#            class_instance = class_(**class_variables)
#        except TypeError as e:
#            print(f'Error al crear la instancia de {class_name}. Variable no esperada en {class_variables}\n{e}')
#            return False
#            
#    else:
#        class_instance = class_()
#    
#    return class_instance


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

    def show_variables(self):
        for variable, value in self.__dict__.items():
            print(f'{variable}: {value}')
        return True
        
    def __eq__(self, other) -> bool:
        if isinstance(other, Observer):
            if self.__dict__ == other.__dict__:
                return True
        return False
    
    #def __repr__(self) -> str:
    #    print(self.__name__)

def instance_has_attributes(instance):
    """ Checks if a class instance has attributes.
    Args:
        class_instance (class): Class instance
    Returns:
        True if class instance has attributes.
        False if class instance has no attributes.
    """
    if instance.__dict__ == {}:
        return False
    else:
        return True
    
def all_instance_attributes_present(class_instance, reference_instance):
    """ Checks if all instance attributes and its values that are not None are present in refrerence_instance.

    """
    instance_attributes = class_instance.__dict__
    not_none_instance_attributes = {k: v for k, v in instance_attributes.items() if v is not None}
    reference_attributes = reference_instance.__dict__

    all_attributes_present = all(instance_attr in reference_attributes.items() for instance_attr in not_none_instance_attributes.items())
    
    if all_attributes_present:
        return True
    return False


# Notifier class
class StatusNotifier:
    
    def __init__(self):
        self.observers = []

    def attach(self, observer: Union[str, Dict, Observer]) -> bool:
        """ 
        Args:
            Acepta Observer, 'str' con nombre o dict {nombre: variables} de Observer.
            Observer: TelegramObserver()
            str: "NotionObserver"
            dict: {"notion_script": "Web Service MG"}}
        Returns:
            True si se agregó Observer a la instancia.
            False si no se agregó Observer a la instancia.
        """             
        #   Manages an instance of Observer's subclass as input
        if isinstance(observer, Observer):   
            instance = observer
        else:
            #   Create Observer instance from str or dict
            instance = create_class_instance(observer)     

        if instance:
            self.observers.append(instance)
            return True
        else:
            print(f'No se agregó {instance.__class__.__name__} a la lista de observadores')
            return False
            

    def attach_all(self, observers: List[Union[str, Dict, Observer]]) -> bool:
        """ 
        Args:
            Acepta lista con Observers, 'str' con nombre o dicts {nombre: variables} de Observers.        
            Ej: [TelegramObserver(), "ConsoleObserver", {"NotionObserver": {"notion_script": "Web Service MG"}}]
        Returns:
            True si se agregaron Observers a la lista. 
            False si no se agregaron Observers.
        """
        for o in observers:
            self.attach(o)

        if len(self.observers) > 0:
            return True
        else:
            print(f'No se agregó ningún Observer')
            return False


    def show_observers(self):
        for observer in self.observers:
            print(f"showing observers: {observer.__class__.__name__}")


    def detach(self, observer):

        #   Manages an instance of Observer's subclass as input
        if isinstance(observer, Observer):   
            instance_to_remove = observer
        else:
            #   Create Observer instance from str or dict
            instance_to_remove = create_class_instance(observer)     

        if instance_to_remove:
            for idx, obs in list(enumerate(self.observers))[:]:
                if isinstance(instance_to_remove, type(obs)):
                    if not instance_has_attributes(instance_to_remove):
                        del self.observers[idx]
                        return True
                    else:
                        if all_instance_attributes_present(instance_to_remove, obs):
                            del self.observers[idx]
                            return True
            print(f'No se removió {instance_to_remove.__class__.__name__} de la lista de observadores porque no se encontró una instancia de esa clase.')
            return False        
                    
        else:
            print(f'No se removió {observer} de la lista de observadores porque no se encontró una instancia de esa clase.')
            return False
    
        
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
        """" Este método se usa para confirmar una ejecución exitosa en el dashboard de monitoreo en Notion. 
        Args:
            notion_script (str): Nombre del script para notificar ejecución en Notion. Usado por NotionObserver.
        Returns:
            True si se notificó la ejecución en Notion.
            False si no se notificó la ejecución en Notion.
        
        """

        # Obtiene el script de los argumentos, si no tiene, utiliza el que tenga en self.script
        if kwargs.get("notion_script"):
            script = kwargs.get("notion_script")
        else:
            if self.script:
                script = self.script
            else:
                print("No se especificó el script a notificar")
                return False

        # Envía notificación a Notion
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
    default_chat_alias = "inea_notificaciones"
    default_message = "Ejecución notificada en Telegram. Mensaje por defecto."

    def __init__(self, nombre_bot=None, chat_alias=None) -> None:
        if nombre_bot:
            self.nombre_bot = nombre_bot
        else:
            self.nombre_bot = TelegramObserver.default_nombre_bot
        if chat_alias:
            self.chat_alias = chat_alias
        else:
            self.chat_alias = TelegramObserver.default_chat_alias
        self.chat_id = chat_telegram(self.chat_alias)
    
    def notify(self, **kwargs):
        if "chat_alias" in kwargs.keys():
            chat_alias = kwargs.get("chat_alias")
            chat_id = chat_telegram(chat_alias)
        else:
            chat_alias = self.chat_alias
            chat_id = self.chat_id
        
        if "message" in kwargs.keys():
            message = kwargs.get("message")
        else:
            message = self.default_message

        if "nombre_bot" in kwargs.keys():
            nombre_bot = kwargs.get("nombre_bot")
        else:
            nombre_bot = self.nombre_bot
            #print("No se especificó el nombre del bot a usar, se usa iojan por defecto en TelegramObserver.notify_up")
        
        print(nombre_bot, chat_id, message)
        if mandar_mensaje_telegram(nombre_bot, chat_id, message):
            return True
        return False
      

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

    #   Notifier script that accepts command line arguments

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
            channel_parameters = {channel_class.__name__: OBSERVERS_VARS_MAPPING[c]}
            #instance = create_class_instance(channel_class.__name__, OBSERVERS_VARS_MAPPING[c])
            instance = create_class_instance(channel_parameters)
        else:
            instance = channel_class()

        # Attachs the instance to the StatusNotifier
        mg_status_notifier.attach(instance)

    # Configures Notifier method as an object
    notification_object = getattr(mg_status_notifier, method)
    
    #   Sends notification
    notification_object(message=message)

