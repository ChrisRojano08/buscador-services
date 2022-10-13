# Programa "Extractor de URL's"
# Esau Abraham Meneses Baez - Christopher Rojano Jimenez

import os
from os.path import exists
import whois
from flask import jsonify
import logging

class Extractor: 
    def is_registered(domain_name):
        try:
            w = whois.whois(domain_name)
        except Exception:
            return False
        else:
            return bool(w.domain_name)

    def checkUrl(fileText):
        finalTxt = []
        for i in fileText:
            valiGoogle = i.find("google.com")
            valiGit = i.find("github.com")
            valilocal = i.find("localhost")
            
            if valiGoogle == -1 and valiGit == -1 and valilocal == -1:
                if Extractor.is_registered(i):
                    finalTxt.append(i)
        return finalTxt

    def rFile(fileText, path):
        text = fileText.read()
        tp = text.split("\n")
        
        if exists(path):
            pathU = open(path, encoding="utf8")
            oldUrls = pathU.read().split("\n")[:-1]
            pathU.close()
        else:
            oldUrls = []

        textL = []
        for ite in tp:
            te = ite[(ite.find("HEAD ")+5):]
            te = te[:(te.find("- HIER"))].replace(" ", "")

            if not(te in oldUrls):
                textL.append(te)
        
        textSave = []
        textIte = set(textL)
        for i in textIte:
            if textL.count(i) > 1:
                textSave.append(i)
            else:
                textSave.append(i)
        
        finalText = Extractor.checkUrl(fileText=textSave)

        if len(finalText) > 0:
            Extractor.saveTxt(textIn=str(finalText).replace(",", "\n").replace("'","").replace("[","").replace("]","").replace(" ",""), nameFile=path)
        
    def saveTxt(textIn, nameFile):
        with open(nameFile, "a", encoding="utf-8") as f:
            f.write(textIn)
            f.write('\n')

        f.close()
        logging.info("Exito!\nSe ha guardado el archivo en: "+nameFile)

    def extractor(self):
        pathFile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'access.log')
        pathUrl = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'urls.txt')
        
        try:
            url = open(pathFile, encoding="utf8")
            Extractor.rFile(url, pathUrl)
        except Exception as e:
            logging.error("Error al obtener la informacion\nVerifique la direccion de su path")
            return jsonify(status='Error', exception=''+str(e))
        

        res = [
                {
                    "status": 'Ok',
                    "message": 'Se generaron las urls con exito!'
                }
            ]

        return jsonify(res)

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
        


