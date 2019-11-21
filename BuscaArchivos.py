
import sys
import os
import zipfile
import getopt
from pathlib import Path
import subprocess, time
from msvcrt import getch

def isZip(variable): 
    if ('.zip' in variable): 
        return True
    else: 
        return False
  
def get_windows_terminal():
    from ctypes import windll, create_string_buffer
    h = windll.kernel32.GetStdHandle(-12)
    csbi = create_string_buffer(22)
    res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
 
    if not res: return 80, 25 
 
    import struct
    (bufx, bufy, curx, cury, wattr, left, top, right, bottom, maxx, maxy)\
    = struct.unpack("hhhhHhhhhhh", csbi.raw)
    width = right - left + 1
    height = bottom - top + 1
 
    return width, height

def printInstrucciones():
     print ('\tusar: BuscaArchivos.py -o <buscar en> -b <direcorio o archivo> -s')
     print ('\t\t-h\tAyuda')
     print ('\t\t-o\tDirectorio donde se inicia la busqueda')
     print ('\t\t-b\tArchivo o directorio a buscar')
     print ('\t\t-s\t(Opcional) Desplegar sin paginacion')
     print ('  ej:   BuscaArchivos.py -o "I:/Backup/Documents/Visual Studio 2015" -b "/Projects/SAGA"')

def main(argv):

    columnas, filas = get_windows_terminal()
    origen = ''
    buscar = ''
    paginar = True
    try:
        opts, args = getopt.getopt(argv,"hso:b:")
    except getopt.GetoptError:
        printInstrucciones()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            printInstrucciones()
            sys.exit()
        elif opt in ("-o"):
            origen = arg
        elif opt in ("-b"):
            buscar = arg
        elif opt in ("-s"):
            paginar = False
            

    print("")
    print(' '*5 +"origen : " + origen)
    print(' '*5 +"buscar : " + buscar)

    if len(origen) == 0 or len(buscar) == 0:
        printInstrucciones()
        sys.exit(2)

    if not os.path.exists(os.path.join(origen)):
        print ('-o: error en origen: ' + origen)
        sys.exit(2)

    z = 0
    numArchivos = 0
    numZip = 0

    for (root,dirs,files) in os.walk(os.path.join(origen)):
        for dir in dirs:
            archBuscar = sorted(os.listdir( os.path.join(root,dir) ))
            zipArchivos = filter(isZip,archBuscar)
            for zipArchivo in zipArchivos:
                cont = 0
                numZip += 1
                with zipfile.ZipFile(os.path.join(os.path.join(root,dir),zipArchivo)) as esteZip:
                    for archivo in esteZip.filelist:
                        if buscar in archivo.filename:
                            numArchivos += 1
                            cont += 1
                            if paginar and cont == filas - 1:
                                cont = 1
                                print("presione una tecla para continuar, ESC para salir, C continuar sin paginacion...")
                                z = ord(getch())
                                if z == 67 or z == 99:
                                    paginar = False
                                if z == 27:
                                    break
                            print(archivo.filename)
                if z == 27:
                    break
    print("\nArchivos ZIP: " + str(numZip))
    print("Encontrados: " + str(numArchivos))

if __name__ == "__main__":
   main(sys.argv[1:])
