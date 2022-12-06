import logging
from flask import jsonify
import os
from os.path import exists
import json
import time
import itertools

from nltk.corpus import stopwords

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

    def obtainUrls(text, path, typeUrls):
        try:
            invDict = Search.getDict(path)
            words = text.split()

            urls = []
            spanish_stop = set(stopwords.words('spanish'))

            if len(words) == 1:
                justUrls = []
                if not(text.lower() in spanish_stop):
                    for key, values in invDict.items():
                        if key.lower() in text.lower():
                            for value in values:
                                if typeUrls != 'ALL':
                                    if not(value[0] in justUrls) and value[1]==typeUrls:
                                        savAux = value[:]
                                        savAux.append([[text, value[2]]])

                                        urls.append(savAux)
                                        justUrls.append(value[0])
                                else:
                                    if not(value[0] in justUrls):
                                        savAux = value[:]
                                        savAux.append([[text, value[2]]])

                                        urls.append(savAux)
                                        justUrls.append(value[0])
            else:
                justUrls = []
                for word in words:
                    if not(word.lower() in spanish_stop):
                        for key, values in invDict.items():
                            if  key.lower() in word.lower():
                                for value in values:
                                    if typeUrls != 'ALL':
                                        if not(value[0] in justUrls) and value[1]==typeUrls:
                                            savAux = value[:]
                                            savAux.append([[word, value[2]]])

                                            urls.append(savAux)
                                            justUrls.append(value[0])
                                        elif value[1]==typeUrls:
                                            if any(e[0] == word for e in urls[justUrls.index(value[0])][4]):
                                                urls[justUrls.index(value[0])] [4] [[sublist[0] for sublist in urls[justUrls.index(value[0])] [4]].index(word)][1] += value[2]
                                            else:
                                                urls[justUrls.index(value[0])][4].append([word, value[2]])
                                            
                                            urls[justUrls.index(value[0])][2] += value[2]
                                    else:
                                        if not(value[0] in justUrls):
                                            savAux = value[:]
                                            savAux.append([[word, value[2]]])

                                            urls.append(savAux)
                                            justUrls.append(value[0])
                                        else:
                                            if any(e[0] == word for e in urls[justUrls.index(value[0])][4]):
                                                urls[justUrls.index(value[0])] [4] [[sublist[0] for sublist in urls[justUrls.index(value[0])] [4]].index(word)][1] += value[2]
                                            else:
                                                urls[justUrls.index(value[0])][4].append([word, value[2]])
                                            
                                            urls[justUrls.index(value[0])][2] += value[2]

            urls.sort(key=lambda row: (row[2]), reverse=True)
        except Exception as e:
            urls = str(e)

        return urls

    def obtainImgs(text, path):
        try:
            invImgDict = Search.getDict(path)
            words = text.split()

            urls = []
            justUrls = []
            spanish_stop = set(stopwords.words('spanish'))

            if len(words) == 1:
                if not(text.lower() in spanish_stop):
                    for key, values in invImgDict.items():
                        if key.lower() in text.lower():
                            for value in values:
                                if not(value[0] in justUrls):
                                    for srcImg in value[2]:
                                        savAux = [value[0], value[1], srcImg]
                                        urls.append(savAux)

                                    justUrls.append(value[0])
            else:
                justUrls = []
                for word in words:
                    print(word)
                    if not(word.lower() in spanish_stop):
                        for key, values in invImgDict.items():
                            if key.lower() in word.lower():
                                for value in values:
                                    if not(value[0] in justUrls):
                                        for srcImg in value[2]:
                                            savAux = [value[0], value[1], srcImg]
                                            urls.append(savAux)

                                        justUrls.append(value[0])
                                    else:

                                        urls[justUrls.index(value[0])][1] += value[1]

            urls.sort(key=lambda row: (row[1]), reverse=True)
            urls = list(urls for urls,_ in itertools.groupby(urls))
        except Exception as e:
            urls = str(e)

        return urls

    def getUrls(self, datos, typeUrls):
        inicio = time.time()
        dataSearch = datos['search']

        try:
            pathFileInvDict = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'indiceInv.txt')

            urls = Search.obtainUrls(dataSearch, pathFileInvDict, typeUrls)

            fin = time.time()
            res = {
                    "status": 'Ok',
                    "message": 'Se obtuvieron las urls con exito!',
                    "data": urls,
                    "time": str(len(urls))+" resultados obtenidos en "+str(round(fin-inicio, 4))+" segundos"
                }
        
        except Exception as e:
            logging.error("Error al obtener la informacion\nVerifique su archivo!")
            return jsonify(status='Error', exception=''+str(e))
        
        return jsonify(res)

    def getImgs(self, datos):
        inicio = time.time()
        dataSearch = datos['search']

        try:
            pathFileInvDict = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'indiceImgInv.txt')

            imgs = Search.obtainImgs(dataSearch, pathFileInvDict)

            fin = time.time()
            res = {
                    "status": 'Ok',
                    "message": 'Se obtuvieron las imagenes con exito!',
                    "data": imgs,
                    "time": str(len(imgs))+" resultados obtenidos en "+str(round(fin-inicio, 4))+" segundos"
                }
        
        except Exception as e:
            logging.error("Error al obtener la informacion\nVerifique su archivo!")
            return jsonify(status='Error', exception=''+str(e))
        
        return jsonify(res)