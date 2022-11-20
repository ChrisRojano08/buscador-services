from urltitle import URLTitleReader
import urllib.request
import os
import logging
from flask import jsonify
import PyPDF2
from os.path import exists
import json
from bs4 import BeautifulSoup


def generateTitle(url):
    try:
        fp = urllib.request.urlopen(url, timeout=20)
        mybytes = fp.read()

        try:
            mystr = mybytes.decode("utf8")
            processExt = 'html'
        except:
            try:
                mystr = mybytes.decode("latin-1")
                processExt = 'html'
            except:
                try:
                    mystr = mybytes.decode("ascii")
                    processExt = 'html'
                except:
                    try:
                        soup = BeautifulSoup(mybytes, features="html.parser")

                        for script in soup(["script", "style"]):
                            script.extract()

                        text = soup.get_text()

                        lines = (line.strip() for line in text.splitlines())
                        chunks = (phrase.strip()
                                for line in lines for phrase in line.split("  "))
                        mystr = '\n'.join(chunk for chunk in chunks if chunk)
                        processExt = 'text'

                    except Exception as e:
                        logging.error(str(e))

        if processExt == 'html':
            if '<title>' in mystr and '</title>' in mystr:
                title = str(mystr).split('<title>')[
                            1].split('</title>')[0]
            else:
                try:
                    reader = URLTitleReader(verify_ssl=True)
                    title = reader.title(url)
                except:
                    title = url
        else:
            try:
                reader = URLTitleReader(verify_ssl=True)
                title = reader.title(url)
            except:
                title = url

        if '\n' in title or 'text/html' in title or title == '' or title == ' ':
            if 'youtube.com' in url:
                uu = url.split('/')
                title = 'Youtube - '+uu[len(uu)-1].capitalize()
            else:
                title = url
    except:
        title = url

    return title


def getInvDict(pathFile):
    data = {}
    urls = []
    if exists(pathFile):
        with open(pathFile.replace('.txt', '_T.txt'), encoding="utf8") as f:
            data = json.load(f)

        for key, value in data.items():
            items = []
            for item in value:
                if not(item[0] in urls):
                    urls.append(item[0])

                items.append(item)

            data[key] = items
    return [data, urls]


def saveTxt(textIn, nameF):
    pathFile = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'src', nameF)

    # Si recibe un texto lo guarda directo
    if isinstance(textIn, str):
        with open(pathFile, "a", encoding="utf-8") as f:
            f.write(textIn)
            f.write('\n')

        f.close()

    # Si recibe un diccionario se convierte a un objeto json antes de guardarlo
    elif isinstance(textIn, dict):
        with open(pathFile, "w", encoding="utf-8") as f:
            f.write(json.dumps(textIn, ensure_ascii=False).replace(
                '[', '(').replace(']', ')').replace('((', '[(').replace('))', ')]'))
        f.close()

        with open(pathFile.replace('.txt', '_T.txt'), "w", encoding="utf-8") as f:
            f.write(json.dumps(textIn, ensure_ascii=False))
        f.close()



pathFileDict = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'indiceInv.txt')
dictI = {}
dictI = getInvDict(pathFileDict)[0]

for key, value in dictI.items():
    for item in value:
        if 'text/html' in item[3]:
            item[3] = generateTitle(item[0])

saveTxt(dictI, 'indiceInv.txt')
