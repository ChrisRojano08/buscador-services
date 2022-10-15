# buscador-services v0.3.1

## Proyecto buscador en python
En el siguiente repositorio contiene el código realizado para generar un buscador web.
Este proyecto utiliza un access.log, generado en squid proxy mediante Ubuntu 20.04, para generar una lista de urls.
Con la lista de urls se genera un diccionario con las palabras y su numero de repeticiones.
...


##Instalación
Para instalar este proyecto requiere de:
- Github
- Python 3

Primero clone el repositorio desde la rama "master".
Para instalar los paquetes necesarios para el proyecto solo ejecute el siguiente comando en la raiz del repositorio clonado:
pip install -r requeriments.txt
```

## Versiones
- [0.1] Creación del algoritmo que extrae texto desde una url
- [0.2] Creación del algortimo que genera una lista de urls a partir de un access.log de squid
- [0.3] Combinación de lo metodos anteriores para generar el diccionario con las urls y sus palabras repetidas
- [0.3.1] Documentación añadida

