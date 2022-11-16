import logging
from flask import jsonify
import os
from os.path import exists
import json
import time

from .indices import Indices
indices = Indices()

class Search():
    def getDict(pathFile):
        data = []
        if exists(pathFile):
            with open(pathFile.replace('.txt','_T.txt'), encoding="utf8") as f:
                data = json.load(f)
            
            for key, value in data.items():
                items = []
                for item in value:
                    newIt = item
                    items.append(newIt)

                data[key] = items
        return data

    def obtainUrls(text, path):
        try:
            invDict = Search.getDict(path)
            words = text.split()

            urls = []
            if len(words) == 1:
                for key, values in invDict.items():
                    if text.lower() in key.lower():
                        for value in values:
                            if not(value[0] in urls):
                                urls.append(value)
            else:
                justUrls = []
                for word in words:
                    logging.error(word)
                    for key, values in invDict.items():
                        if word.lower() == key.lower():
                            for value in values:
                                if not(value[0] in justUrls):
                                    urls.append(value)
                                    justUrls.append(value[0])
                                else:
                                    urls[justUrls.index(value[0])][2] += value[2]

                #logging.error([sublist[0] for sublist in urls])

            urls.sort(key=lambda row: (row[2]))
        except Exception as e:
            urls = str(e)

        return urls

    def getUrls(self, datos):
        inicio = time.time()
        dataSearch = datos['search']

        try:
            pathFileInvDict = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'indiceInv.txt')

            urls = Search.obtainUrls(dataSearch, pathFileInvDict)

            fin = time.time()
            res = {
                    "status": 'Ok',
                    "message": 'Se generó el diccionario con exito!',
                    "data": urls,
                    "time": str(len(urls))+" resultados obtenidos en "+str(round(fin-inicio, 4))+" segundos"
                }
        
        except Exception as e:
            logging.error("Error al obtener la informacion\nVerifique su archivo!")
            return jsonify(status='Error', exception=''+str(e))
        
        return jsonify(res)