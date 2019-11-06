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
        archivo = archivo[:30]

    print(' %s  |%d' % (' '*5 + archivo + ' '*espacios, total))


def isZip(variable): 
    if ('.zip' in variable): 
        return True
    else: 
        return False
  

def main(argv):

    origen = ''
    destino = ''
    extraer = ''
    try:
        opts, args = getopt.getopt(argv,"ho:d:x:",["ofile=","dfile=","xfile="])
    except getopt.GetoptError:
        print ('  usar: restauraArchivo.py -o <restaurar desde> -d <restaurar a> -x <extraer el direcorio o archivo>')
        print ('  ej:   restauraArchivo.py -o "I:/Backup/Documents/Visual Studio 2015" -d I:/tmp -x "Documents/Visual Studio 2015/Projects/SAGA"')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('  usar: restauraArchivo.py -o <restaurar desde> -d <restaurar a> -x <extraer el direcorio o archivo>')
            print ('  ej:   restauraArchivo.py -o "I:/Backup/Documents/Visual Studio 2015" -d I:/tmp -x "Documents/Visual Studio 2015/Projects/SAGA"')
            sys.exit()
        elif opt in ("-o", "--ofile"):
            origen = arg
        elif opt in ("-d", "--dfile"):
            destino = arg
        elif opt in ("-x", "--xfile"):
            extraer = arg
    
    print("")
    print(' '*5 +"origen : " + origen)
    print(' '*5 +"destino: " + destino)
    print(' '*5 +"extraer: " + extraer)

    if len(origen) == 0 or len(destino) == 0 or len(extraer) == 0:
        print ('  usar: restauraArchivo.py -o <restaurar desde> -d <restaurar a> -x <extraer el direcorio o archivo>')
        print ('  ej:   restauraArchivo.py -o "I:/Backup/Documents/Visual Studio 2015" -d I:/tmp -x "Documents/Visual Studio 2015/Projects/SAGA"')
        print("Debe ingresar toda la informacion.")
        sys.exit(2)

    if not os.path.exists(os.path.join(origen)):
        print ('-o: error en origen: ' + origen)
        sys.exit(2)

    print("")

    resp = input("Desea continuar? (s/n) ")
    if not (resp == 's' or resp == 'S' or len(resp) == 0):
        sys.exit(2)

    dir_origen = os.path.join(origen)
    dir_destino= os.path.join(destino)

    dirs = sorted(os.listdir( dir_origen ))
    files = filter(isZip, dirs)

    for file in files:
        cont = 0
        with zipfile.ZipFile(os.path.join(dir_origen,file)) as myzip:
            for archivo in myzip.filelist:
                if extraer in archivo.filename:
                    cont += 1
                    myzip.extract(archivo.filename, dir_destino)
        progreso(cont, file)




if __name__ == "__main__":
   main(sys.argv[1:])
