import urllib.request
import os
import logging
from flask import jsonify
import PyPDF2

def getText(url):
    try:
        logging.info('Solicitando info....')

        fp = urllib.request.urlopen(url, timeout=25)
        mybytes = fp.read()
        headers = fp.getheaders()
        
        pdfN = 0
        for head in headers:
            if head[0] == 'Content-Type':
                if head[1] == 'application/pdf':
                    file = open('tests' + ".pdf", 'wb')
                    file.write(mybytes)
                    file.close()

                    pdfFileObj = open('tests' + ".pdf", 'rb')
                    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
                    print('Paginas: '+str(pdfReader.numPages)) 
                        
                    pageObj = pdfReader.getPage(0)
                        
                    print('Texto: '+(pageObj.extractText()))

                    print('\n')
                else:
                    mystr = mybytes.decode("utf8")
                    print(mystr)
        
        fp.close()
        logging.info('Informacion de \"'+url+'\" obtenida, procesando...')
    except Exception as e:
        print('Error')
        print(str(e))
            


urls = pathFile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'urls.txt')
try:
    urls = open(pathFile, encoding="utf8")
    urls = [word.strip() for word in urls.readlines()]

    for url in urls:
        text = getText(url)


except Exception as e:
    print(str(e))
