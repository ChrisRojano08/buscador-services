import re
import urllib.request
from xml.dom import NotFoundErr
import nltk
from nltk.tokenize import regexp_tokenize
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
import os
from os.path import exists
import logging
from flask import jsonify
import json

class Indices:
    def removeBetweenTag(tagR, actI, txtF):
        wordAux = ''
        actI+=1
        
        initI = actI-1
        while wordAux!=('</'+tagR):
            if actI>=len(txtF):
                logging.error('Se encontró un < sin cerrar')
                logging.error('Caracter empezo en '+ str(initI))
                break
            auxC = txtF[actI]
            if auxC == '<':
                initII = actI
                while auxC != '>':
                    if actI>=len(txtF):
                        logging.error('Se encontró un < sin cerrar')
                        logging.error('Caracter empezo en '+ str(initII))
                        break

                    wordAux += auxC
                    actI+=1
                    auxC = txtF[actI]
            else:
                wordAux=''
                actI+=1
        return actI

    def removeBetweenChr(chrR, actI, txtF):
        auxC=''
        initI = actI
        while auxC != chrR:
            actI+=1
            auxC = txtF[actI]
            if actI>len(txtF):
                logging.error('Falta '+chrR+' de cierre')
                logging.error('Caracter empezo en '+ str(initI))
                break
        return actI

    def removeRepiteChr(chrR, txtF):
        auxC=''
        i = 0
        newTxt=''
        while i<(len(txtF)-2):
            if i>len(txtF):
                break
            auxC = txtF[i]

            if(auxC == chrR):
                while txtF[i+1] == chrR:
                    i+=1
                    if i<len(txtF):
                        break
            newTxt += auxC
            i+=1
        return newTxt

    def getText(url):
        try:
            uslessChars = [':', ",", ".", "/", "+", "\"", "\'", "\\", "\n", "$", "-", ">", '[', "]", "\t", "#"]
            uslessTags = ['script', 'semmantics', 'math', 'annotation', 'style']

            logging.info('Solicitando info....')
            fp = urllib.request.urlopen(url, timeout=25)
            mybytes = fp.read()

            mystr = mybytes.decode("utf8")
            fp.close()
            logging.info('Informacion de \"'+url+'\" obtenida, procesando...')

            auxC = ''
            newStr = ''
            i = 0
            wordAux=''
            while i<len(mystr):
                auxC = mystr[i]

                if(auxC == '<'):
                    initI = i
                    while auxC != '>':
                        i+=1
                        auxC = mystr[i]
                        wordAux+=auxC
                        if i>len(mystr):
                            logging.error('Se encontró un < sin cerrar')
                            logging.error('Caracter empezo en '+ str(initI))
                            break

                        if wordAux in uslessTags:
                            i = Indices.removeBetweenTag(wordAux, i, mystr)
                            break
                        
                wordAux=''
                
                if(auxC == '['):
                    i = Indices.removeBetweenChr(']', i, mystr)

                if(auxC == '{'):
                    i = Indices.removeBetweenChr('}', i, mystr)
                
                if(auxC != '\n'):
                    newStr += auxC
                
                i+=1
                
            for ch in uslessChars:
                newStr = newStr.replace(ch, " ")
            
            logging.info('Informacion obtenida!\n')
            newStr = Indices.removeRepiteChr(' ', newStr)
            newStr = Indices.removeRepiteChr('\n', newStr)
        except:
            newStr = ''
        return newStr

    def saveTxt(textIn, nameF):
        pathFile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', nameF)
        
        if isinstance(textIn, str):
            with open(pathFile, "a", encoding="utf-8") as f:
                f.write(textIn)
                f.write('\n')

            f.close()
        elif isinstance(textIn, dict):
            with open(pathFile, "w", encoding="utf-8") as f:
                f.write(json.dumps(textIn, ensure_ascii=False))

            f.close()

    def removeRepite(words, chrRmv, numb):
        chrTup = []
        chrFind = ''
        for _ in range(0, numb):
            chrFind+=chrRmv
            chrTup.append(chrFind)
        return [word for word in words if not(word in chrTup)]

    def containsNumber(value):
        if True in [char.isdigit() for char in value]:
            return True
        return False

    def readTxt(url, prevText, pathFile):
        text = prevText
        text = text.replace('_', ' ').replace('(','').replace(')','').replace('-','').replace(';','')

        tokenizer = RegexpTokenizer('\s+', gaps=True)
        tp = tuple(tokenizer.tokenize(text))
        spanish_stop = set(stopwords.words('spanish'))
        tp = [word for word in tp if not(Indices.containsNumber(word))]
        tp = [word for word in tp if not word.isnumeric()]
        tp = [word for word in tp if word.isalnum()]
        tp = [word for word in tp if word.lower() not in spanish_stop]
        tps = set(tp)

        tps = Indices.removeRepite(tps, 't', 75)
        tps = Indices.removeRepite(tps, 'e', 25)

        finaltp = []
        for i in tps:
            if len(i) > 2:
                if tp.count(i) > 1:
                    finaltp.append([i, tp.count(i)])
                else:
                    finaltp.append([i, tp.count(i)])
        
        # Indices.saveTxt(textIn=str(finaltp).replace(" ", "\n"), nameF=pathFile)
        return finaltp
    
    def getDict(pathFile):
        data = {}
        if exists(pathFile):
                with open(pathFile, encoding="utf8") as f:
                    data = json.load(f)
        return data
        
    def generateIdx(self):
        urls = pathFile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'urls.txt')
        pathFileDict = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'dictionay.txt')

        try:
            urls = open(pathFile, encoding="utf8")
            urls = [word.strip() for word in urls.readlines()]
            i = 0

            idx = {}
            prevDict = Indices.getDict(pathFileDict)
            for url in urls:
                if not(url in prevDict):
                    text = Indices.getText(url)
                    if len(text) > 0:
                        indN = Indices.readTxt(url=url, prevText=text, pathFile=("text"+str(i)+".txt"))
                        idx[''+url+''] = indN
                        i += 1

                    logging.error(url)

            if len(idx) > 0:
                if len(prevDict)>0:
                    newDict = idx.copy()
                    for key, value in prevDict.items():
                        newDict[key] = value
                    
                    Indices.saveTxt(newDict, 'dictionay.txt')
                else:
                    Indices.saveTxt(idx, 'dictionay.txt')

        except Exception as e:
            logging.error("Error al obtener la informacion\nVerifique las urls de su archivo!")
            return jsonify(status='Error', exception=''+str(e))

        res = [
                {
                    "status": 'Ok',
                    "message": 'Se generó el diccionario con exito!',
                    "data": 'si'
                }
            ]
        return jsonify(res)

    def getIdx(self):
        pathFile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'dictionay.txt')

        try:
            if exists(pathFile):
                res = [
                    {
                        "status": 'Ok',
                        "message": 'Se obtuvo el diccionario con exito!',
                        "data": Indices.getDict(pathFile)
                    }
                ]

                return jsonify(res)
            else:
                raise NotFoundErr('No se encontró el diccionario! Asegurese de haberlo creado antes')
        except Exception as e:
            logging.error("Error al obtener la informacion\nVerifique su archivo!")
            return jsonify(status='Error', exception=''+str(e))