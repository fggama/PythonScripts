import getopt
import sys
import os
import hashlib
import _pickle as cPickle
import zipfile
from datetime import datetime
from pathlib import Path
import subprocess, time

timestampStr = datetime.now().strftime("%Y-%m-%d_%H-%M")
archivoActual = ""
versionZIP = 1

def ejecuta(dir_path, origen, destino):
    """Ejecuta la copia: origen -> destino"""
    dict={}
    dir_origen = Path(origen)
    dir_destino = os.path.join(Path(dir_path), Path(destino))
    print(origen + '->' + dir_destino)
    zipZero = True
    os.chdir(dir_origen)

    try:
        chksm = os.path.join(dir_destino,"chksm.txt")
        if os.path.getsize(chksm) > 0:
            setArchivoActual(chksm)
            checksum = open(chksm,'rb')
            dict = cPickle.load(checksum)
            checksum.close()
    except IOError:
        num = sum([len(files) for r, d, files in os.walk(dir_origen)])
        cont = 0
        setArchivoActual(os.path.join(dir_destino,"chksm.txt"))
        checksum=open(os.path.join(dir_destino,"chksm.txt"),'wb')
        setArchivoActual(os.path.join(dir_destino,"ignore.txt"))
        ignore=open(os.path.join(dir_destino,"ignore.txt"),'w')

        for (root,dirs,files) in os.walk(dir_origen):
            if not os.path.exists(os.path.join(root,".caignore")):
                for archivo in files:
                    cont += 1
                    progreso(num,cont,os.path.join(root,archivo))
                    setArchivoActual(os.path.join(root,archivo))
                    f_temp = open(os.path.join(root,archivo),'rb')
                    content=f_temp.read()
                    m = hashlib.md5()
                    m.update(content)
                    dict[os.path.join(root,archivo)] = m.hexdigest()
                    f_temp.close()
            else:
                ignore.write(root)
                ignore.write('\n')

        if cont < num:
            progreso(num,num,'')

        cPickle.dump(dict,checksum)
        checksum.close()
        ignore.close()
        delta = zipfile.ZipFile(os.path.join(dir_destino,"delta.zip"),'w')
  
        # Escribe archivo ZIP
        cont = 0
        for (root,dirs,files) in os.walk(dir_origen):
            for archivo in files:
                cont += 1
                progreso(num,cont,os.path.join(root,archivo))
                zipZero = False
                setArchivoActual("delta:" + os.path.join(dir_destino,"delta.zip"))
                delta.write(os.path.join(root,archivo), os.path.join(setDir(root,dir_origen),archivo))
        delta.close()
  
        # Registro de archivos borrados
        setArchivoActual(os.path.join(dir_destino,"remove.txt"))
        remove = open(os.path.join(dir_destino,"remove.txt"),'w')
        for k, v in list(dict.items()):
            if(not os.path.exists(k)):
                remove.write(k)
                remove.write('\n')
                del dict[k]
        remove.close()

        if zipZero:
            os.remove(os.path.join(dir_destino,"delta.zip"))
        else:
            renombraArchivo(dir_destino,timestampStr)
        return

    # Registro de archivos borrados
    setArchivoActual(os.path.join(dir_destino,"remove.txt"))
    remove = open(os.path.join(dir_destino,"remove.txt"),'w')
    for k, v in list(dict.items()):
        if(not os.path.exists(k)):
            remove.write(k)
            remove.write('\n')
            del dict[k]
    remove.close()

    # Escribe archivo ZIP
    # Registro de archivos ignorados
    setArchivoActual(os.path.join(dir_destino,"ignore.txt"))
    ignore = open(os.path.join(dir_destino,"ignore.txt"),'w')
    delta = zipfile.ZipFile(os.path.join(dir_destino,"delta.zip"),'w')
    num = sum([len(files) for r, d, files in os.walk(dir_origen)])
    cont = 0
    for (root,dirs,files) in os.walk(dir_origen):
        if not os.path.exists(os.path.join(root,".caignore")):
            for archivo in files:
                cont += 1
                progreso(num,cont,os.path.join(root,archivo))
                setArchivoActual(os.path.join(root,archivo))
                f_temp = open(os.path.join(root,archivo),'rb')
                content = f_temp.read()
                m = hashlib.md5()
                m.update(content)
                f_temp.close()
                try:
                    if(dict[os.path.join(root,archivo)] != m.hexdigest()):
                        zipZero = False
                        setArchivoActual("delta:" + os.path.join(dir_destino,"delta.zip"))
                        delta.write(os.path.join(root,archivo), os.path.join(setDir(root,dir_origen),archivo))
                        dict[os.path.join(root,archivo)] = m.hexdigest()
                except KeyError:
                    zipZero = False
                    setArchivoActual("delta:" + os.path.join(dir_destino,"delta.zip"))
                    delta.write(os.path.join(root,archivo), os.path.join(setDir(root,dir_origen),archivo))
                    dict[os.path.join(root,archivo)] = m.hexdigest()
        else:
            ignore.write(root)
            ignore.write('\n')
    
    if cont < num:
        progreso(num,num,'')
    delta.close()
    ignore.close()

    setArchivoActual(os.path.join(dir_destino,"chksm.txt"))
    f=open(os.path.join(dir_destino,"chksm.txt"),'wb')
    cPickle.dump(dict,f)
    f.close()
    if zipZero:
        os.remove(os.path.join(dir_destino,"delta.zip"))
    else:
        renombraArchivo(dir_destino,timestampStr)

