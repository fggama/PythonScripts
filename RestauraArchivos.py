import sys
import os
import zipfile
import getopt
from pathlib import Path
import subprocess, time

def progreso(total, archivo):
    espacios = 30 - len(archivo)
    if espacios < 0:
        espacios = 0
        archivo = archivo[:100]

    print(' %s  |%d' % (' '*5 + archivo + ' '*espacios, total))


def listaArchivosZip(dir_origen, recursivo):
    dirs = os.listdir( dir_origen )
    arch = []
    for dir in dirs:
        if os.path.isdir(os.path.join(dir_origen,dir)):
            if recursivo:
                x=listaArchivosZip(os.path.join(dir_origen,dir), True)
                arch.extend(x)
        else:
            if ('.zip' in dir):
                arch.append(os.path.join(dir_origen,dir))
    return arch

def printInstrucciones():
     print ('\tusar: RestauraArchivos.py -o <restaurar desde> -d <restaurar a> -x <extraer el directorio o archivo> -r')
     print ('\t\t-h\tAyuda')
     print ('\t\t-o\tDirectorio desde donde se restaura (origen)')
     print ('\t\t-r\t(opcional) Buscar en directorio origen en forma recursiva')
     print ('\t\t-d\tDirectorio destino')
     print ('\t\t-x\tNombre del directorio o archivo a etraer, * para TODO')
     print ('  ej:   RestauraArchivos.py -o "I:/Backup/Documents/Visual Studio 2015" -d I:/tmp -x "Documents/Visual Studio 2015/Projects/SAGA"')

def main(argv):

    origen = ''
    destino = ''
    extraer = ''
    recursivo = False
    try:
        opts, args = getopt.getopt(argv,"hro:d:x:")
    except getopt.GetoptError:
        printInstrucciones()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            printInstrucciones()
            sys.exit()
        elif opt in ("-o"):
            origen = arg
        elif opt in ("-d"):
            destino = arg
        elif opt in ("-x"):
            extraer = arg
        elif opt == '-r':
            recursivo = True
    
    if len(origen) == 0 or len(destino) == 0 or len(extraer) == 0:
        printInstrucciones()
        sys.exit(2)

    print("\nSe recuperaran todos los archivos y directorios con '" + extraer + "'")
    print(' '*5 +"desde : " + origen)
    print(' '*5 +"    a : " + destino)

    resp = input("\nDesea continuar? (s/n) ")
    if not (resp == 's' or resp == 'S' or len(resp) == 0):
        sys.exit(2)

    if not os.path.exists(os.path.join(origen)):
        print ('-o: error en origen: ' + origen)
        sys.exit(2)

    dir_origen = os.path.join(origen)
    dir_destino= os.path.join(destino)
    
    if extraer == '*':
        recursivo = True

    files = sorted(listaArchivosZip(dir_origen,recursivo))
    contArchivos = 0
    for file in files:
        contArchivos+=1
        cont = 0
        with zipfile.ZipFile(os.path.join(file)) as myzip:
            for archivo in myzip.filelist:
                if extraer == '*' or extraer in archivo.filename:
                    cont += 1
                    myzip.extract(archivo.filename, dir_destino)
        if cont > 0:
            progreso(cont, file)
      

    if contArchivos == 0:
        print ("No se encontro archivos ZIP en '" + dir_origen + "'")
    else:
        print ("Se proceso " + str(contArchivos) + " archivos")



if __name__ == "__main__":
   main(sys.argv[1:])
