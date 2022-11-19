import urllib.request
import os
import logging
from flask import jsonify
import PyPDF2

def getText(url, nUrl):
    try:
        logging.info('Solicitando info....')

        fp = urllib.request.urlopen(url, timeout=25)
        mybytes = fp.read()
        headers = fp.getheaders()
        
        for head in headers:
            if head[0] == 'Content-Type':
                if head[1] == 'application/pdf':
                    file = open('tests' + str(nUrl) + ".pdf", 'wb')
                    file.write(mybytes)
                    file.close()

                    pdfFileObj = open('tests' + str(nUrl) + ".pdf", 'rb')
                    pdfReader = PyPDF2.PdfFileReader(pdfFileObj, strict=False)
                    
                    textSave = ''
                    for pag in range(0, pdfReader.numPages):
                        pageObj = pdfReader.getPage(pag)
                        textSave += pageObj.extractText().replace('\n', ' ').replace('-', ' ')
                    
                    file = open('tests' + str(nUrl) + ".txt", 'w', encoding="utf-8")
                    file.write(str(textSave))
                    file.close()
                else:
                    mystr = mybytes.decode("utf8")
        
        fp.close()
        # logging.info('Informacion de \"'+url+'\" obtenida, procesando...')
    except Exception as e:
        print(str(e))
            

"""
urls = pathFile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'urls.txt')
try:
    urls = open(pathFile, encoding="utf8")
    urls = [word.strip() for word in urls.readlines()]

    i = 0
    for url in urls:
        text = getText(url, i)
        i += 1


except Exception as e:
    print(str(e))
"""

txt = "http://www.youtube.com/results?search_query=curso+de+Spring+Boot"

print(txt.index('search_query'))
print(txt[txt.index('search_query')+13:].replace('+',' '))
