# PROCESA REQUESTS DE LA API DE MELI A NUESTRO SERVIDOR


from flask import Flask, render_template, request, flash, send_file, Blueprint
import logging


callbacks_ml = Blueprint('callbacks_ml', __name__, template_folder="templates")



@callbacks_ml.route("/callbacks_ml", methods=['POST'])
def notificaciones_ml():
    #TODO: RECIBIR NOTIFICACIONES DE MELI Y GUARDARLAS EN LA BASE DE DATOS
    
    request_data = request.get_json()

    # Process the JSON data
    if request_data:
        resource = request_data.get('resource')
        user_id = request_data.get('user_id')
        topic = request_data.get('topic')
        application_id = request_data.get('application_id')
        attempts = request_data.get('attempts')
        sent = request_data.get('sent')
        received = request_data.get('received')

        # Do something with the extracted data
        # For example, print the data
        print("Resource:", resource)
        print("User ID:", user_id)
        print("Topic:", topic)
        print("Application ID:", application_id)
        print("Attempts:", attempts)
        print("Sent:", sent)
        print("Received:", received)

    return resource


@callbacks_ml.route("/callbacks_ml/code=<code>", methods=['GET'])
def code_ml(code):
    #TODO: PROCESAR CODE Y RECIBIR REFRESH TOKEN
    # GUARDAR REFRESH TOKEN EN DATABASE
    # NOTIFICAR POR TELEGRAM QUE SE GENERÓ UN NUEVO REFRESH TOKEN CON EXITO
    
    return code
