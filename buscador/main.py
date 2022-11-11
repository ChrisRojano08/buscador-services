from flask import Flask, jsonify
import logging

#Importando paquetes que implementan la funcionalidad
from services.extractor_urls import Extractor
extractor = Extractor()

from services.indices import Indices
indices = Indices()

app = Flask(__name__)

#Ruta de prueba
@app.route("/")
def test():
    return "<h1 style='color:blue'>Hello There!</h1>"

#Ruta para generar el archivo de urls
@app.route("/generateUrls")
def generateUrls():
    try:
        response = extractor.extractor()

        return response
    except Exception as e:
        logging.exception(e)
        return jsonify(status='Error',  info='Algo salio mal', excepcion=''+str(e))

#Ruta para obtener lista de urls
@app.route("/getUrls")
def getUrls():
    try:
        response = extractor.getUrls()

        return response
    except Exception as e:
        logging.exception(e)
        return jsonify(status='Error',  info='Algo salio mal', excepcion=''+str(e))

#Ruta para generar el dicionario 
@app.route("/generateIdx")
def generateIdx():
    try:
        response = indices.generateIdx()

        return response
    except Exception as e:
        logging.exception(e)
        return jsonify(status='Error',  info='Algo salio mal', excepcion=''+str(e))

#Ruta para obtener el diccionario
@app.route("/getIdx")
def getIdx():
    try:
        response = indices.getIdx()

        return response
    except Exception as e:
        logging.exception(e)
        return jsonify(status='Error',  info='Algo salio mal', excepcion=''+str(e))

#Ruta para traducir el diccionario
@app.route("/translateIdx")
def trasnlateIdx():
    try:
        response = indices.trasnlateIdx()

        return response
    except Exception as e:
        logging.exception(e)
        return jsonify(status='Error',  info='Algo salio mal', excepcion=''+str(e))

#Ruta para generar el dicionario inverso
@app.route("/generateIdxInv")
def generateIdxInv():
    try:
        response = indices.generateIdxInv()

        return response
    except Exception as e:
        logging.exception(e)
        return jsonify(status='Error',  info='Algo salio mal', excepcion=''+str(e))

#Definimos que el host sera "localhost"
if __name__ == "__main__":
    app.run(host='0.0.0.0')
