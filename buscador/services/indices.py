import re
import urllib.request
import nltk
from nltk.tokenize import regexp_tokenize
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
import os
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

        with open(pathFile, "w", encoding="utf-8") as f:
            if isinstance(textIn, str):
                f.write(textIn)
            elif isinstance(textIn, dict):
                f.write(json.dumps(textIn))
        f.close()

    def readTxt(url, prevText, pathFile):
        text = prevText
        text = text.replace('_', ' ').replace('(','').replace(')','').replace('-','').replace(';','')
        tokenizer = RegexpTokenizer('\s+', gaps=True)
        tp = tuple(tokenizer.tokenize(text))
        spanish_stop = set(stopwords.words('spanish'))
        tp = [word for word in tp if not word.isnumeric()]
        tp = [word for word in tp if word.isalnum()]
        tp = [word for word in tp if word.lower() not in spanish_stop]
        tps = set(tp)
        finaltp = []
        for i in tps:
            if len(i) > 2:
                if tp.count(i) > 1:
                    finaltp.append([i, tp.count(i)])
                else:
                    finaltp.append([i, tp.count(i)])
        
        # Indices.saveTxt(textIn=str(finaltp).replace(" ", "\n"), nameF=pathFile)
        return finaltp
        
    def generateIdx(self):
        urls = pathFile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'urls.txt')
        try:
            urls = open(pathFile, encoding="utf8")
            urls = [word.strip() for word in urls.readlines()]
            i = 0

            idx = {}
            for url in urls:
                logging.error(url)
                text = Indices.getText(url)
                indN = Indices.readTxt(url=url, prevText=text, pathFile=("text"+str(i)+".txt"))

                idx[''+url+''] = indN
                i += 1

            # logging.error(idx)
            Indices.saveTxt(idx, 'dictionay.txt')

        except Exception as e:
            logging.error("Error al obtener la informacion\nVerifique las urls de su archivo!")
            return jsonify(status='Error', exception=''+str(e))

        res = [
                {
                    "status": 'Ok',
                    "message": 'Se obtuvieron las urls con exito!',
                    "data": 'si'
                }
            ]
        return jsonify(res)