from decouple import config
from dotenv import load_dotenv
import telebot

import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
path2root = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(path2root)

def markdown_text(text):
    """Compatibiliza un texto cualquiera con MarkdownV2 salvando los caracteres reservados agregando "\" antes.
    Los caracteres reservados son ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']

    Args:
        text (_str_): Texto a compatibilizar con Markdown

    Returns:
        _str_: Texto con caracteres especiales salvados con "\".
    """
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    escaped_text = ''.join(['\\' + t if t in special_chars else t for t in text])
    return escaped_text

def telegram_api_key(bot_name):
    if bot_name.lower() == "tecnorium":
        API_KEY = config("TEC_TEL_BOT_API_KEY")
    elif bot_name.lower() == "celestron":
        API_KEY = config("CEL_TEL_BOT_API_KEY")
    elif bot_name.lower() == "lenovo":
        API_KEY = config("LEN_TEL_BOT_API_KEY")
    elif bot_name.lower() == "iojan" or bot_name.lower() == "iojann":
        API_KEY = config("IOJAN_TEL_BOT_API_KEY")
    else:
        print("No se tienen credenciales para el bot, se usan las de iojan", bot_name)
        API_KEY = config("IOJAN_TEL_BOT_API_KEY")
    return API_KEY

def chat_telegram(alias_chat):

    if alias_chat == "ineabots" or alias_chat == "inea bots":
        chat_id = -625477360
    elif alias_chat == "ineapublis" or alias_chat == "inea publis":
        chat_id = -625477360    
    elif alias_chat == "ineanotis" or alias_chat == "inea notis":
        chat_id = -625477360   
    elif alias_chat == "ineaquestions" or alias_chat == "inea questions":
        chat_id = -625477360        
    else:
        chat_id = False
    return chat_id


def mandar_mensaje_telegram(nombre_bot, chat_id, mensaje, parse="MarkdownV2"):
    """Envía mensaje por telegram. 

    Args:
        nombre_bot (_str_): Nombre de Bot que tiene que estar presente en telegram_api_key()
        alias_chat (_str_): Alias que debe estar presente en chat_telegram()
        mensaje (_str_): Mensaje que se quiere enviar.
        parse (str, optional): _description_. Defaults to "MarkdownV2". Otra opción es usar "HTML". Si no se quiere parsear, se pasa parse=None. Más info sobre formateo de mensajes: https://core.telegram.org/bots/api#formatting-options
    """

    bot = telebot.TeleBot(telegram_api_key(nombre_bot))
    if parse == None:
        bot.send_message(chat_id, markdown_text(mensaje))
    else:
        bot.send_message(chat_id, markdown_text(mensaje), parse_mode=parse)


# mandar_mensaje_telegram("iojan", chat_telegram("ineabots"), "🔴 🟠 🟡 🟢 🟣 🔵 ⚪")
# print(chat_telegram("ineabots"))

if __name__ == '__main__':
    mandar_mensaje_telegram("iojan", chat_telegram("ineabots"), "mensaje de prueba")
    pass