def setDir(root, dir_origen):
    if versionZIP == 1:
        return root.replace(str(dir_origen),"")
    else:
        return root

def renombraArchivo(dir_destino, timestampStr):
    """Renombra el archivo delta.zip al archivo de la fecha"""
    if os.path.exists(os.path.join(dir_destino,"delta.zip")):
        os.rename(os.path.join(dir_destino,"delta.zip"),os.path.join(dir_destino,timestampStr + ".zip"))


def directorioDestino(path):
    """Verifica la existencia y crea los directorios destino"""
    if not os.path.exists(path):
        try:
            os.makedirs(path)
            print("+ directorio " + path)
        except:
            print("")
            print(path + "--> Error destino: ", sys.exc_info())

def progreso(total, i, archivo):
    """Despliega el progreso de la ejecució"""
    incre = int(50.0 / total * i)
    espacios = 100 - len(archivo)
    if espacios < 0:
        espacios = 0
        archivo = archivo[:100]

    if i < total:
        sys.stdout.write('\r' + '| %d%%  |%s' % (2*incre,' '*5 + archivo + ' '*espacios))
    else:
        sys.stdout.write('\r' + '|%d%%  |%s' % (100,' '*5 + 'Finalizado' + ' '*90))
        sys.stdout.write('\n')
        print(total)
    sys.stdout.flush()

def setArchivoActual(nombre):
    """Registra el nombre del archivo en proceso"""
    global archivoActual
    archivoActual = nombre

def main(argv):
    archiDetalle = ""
    global versionZIP
    versionZIP = 0

    try:
        print (argv)
        opts, args = getopt.getopt(argv,"h2d:")
    except getopt.GetoptError:
        print ('Error:')
        print ('  usar: CopiaArchivos.py -d <archivo de detalle> -2 -h')
        print ('  ej:   CopiaArchivos.py -d detalle.txt')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('  usar: CopiaArchivos.py -d <archivo de detalle> -2 -h')
            print ('  ej:   CopiaArchivos.py -d detalle.txt' -2)
            sys.exit()
        elif opt in ("-d"):
            archiDetalle = arg
        elif opt in ("-2"):
            versionZIP = 1

    if len(archiDetalle) == 0:
        print ('Error:')
        print ('  usar: CopiaArchivos.py -d <archivo de detalle> -2 -h')
        print ('  ej:   CopiaArchivos.py -d detalle.txt')
        sys.exit(2)
        
    origen = ""
    destino = ""
    try:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        if not os.path.exists(os.path.join(dir_path,archiDetalle)):
            raise Exception('No se encuentra el archivo ' + archiDetalle)
    
        setArchivoActual(os.path.join(dir_path,archiDetalle))
        f_temp=open(os.path.join(dir_path,archiDetalle),'r')
        detalle = f_temp.readlines()
        for linea in detalle:
            if len(linea) == 0 or linea.startswith("#"):
                continue
        
            dirs = linea.replace('/','\\').rstrip().split(",")
            destino = os.path.join(Path(dir_path), Path(dirs[1]))
            origen = dirs[0]
            directorioDestino(os.path.join(Path(dir_path), Path(dirs[1])))

            if not os.path.isdir(dirs[0]):
                print("No existe el directorio origen: " + dirs[0])
            else:
                ejecuta(dir_path, dirs[0], dirs[1])

        f_temp.close()
        print("Finalizado")
    except:
        print("")
        print("Detalle del proceso ")
        print("   origen: " + origen)
        print("  destino: " + destino)
        print("  archivo: " + archivoActual)
        print("Info:", sys.exc_info())


if __name__ == "__main__":
    main(sys.argv[1:])

