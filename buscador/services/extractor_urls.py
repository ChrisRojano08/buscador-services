# Programa "Extractor de URL's"
# Esau Abraham Meneses Baez - Christopher Rojano Jimenez

import os
from os.path import exists
import whois
from flask import jsonify
import logging
import urllib.request
import time

from .execTime import Timer
formatTi = Timer()

class Extractor: 
    #Validacion de urls mediante la libreria whois
    def is_registered(domain_name):
        try:
            w = whois.whois(domain_name)
        except Exception:
            return False
        else:
            return bool(w.domain_name)

    #Filtro para eliminar urls de google o github y consultas a localhost
    def checkUrl(fileText, path):
        n=0
        with open(path, "a", encoding="utf-8") as fileUrl:
            try:
                valiGoogle = fileText.find("google.com")
                valiGit = fileText.find("github.com")
                valilocal = fileText.find("localhost")
                    
                if valiGoogle == -1 and valiGit == -1 and valilocal == -1:
                    if not fileText.endswith('.css'):
                        if not fileText.endswith('.pptx'):
                            if not fileText.endswith('.ppt'):
                                try:
                                    hdr = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)' }
                                    req = urllib.request.Request(fileText, headers=hdr)
                                    urllib.request.urlopen(req, timeout=10)

                                    fileUrl.write(fileText)
                                    fileUrl.write('\n')
                                    n=1
                                except:
                                    print('',end='')
                                    n=0
            except Exception as e:
                logging.error(str(e))
                n=0
        return n

    #Obtención de urls
    def rFile(fileText, path):
        #Se lee el archivo de access.log
        text = fileText.read()
        tp = text.split("\n")
        
        #Se valida si ya existe un archivo de urls previo
        # si existe obtiene las urls anteriores
        if exists(path):
            pathU = open(path, encoding="utf8")
            oldUrls = pathU.read().split("\n")[:-1]
            pathU.close()
        else:
            oldUrls = []

        #Se itera entre las lineas del access.log y se extrae solo las urls
        textL = []
        for ite in tp:
            try:
                te = ite[(ite.find("HEAD ")+5):]
                te = te[:(te.find("- HIER"))].replace(" ", "")
            except Exception as e:
                logging.error(str(e))

            #De haber urls previas, se valida que no este repetida la url
            if not(te in oldUrls):
                textL.append(te)
        
        #Se eliminan duplicados del access.log
        nUrl = 0
        textIte = set(textL)
        for i in textIte:
            try:
                if textL.count(i) > 1:
                    nUrl += Extractor.checkUrl(i, path)
                else:
                    nUrl += Extractor.checkUrl(i, path)
            except Exception as e:
                logging.error(str(e))
        return nUrl
        
    #Guardado de urls en un archivo txt
    def saveTxt(textIn, nameFile):
        with open(nameFile, "a", encoding="utf-8") as f:
            f.write(textIn)
            f.write('\n')

        f.close()
        logging.info("Exito!\nSe ha guardado el archivo en: "+nameFile)

    #Metodo principal que llama a los metodos que extraen las urls
    def extractor(self):
        inicio = time.time()

        pathFile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'access.log')
        pathUrl = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'urls.txt')
        
        try:
            url = open(pathFile, encoding="utf8")
            nUrls = Extractor.rFile(url, pathUrl)
        except Exception as e:
            logging.error("Error al obtener la informacion\nVerifique la direccion de su path")
            return jsonify(status='Error', exception=''+str(e))
        
        if nUrls<=0:
            res = [
                    {
                        "status": 'Ok',
                        "message": 'No se generaron nuevas urls.',
                    }
                ]
        else:
            fin = time.time()
            res = [
                    {
                        "status": 'Ok',
                        "message": 'Se generaron las urls con exito!',
                        "time": str(nUrls)+" urls generadas en "+str(formatTi.execTime(inicio, fin))
                    }
                ]

        return jsonify(res)

    #Metodo que lee las urls y las regresa como respuesta json
    def getUrls(self):
        urls = []

        try:
            pathFile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'urls.txt')
            urls = open(pathFile, encoding="utf8")
        except Exception as e:
            logging.error("Error al obtener la informacion\nVerifique la direccion de sus urls")
            return jsonify(status='Error', exception=''+str(e))

        res = [
                {
                    "status": 'Ok',
                    "message": 'Se obtuvieron las urls con exito!',
                    "data": [word.strip() for word in urls.readlines()]
                }
            ]
        return jsonify(res)
        


