from flask import Flask, jsonify
import logging

from services.extractor_urls import Extractor
extractor = Extractor()

from services.indices import Indices
indices = Indices()

app = Flask(__name__)

@app.route("/")
def test():
    return "<h1 style='color:blue'>Hello There!</h1>"

@app.route("/generateUrls", methods=['POST'])
def generateUrls():
    try:
        response = extractor.extractor()

        return response
    except Exception as e:
        logging.exception(e)
        return jsonify(status='Error',  info='Algo salio mal', excepcion=''+str(e))

@app.route("/getUrls", methods=['POST'])
def getUrls():
    try:
        response = extractor.getUrls()

        return response
    except Exception as e:
        logging.exception(e)
        return jsonify(status='Error',  info='Algo salio mal', excepcion=''+str(e))

@app.route("/generateIdx", methods=['POST'])
def generateIdx():
    try:
        response = indices.generateIdx()

        return response
    except Exception as e:
        logging.exception(e)
        return jsonify(status='Error',  info='Algo salio mal', excepcion=''+str(e))

if __name__ == "__main__":
    app.run(host='0.0.0.0')
