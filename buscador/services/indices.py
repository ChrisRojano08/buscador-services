import re
import urllib.request
from webbrowser import get
from xml.dom import NotFoundErr
from nltk.tokenize import regexp_tokenize
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
import os
from os.path import exists
import logging
from flask import jsonify
import json
import googletrans
import PyPDF2
import time
from bs4 import BeautifulSoup

from .execTime import Timer
formatTi = Timer()

class Indices:
    #Eliminación de texto entre una etiqueta html (<math></math>, <verbose></verbose>, etc)
    def removeBetweenTag(tagR, actI, txtF):
        wordAux = ''
        actI+=1
        
        initI = actI-1
        #Se itera hasta encontrar la etiqueta de cierre </+etiqueta
        while wordAux!=('</'+tagR):
            #Si se llega al final del texto se lanza un mensaje de error
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

    #Eliminación de texto entre un caracter ("dummy text", /html comment/, etc)
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

    #Eliminación de texto repetido
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

    #Obtencion y clasificacion de las palabras obtenidas en una url
    def getText(url):
        try:
            #Caracteres y etiquetas html a eliminar
            uslessChars = [':', ",", ".", "/", "+", "\"", "\'", "\\", "\n", "$", "-", ">", '[', "]", "\t", "#"]
            uslessTags = ['script', 'semmantics', 'math', 'annotation', 'style']
            typeUrl = ''
            mystr = ''

            #Se hace la peticion para obtener el codigo html de toda la pagina
            logging.info('Solicitando info....')
            fp = urllib.request.urlopen(url, timeout=20)
            mybytes = fp.read()
            headers = fp.getheaders()

            processExt = 'html'
            for head in headers:
                if head[0] == 'Content-Type':
                    if head[1] == 'application/pdf':
                        try:
                            file = open('savePDF' + ".pdf", 'wb')
                            file.write(mybytes)
                            file.close()

                            pdfFileObj = open('savePDF' + ".pdf", 'rb')
                            pdfReader = PyPDF2.PdfFileReader(pdfFileObj, strict=False)

                            for pag in range(0, pdfReader.numPages):
                                pageObj = pdfReader.getPage(pag)
                                mystr += pageObj.extractText().replace('\n', ' ').replace('-', ' ')
                            typeUrl = 'PDF'

                            processExt = 'text'
                        except Exception as e:
                            mystr = ''
                            logging.error(str(e))
                    else:
                        try:
                            mystr = mybytes.decode("utf8")
                            typeUrl = 'URL'
                            processExt = 'html'
                        except:
                            mystr = mybytes.decode("latin-1")
                            typeUrl = 'URL'
                            processExt = 'html'
                        finally:
                            try:
                                soup = BeautifulSoup(mybytes, features="html.parser")

                                for script in soup(["script", "style"]):
                                    script.extract()

                                text = soup.get_text()

                                lines = (line.strip() for line in text.splitlines())
                                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                                mystr = '\n'.join(chunk for chunk in chunks if chunk)
                                processExt = 'text'
                            except Exception as e:
                                mystr = ''
                                logging.error(str(e))
            
            if url.find("youtube.com") != -1:
                typeUrl = 'YOUTUBE'
            else:
                listShop = ['mercadolibre.com.mx',
                        'cyberpuerta.mx',
                        'coppel.com',
                        'walmart.com.mx',
                        'amazon.com.mx',
                        'aliexpress.com',
                        'bodegaaurrera.com.mx',
                        'officedepot.com.mx',
                        'linio.com.mx'
                    ]
                for lsp in listShop:
                    if url.find(lsp) != -1:
                        typeUrl = "SHOP"
                        break

            fp.close()
            logging.info('Informacion de \"'+url+'\" obtenida, procesando...')
            
            newStr = ''
            if processExt=='html':
                auxC = ''
                
                i = 0
                wordAux=''
                #Se itera entre el codigo obtenido y obtener solo el texo
                while i<len(mystr):
                    auxC = mystr[i]

                    #Se eliminan caracteres y etiquetas de html
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
                            
                            #Si se detecta que es una de las etiquetas sin texto util entre ellas
                            # se llama a la funcion que elimina ese texto y las etiquetas
                            if wordAux in uslessTags:
                                i = Indices.removeBetweenTag(wordAux, i, mystr)
                                break
                            
                    wordAux=''
                    
                    #Si se detecta que es un de los caracteres sin texto util entre ellos
                    # se llama a la funcion que elimina ese texto
                    if(auxC == '['):
                        i = Indices.removeBetweenChr(']', i, mystr)

                    if(auxC == '{'):
                        i = Indices.removeBetweenChr('}', i, mystr)
                    
                    if(auxC != '\n'):
                        newStr += ''+auxC
                    
                    i+=1
            else:
                newStr = mystr
                
            #Se eliminan los caracteres que no son utiles
            for ch in uslessChars:
                newStr = newStr.replace(ch, " ")
            newStr = Indices.removeRepiteChr(' ', newStr)
            newStr = Indices.removeRepiteChr('\n', newStr)

            logging.info('Informacion obtenida!\n')
        #Si ocurre algun error se guarda ''
        except Exception as e:
            logging.error(str(e))
            newStr = ''
        return [newStr, typeUrl]

    #Guardado en un archivo txt
    def saveTxt(textIn, nameF):
        pathFile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', nameF)
        
        #Si recibe un texto lo guarda directo
        if isinstance(textIn, str):
            with open(pathFile, "a", encoding="utf-8") as f:
                f.write(textIn)
                f.write('\n')

            f.close()

        #Si recibe un diccionario se convierte a un objeto json antes de guardarlo
        elif isinstance(textIn, dict):
            with open(pathFile, "w", encoding="utf-8") as f:
                f.write(json.dumps(textIn, ensure_ascii=False).replace('[','(').replace(']',')').replace('((','[(').replace('))',')]'))
            f.close()

            with open(pathFile.replace('.txt','_T.txt'), "w", encoding="utf-8") as f:
                f.write(json.dumps(textIn, ensure_ascii=False))
            f.close()

    #Eliminación de cierto caracter que se repite hasta un "numb" de veces
    def removeRepite(words, chrRmv, numb):
        chrTup = []
        chrFind = ''
        for _ in range(0, numb):
            chrFind+=chrRmv
            chrTup.append(chrFind)
        return [word for word in words if not(word in chrTup)]

    #Validacion de una cadena para determinar si contiene algun numero
    def containsNumber(value):
        if True in [char.isdigit() for char in value]:
            return True
        return False

    #Busqueda de palabras en un texto que obtiene el numero de veces que se repiten
    def readTxt(url, prevText, pathFile):
        #Se hace un filtrado previo para evitar caracteres que no sean palabras
        # tambien se eliminan los articulos (stopwords en ingles)
        text = prevText[0].lower()
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

        #Se busca si "i" palabra ya fue previamente guardada
        # si no, se almacena junto con su numero de repeticiones
        finaltp = []
        aux = ('**typeUrl**', prevText[1])
        finaltp.append(aux)
        for i in tps:
            manyWord = i.split(' ')
            if len(manyWord)>1:
                palabra = manyWord[0]
            else:
                palabra = i

            if len(palabra) > 2 or len(palabra)<24:
                if tp.count(palabra) > 1:
                    aux = (palabra, tp.count(palabra))
                    finaltp.append(aux)
                else:
                    aux = (palabra, tp.count(palabra))
                    finaltp.append(aux)
        return finaltp

    #return [newStr, typeUrl]
    def readTxtInv(urls, prevDict):
        #Se hace un filtrado previo para evitar caracteres que no sean palabras
        # tambien se eliminan los articulos (stopwords en ingles)
        invDic = {}
        for url in urls:
            try:
                prevText = Indices.getText(url)

                if len(text[0]) > 0:
                    text = prevText[0].lower()
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
                    for i in tps:
                        manyWord = i.split(' ')
                        if len(manyWord)>1:
                            palabra = manyWord[0]
                        else:
                            palabra = i
                        
                        if len(palabra) > 2 or len(palabra)<24:
                            if tp.count(palabra) > 1:
                                if palabra in invDic:
                                    invDic[''+palabra+''].append((url, prevText[1], tp.count(palabra)))
                                else:
                                    invDic[''+palabra+''] = [(url, prevText[1], tp.count(palabra))]
                            else:
                                if palabra in invDic:
                                    invDic[''+palabra+''].append((url, prevText[1], tp.count(palabra)))
                                else:
                                    invDic[''+palabra+''] = [(url, prevText[1], tp.count(palabra))]
                else:
                    logging.error(url+' generó NAN')
            except Exception as e:
                logging.error(str(e))
        return invDic
    
    #Obtencion de un diccionario desde un archivo de texto
    def getDict(pathFile):
        data = {}
        if exists(pathFile):
            with open(pathFile.replace('.txt','_T.txt'), encoding="utf8") as f:
                data = json.load(f)

            for key, value in data.items():
                items = []
                for item in value:
                    newIt = tuple(item)
                    items.append(newIt)

                data[key] = items
        return data

    def translateIndex(pathFile):
        try:
            translator = googletrans.Translator()

            with open(pathFile, encoding="utf8") as f:
                dummyDict = json.load(f)

            engDict = {}
            espDict = {}
            try:
                for key, value in dummyDict.items():
                    wordEng = []
                    try:
                        for words in value:
                            if words[0] != '**typeUrl**':
                                translated = translator.translate(words[0], dest='en')
                                wordEng.append([translated.text, words[1]])
                            else:
                                wordEng.append([words[0], words[1]])
                        engDict[key] = wordEng
                    except Exception as e:
                        logging.error(str(e))
                
                for key, value in dummyDict.items():
                    wordEng = []
                    try:
                        for words in value:
                            if words[0] != '**typeUrl**':
                                translated = translator.translate(words[0], dest='es')
                                wordEng.append([translated.text, words[1]])
                            else:
                                wordEng.append([words[0], words[1]])
                        espDict[key] = wordEng
                    except Exception as e:
                        logging.error(str(e))
            except Exception as e:
                logging.error(str(e))
            Indices.saveTxt(engDict, 'indice-Eng.txt')
            Indices.saveTxt(espDict, 'indice-Esp.txt')
        except Exception as e:
            logging.error(str(e))

    #Metodo principal que llama a los demás metodos que generan el diccionario
    def generateIdx(self):
        inicio = time.time()
        urls = pathFile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'urls.txt')
        pathFileDict = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'indice.txt')

        try:
            #Se obtiene el archivo de urls previamente generado
            urls = open(pathFile, encoding="utf8")
            urls = [word.strip() for word in urls.readlines()]
            i = 0

            #Se abre el archivo de diccionario de existir uno
            idx = {}
            prevDict = Indices.getDict(pathFileDict)
            for url in urls:
                #Se valida que la url no se encuentre en un diccioanrio previo
                if not(url in prevDict):
                    #Se obtiene el texto, sin codigo html, de una url
                    text = Indices.getText(url)
                    if len(text[0]) > 0:
                        #Se genera el diccionario con las palabras del texto de la url
                        indN = Indices.readTxt(url=url, prevText=text, pathFile=("text"+str(i)+".txt"))

                        #Se almacena en el diccionario global la url como llave y sus palabras como valor ("url": (palabra, #Repeticiones))
                        idx[''+url+''] = indN
                        i += 1
                    #else:
                    #    logging.error(url+' generó NAN')
            #Si se encontro un diccionario previo
            if len(idx) > 0:
                if len(prevDict)>0:
                    #Se combina el diccionario previo y el generado actualmente
                    newDict = idx.copy()
                    for key, value in prevDict.items():
                        newDict[key] = value
                    
                    #Se guardan ambos diccionarios combinados
                    Indices.saveTxt(newDict, 'indice.txt')
                else:
                    #Se guarda el diccionario generado
                    Indices.saveTxt(idx, 'indice.txt')
            pathFileDict = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'indice_T.txt')
            #Indices.translateIndex(pathFileDict)
        except Exception as e:
            logging.error("Error al obtener la informacion\nVerifique las urls de su archivo!")
            return jsonify(status='Error', exception=''+str(e))

        fin = time.time()
        res = [
                {
                    "status": 'Ok',
                    "message": 'Se generó el diccionario con exito!',
                    "time": "Diccionario generado en "+str(formatTi.execTime(inicio, fin))
                }
            ]
        return jsonify(res)

    def generateIdxInv(self):
        inicio = time.time()
        urls = pathFile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'urls.txt')
        pathFileDict = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'indiceInv.txt')

        try:
            #Se obtiene el archivo de urls previamente generado
            urls = open(pathFile, encoding="utf8")
            urls = [word.strip() for word in urls.readlines()]

            #Se abre el archivo de diccionario de existir uno
            prevDict = Indices.getDict(pathFileDict)
            indN = Indices.readTxtInv(urls, prevDict)

            Indices.saveTxt(indN, 'indiceInv.txt')
        except Exception as e:
            logging.error("Error al obtener la informacion\nVerifique las urls de su archivo!")
            return jsonify(status='Error', exception=''+str(e))

        fin = time.time()
        res = [
                {
                    "status": 'Ok',
                    "message": 'Se generó el diccionario con exito!',
                    "time": "Diccionario generado en "+str(formatTi.execTime(inicio, fin))
                }
            ]
        return jsonify(res)

    #Metodo que lee el diccionario y lo regresa como respuesta json
    def getIdx(self):
        pathFile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'indice.txt')

        try:
            if exists(pathFile):
                res = [
                    {
                        "status": 'Ok',
                        "message": 'Se obtuvo el diccionario con exito!',
                        "data": 'str(Indices.getDict(pathFile))'
                    }
                ]

                return jsonify(res)
            else:
                raise NotFoundErr('No se encontró el diccionario! Asegurese de haberlo creado antes')
        except Exception as e:
            logging.error("Error al obtener la informacion\nVerifique su archivo!")
            return jsonify(status='Error', exception=''+str(e))

    #Metodo que lee el diccionario y lo traduce
    def trasnlateIdx(self):
        inicio = time.time()
        pathFile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'indice_T.txt')

        try:
            if exists(pathFile):
                Indices.translateIndex(pathFile)
                
                fin = time.time()
                res = [
                    {
                        "status": 'Ok',
                        "message": 'Se obtuvo el diccionario con exito!',
                        "time": "Diccionario generado en "+str(formatTi.execTime(inicio, fin))
                    }
                ]

                return jsonify(res)
            else:
                raise NotFoundErr('No se encontró el diccionario! Asegurese de haberlo creado antes')
        except Exception as e:
            logging.error("Error al obtener la informacion\nVerifique su archivo!")
            return jsonify(status='Error', exception=''+str(e))